# -*- coding: UTF-8
#
# submission
# **********
#
# Implements a GlobaLeaks submission, then the operations performed
#   by an HTTP client in /submission URI

import copy
from globaleaks.third_party.rstr import rstr

from twisted.internet.defer import inlineCallbacks
from globaleaks.settings import transact, GLSetting
from globaleaks.models import Context, InternalTip, Receiver, WhistleblowerTip, \
    Node, InternalFile
from globaleaks import security
from globaleaks.handlers.base import BaseHandler
from globaleaks.handlers.admin import db_get_context_steps
from globaleaks.handlers.authentication import transport_security_check, unauthenticated
from globaleaks.utils.token import Token, TokenList
from globaleaks.rest import requests
from globaleaks.utils.utility import log, utc_future_date, datetime_now, datetime_to_ISO8601
from globaleaks.rest import errors
from globaleaks.anomaly import Alarm


def wb_serialize_internaltip(internaltip):
    response = {
        'id': internaltip.id,
        'context_id': internaltip.context_id,
        'creation_date': datetime_to_ISO8601(internaltip.creation_date),
        'expiration_date': datetime_to_ISO8601(internaltip.expiration_date),
        'wb_steps': internaltip.wb_steps,
        'files': [f.id for f in internaltip.internalfiles],
        'receivers': [r.id for r in internaltip.receivers],
        'wb_e2e_public': internaltip.wb_e2e_public,
    }

    return response


def db_create_whistleblower_tip(store, wb_signature, internaltip_id):
    wbtip = WhistleblowerTip()
    wbtip.access_counter = 0
    wbtip.wb_signature = wb_signature
    wbtip.internaltip_id = internaltip_id
    store.add(wbtip)

def hybrid_get_receipt_hash(store):
    """
    """
    node = store.find(Node).one()
    return_value_receipt = unicode( rstr.xeger(node.receipt_regexp) )
    receipt_hash = security.hash_password(return_value_receipt, node.receipt_salt)
    return receipt_hash, return_value_receipt


@transact
def create_whistleblower_tip(*args):
    return db_create_whistleblower_tip(*args)


def import_receivers(store, submission, receiver_id_list):
    context = submission.context

    receiver_id_list = set(receiver_id_list)

    if not len(receiver_id_list):
        log.err("Receivers required to be selected, not empty")
        raise errors.SubmissionFailFields("Needed almost one Receiver selected")

    if context.maximum_selectable_receivers and \
                    len(receiver_id_list) > context.maximum_selectable_receivers:
        raise errors.InvalidInputFormat("Provided an invalid number of Receivers")

    for receiver_id in receiver_id_list:
        try:
            receiver = store.find(Receiver, Receiver.id == unicode(receiver_id)).one()
        except Exception as excep:
            log.err("Receiver requested (%s) can't be found: %s" %
                    (receiver_id, excep))
            raise errors.ReceiverIdNotFound

        if context not in receiver.contexts:
            raise errors.InvalidInputFormat("Forged receiver selection, you fuzzer! <:")

        try:
            if not GLSetting.memory_copy.allow_unencrypted and \
                            receiver.pgp_key_status != u'enabled':
                log.err("Encrypted only submissions are supported. Cannot select [%s]" % receiver_id)
                continue
            submission.receivers.add(receiver)
        except Exception as excep:
            log.err("Receiver %s can't be assigned to the tip [%s]" % (receiver_id, excep))
            continue

        log.debug("+receiver [%s] In tip (%s) #%d" % \
                  (receiver.name, submission.id, submission.receivers.count() ))

    if submission.receivers.count() == 0:
        log.err("Receivers required to be selected, not empty")
        raise errors.SubmissionFailFields("Needed at least one Receiver selected [2]")


def verify_fields_recursively(fields, wb_fields):
    for f in fields:
        if f not in wb_fields:
            raise errors.SubmissionFailFields("missing field (no structure present): %s" % f)

        if fields[f]['required'] and ('value' not in wb_fields[f] or
                                              wb_fields[f]['value'] == ''):
            raise errors.SubmissionFailFields("missing required field (no value provided): %s" % f)

        if isinstance(wb_fields[f]['value'], unicode):
            if len(wb_fields[f]['value']) > GLSetting.memory_copy.maximum_textsize:
                raise errors.InvalidInputFormat("field value overcomes size limitation")

        indexed_fields = {}
        for f_c in fields[f]['children']:
            indexed_fields[f_c['id']] = copy.deepcopy(f_c)

        indexed_wb_fields = {}
        for f_c in wb_fields[f]['children']:
            indexed_wb_fields[f_c['id']] = copy.deepcopy(f_c)

        verify_fields_recursively(indexed_fields, indexed_wb_fields)

    for wbf in wb_fields:
        if wbf not in fields:
            raise errors.SubmissionFailFields("provided unexpected field %s" % wbf)


def verify_steps(steps, wb_steps):
    indexed_fields = {}
    for step in steps:
        for f in step['children']:
            indexed_fields[f['id']] = copy.deepcopy(f)

    indexed_wb_fields = {}
    for step in wb_steps:
        for f in step['children']:
            indexed_wb_fields[f['id']] = copy.deepcopy(f)

    return verify_fields_recursively(indexed_fields, indexed_wb_fields)


def db_create_submission(store, token, request, language):
    context = store.find(Context, Context.id == token.context_associated).one()
    if not context:
        # this can happen only if the context is removed
        # between submission POST and PUT.. :) that's why is better just
        # ignore this check, take che cached and wait the reference below fault
        log.err("Context requested: [%s] not found!" % token.context_associated)
        raise errors.ContextIdNotFound

    submission = InternalTip()

    submission.expiration_date = utc_future_date(seconds=context.tip_timetolive)
    submission.context_id = context.id
    submission.creation_date = datetime_now()

    # the fingerprint / signature is associated to WhistleboerTip 
    submission.wb_e2e_public = request['wb_e2e_public']

    # This value is the copy of the node level setting, that can change in the time.
    submission.is_e2e_encrypted = GLSetting.memory_copy.submission_data_e2e

    if GLSetting.memory_copy.submission_data_e2e:
        log.debug("End2End enabled node level, wb_steps len #%d (has to be 1) first 20bytes: %s" %(
            len(request['wb_steps']),
            request['wb_steps'][0][:20]))
    else:
        log.debug("End2End DIS-abled node level, wb_steps len #%d" % (len(request['wb_steps'])))

    try:
        store.add(submission)
    except Exception as excep:
        log.err("Storm/SQL Error: %s (create_submission)" % excep)
        raise errors.InternalServerError("Unable to commit on DB")

    try:
        for filedesc in token.uploaded_files:
            associated_f = InternalFile()
            associated_f.name = filedesc['filename']
            # aio, when we are going to implement file.description ?
            associated_f.description = ""
            associated_f.content_type = filedesc['content_type']
            associated_f.size = filedesc['body_len']
            associated_f.internaltip_id = submission.id
            associated_f.file_path = filedesc['encrypted_path']
            store.add(associated_f)

            log.debug("=> file associated %s|%s (%d bytes)" % (
                associated_f.name, associated_f.content_type, associated_f.size))

    except Exception as excep:
        log.err("Unable to create a DB entry for file! %s" % excep)
        raise excep

    try:
        wb_steps = request['wb_steps']
        steps = db_get_context_steps(store, context.id, language)
        submission.wb_steps = wb_steps
    except Exception as excep:
        log.err("Submission create: fields validation fail: %s" % excep)
        raise excep

    try:
        import_receivers(store, submission, request['receivers'])
    except Exception as excep:
        log.err("Submission create: receivers import fail: %s" % excep)
        raise excep

    submission_dict = wb_serialize_internaltip(submission)
    return submission_dict


@transact
def create_submission(store, token, request, language):
    return db_create_submission(store, token, request, language)


class SubmissionCreate(BaseHandler):
    """
    This class Request a token to create a submission.
    We keep the naming with "Create" suffix for internal globaleaks convention,
    but this handler do not interact with Database, InternalTip, Submissions, etc.
    """

    @transport_security_check('wb')
    @unauthenticated
    def post(self):
        """
        Request: SubmissionDesc
        Response: SubmissionDesc
        Errors: ContextIdNotFound, InvalidInputFormat, SubmissionFailFields

        This creates an empty submission for the requested context,
        and returns submissionStatus with empty fields and a Submission Unique String,
        This is the unique token used during the submission procedure.
        header session_id is used as authentication secret for the next interaction.
        expire after the time set by Admin (Context dependent setting)

        --- has to became:
        Request: empty
        Response: SubmissionDesc + Token
        Errors: None

        This create a Token, require to complete the submission later
        """
        request = self.validate_message(self.request.body, requests.SubmissionDesc)

        token = Token('submission', request['context_id'])
        token.set_difficulty(Alarm().get_token_difficulty())
        token_answer = token.serialize_token()

        token_answer.update({'id': token_answer['token_id']})
        token_answer.update({'context_id': request['context_id']})
        token_answer.update({'human_captcha_answer': 0})

        self.set_status(201)  # Created
        self.finish(token_answer)


class SubmissionInstance(BaseHandler):
    """
    This is the interface for create, populate and complete a submission.
    Relay in the client-server update and exchange of the submissionStatus message.
    """

    @transport_security_check('wb')
    @unauthenticated
    @inlineCallbacks
    def put(self, token_id):
        """
        Parameter: token_id
        Request: SubmissionDesc
        Response: SubmissionDesc

        PUT finalize the submission
        """

        @transact
        def put_transact(store, token, request):
            status = db_create_submission(store, token, request, self.request.language)

            if len(request['wb_signature']):
                log.debug("End2End encryption submission: handshake fingerprint (TODO sign)")
            else:
                log.debug("End2End disabled: receipt is going to be generated")
                hash, display = hybrid_get_receipt_hash(store)
                print "DEBUG **", hash, display
                status['receipt'] = display
                request['wb_signature'] = hash

            db_create_whistleblower_tip(store, request['wb_signature'], status['id'])
            return status

        request = self.validate_message(self.request.body, requests.SubmissionDesc)

        # the .get method raise an exception if the token is invalid
        token = TokenList.get(token_id)

        if not token.context_associated == request['context_id']:
            raise errors.InvalidInputFormat("Token context unaligned with REST url")

        token.validate(request)

        status = yield put_transact(token, request)

        TokenList.delete(token_id)

        self.set_status(202)  # Updated, also if submission if effectively created (201)
        self.finish(status)
