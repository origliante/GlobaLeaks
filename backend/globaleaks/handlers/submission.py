# -*- coding: UTF-8
#
#   submission
#   **********
#
#   Implements a GlobaLeaks submission, then the operations performed
#   by an HTTP client in /submission URI

import copy

from twisted.internet.defer import inlineCallbacks

from globaleaks.settings import transact, transact_ro, GLSetting
from globaleaks.models import Context, InternalTip, Receiver, ReceiverInternalTip, \
    WhistleblowerTip, Node, InternalFile
from globaleaks import security
from globaleaks.handlers.base import BaseHandler
from globaleaks.handlers.admin import db_get_context_steps
from globaleaks.handlers.authentication import transport_security_check, unauthenticated
from globaleaks.rest import requests
from globaleaks.utils.utility import log, utc_future_date, datetime_now, datetime_to_ISO8601
from globaleaks.third_party import rstr
from globaleaks.rest import errors

def wb_serialize_internaltip(internaltip):

    response = {
        'id' : internaltip.id,
        'context_id': internaltip.context_id,
        'creation_date' : datetime_to_ISO8601(internaltip.creation_date),
        'expiration_date' : datetime_to_ISO8601(internaltip.expiration_date),
        'wb_steps' : internaltip.wb_steps,
        'download_limit' : internaltip.download_limit,
        'access_limit' : internaltip.access_limit,
        'mark' : internaltip.mark,
        'files' : [f.id for f in internaltip.internalfiles],
        'receivers' : [r.id for r in internaltip.receivers],
        'pgp_glkey_pub': internaltip.pgp_glkey_pub,
        'pgp_glkey_priv': internaltip.pgp_glkey_priv
    }

    return response

def db_create_whistleblower_tip(store, submission_desc):
    """
    The plaintext receipt is returned only now, and then is
    stored hashed in the WBtip table
    """
    wbtip = WhistleblowerTip()

    node = store.find(Node).one()

    return_value_receipt = unicode( rstr.xeger(node.receipt_regexp) )
    wbtip.receipt_hash = security.hash_password(return_value_receipt, node.receipt_salt)

    wbtip.access_counter = 0
    wbtip.internaltip_id = submission_desc['id']
    store.add(wbtip)

    return return_value_receipt

@transact
def create_whistleblower_tip(*args):
    return db_create_whistleblower_tip(*args)

def import_receivers(store, submission, receiver_id_list, required=False):
    context = submission.context

    # Clean the previous list of selected Receiver
    for prevrec in submission.receivers:
        try:
            submission.receivers.remove(prevrec)
        except Exception as excep:
            log.err("Unable to remove receiver from Tip, before new reassignment")
            raise excep

    # and now clean the received list and import the new Receiver set.
    receiver_id_list = set(receiver_id_list)

    if required and (not len(receiver_id_list)):
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
                    receiver.gpg_key_status != u'enabled':
                log.err("Encrypted only submissions are supported. Cannot select [%s]" % receiver_id)
                continue
            submission.receivers.add(receiver)
        except Exception as excep:
            log.err("Receiver %s can't be assigned to the tip [%s]" % (receiver_id, excep) )
            continue

        log.debug("+receiver [%s] In tip (%s) #%d" %\
                (receiver.name, submission.id, submission.receivers.count() ) )
   
    if required and submission.receivers.count() == 0:
        log.err("Receivers required to be selected, not empty")
        raise errors.SubmissionFailFields("Needed at least one Receiver selected [2]")

# Remind: it's a store without @transaction because called by a @ŧransact
def import_files(store, submission, files):
    """
    @param submission: the Storm obj
    @param files: the list of InternalFiles UUIDs
    @return:
        Look if all the files specified in the list exist,
        Look if the context *require* almost a file, raise
            an error if missed
    """
    for file_id in files:
        try:
            ifile = store.find(InternalFile, InternalFile.id == unicode(file_id)).one()
        except Exception as excep:
            log.err("Storm error, not found %s file in import_files (%s)" %
                    (file_id, excep))
            raise errors.FileIdNotFound

        ifile.internaltip_id = submission.id

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

        indexed_fields  = {}
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
    indexed_fields  = {}
    for step in steps:
        for f in step['children']:
            indexed_fields[f['id']] = copy.deepcopy(f)

    indexed_wb_fields = {}
    for step in wb_steps:
        for f in step['children']:
            indexed_wb_fields[f['id']] = copy.deepcopy(f)

    return verify_fields_recursively(indexed_fields, indexed_wb_fields)

def db_create_submission(store, request, finalize, language):
    context = store.find(Context, Context.id == unicode(request['context_id'])).one()
    if not context:
        log.err("Context requested: [%s] not found!" % request['context_id'])
        raise errors.ContextIdNotFound

    submission = InternalTip()

    submission.access_limit = context.tip_max_access
    submission.download_limit = context.file_max_download
    submission.expiration_date = utc_future_date(seconds=context.tip_timetolive)
    submission.context_id = context.id
    submission.creation_date = datetime_now()

    if finalize:
        submission.mark = u'finalize'  # Finalized
    else:
        submission.mark = u'submission' # Submission

    try:
        store.add(submission)
    except Exception as excep:
        log.err("Storm/SQL Error: %s (create_submission)" % excep)
        raise errors.InternalServerError("Unable to commit on DB")

    try:
        import_files(store, submission, request['files'])
    except Exception as excep:
        log.err("Submission create: files import fail: %s" % excep)
        raise excep

    try:
        wb_steps = request['wb_steps']

        #TODO: e2e - move verify_steps in the receiver frontend js code 
        if finalize:
            steps = db_get_context_steps(store, context.id, language)
            #verify_steps(steps, wb_steps)

        submission.wb_steps = wb_steps
    except Exception as excep:
        log.err("Submission create: fields validation fail: %s" % excep)
        raise excep

    try:
        import_receivers(store, submission, request['receivers'], required=finalize)
    except Exception as excep:
        log.err("Submission create: receivers import fail: %s" % excep)
        raise excep

    submission_dict = wb_serialize_internaltip(submission)
    return submission_dict

@transact
def create_submission(*args):
    return db_create_submission(*args)

def db_update_submission(store, submission_id, request, finalize, language):
    context = store.find(Context, Context.id == unicode(request['context_id'])).one()
    if not context:
        log.err("Context requested: [%s] not found!" % request['context_id'])
        raise errors.ContextIdNotFound

    submission = store.find(InternalTip, InternalTip.id == unicode(submission_id)).one()
    if not submission:
        log.err("Invalid Submission requested %s in PUT" % submission_id)
        raise errors.SubmissionIdNotFound

    # this may happen if a submission try to update a context
    if submission.context_id != context.id:
        log.err("Can't be changed context in a submission update")
        raise errors.ContextIdNotFound()

    if submission.mark != u'submission':
        log.err("Submission %s do not permit update (status %s)" % (submission_id, submission.mark))
        raise errors.SubmissionConcluded

    try:
        import_files(store, submission, request['files'])
    except Exception as excep:
        log.err("Submission update: files import fail: %s" % excep)
        log.exception(excep)
        raise excep

    try:
        wb_steps = request['wb_steps']
        if finalize:
            steps = db_get_context_steps(store, context.id, language)
            #TODO: move to client code
            #verify_steps(steps, wb_steps)

        submission.wb_steps = wb_steps
    except Exception as excep:
        log.err("Submission update: fields validation fail: %s" % excep)
        log.exception(excep)
        raise excep

    try:
        import_receivers(store, submission, request['receivers'], required=finalize)
    except Exception as excep:
        log.err("Submission update: receiver import fail: %s" % excep)
        log.exception(excep)
        raise excep

    if finalize:
        submission.mark = u'finalize'  # Finalized

        #TODO: validation
        submission.pgp_glkey_pub = request['pgp_glkey_pub']
        submission.pgp_glkey_priv = request['pgp_glkey_priv']
    else:
        submission.mark = u'submission' # Submission

    submission_dict = wb_serialize_internaltip(submission)
    return submission_dict

@transact
def update_submission(*args):
    return db_update_submission(*args)

@transact_ro
def get_submission(store, submission_id):
    submission = store.find(InternalTip, InternalTip.id == unicode(submission_id)).one()

    if not submission:
        log.err("Invalid Submission requested %s in GET" % submission_id)
        raise errors.SubmissionIdNotFound

    return wb_serialize_internaltip(submission)

@transact
def delete_submission(store, submission_id):
    submission = store.find(InternalTip, InternalTip.id == unicode(submission_id)).one()

    if not submission:
        log.err("Invalid Submission requested %s in DELETE" % submission_id)
        raise errors.SubmissionIdNotFound

    if submission.mark != u'submission':
        log.err("Submission %s already concluded (status: %s)" % (submission_id, submission.mark))
        raise errors.SubmissionConcluded

    store.remove(submission)


class SubmissionCreate(BaseHandler):
    """
    This class create the submission, receiving a partial wbSubmissionDesc, and
    returning a submission_id, usable in update operation.
    """

    @transport_security_check('wb')
    @unauthenticated
    @inlineCallbacks
    def post(self):
        """
        Request: wbSubmissionDesc
        Response: wbSubmissionDesc
        Errors: ContextIdNotFound, InvalidInputFormat, SubmissionFailFields

        This creates an empty submission for the requested context,
        and returns submissionStatus with empty fields and a Submission Unique String,
        This is the unique token used during the submission procedure.
        header session_id is used as authentication secret for the next interaction.
        expire after the time set by Admin (Context dependent setting)
        """
        @transact
        def post_transact(store, request, language):
            status = db_create_submission(store, request, request['finalize'], language)

            if request['finalize']:
                receipt = db_create_whistleblower_tip(store, status)
                status.update({'receipt': receipt})
            else:
                status.update({'receipt' : ''})

            return status

        request = self.validate_message(self.request.body, requests.wbSubmissionDesc)

        status = yield post_transact(request, self.request.language)

        self.set_status(201) # Created
        self.finish(status)


class SubmissionInstance(BaseHandler):
    """
    This is the interface for create, populate and complete a submission.
    Relay in the client-server update and exchange of the submissionStatus message.
    """

    @transport_security_check('wb')
    @unauthenticated
    @inlineCallbacks
    def get(self, submission_id):
        """
        Parameters: submission_id
        Response: wbSubmissionDesc
        Errors: SubmissionIdNotFound, InvalidInputFormat

        Get the status of the current submission.
        """
        submission = yield get_submission(submission_id)

        self.set_status(200)
        self.finish(submission)

    @transport_security_check('wb')
    @unauthenticated
    @inlineCallbacks
    def put(self, submission_id):
        """
        Parameter: submission_id
        Request: wbSubmissionDesc
        Response: wbSubmissionDesc
        Errors: ContextIdNotFound, InvalidInputFormat, SubmissionFailFields, SubmissionIdNotFound, SubmissionConcluded

        PUT update the submission and finalize if requested.
        """
        @transact
        def put_transact(store, submission_id, finalize, language):
            status = db_update_submission(store, submission_id, request,
                                          request['finalize'], self.request.language)

            if request['finalize']:
                receipt = db_create_whistleblower_tip(store, status)
                status.update({'receipt': receipt})
            else:
                status.update({'receipt' : ''})

            return status

        request = self.validate_message(self.request.body, requests.wbSubmissionDesc)

        status = yield put_transact(submission_id, request, self.request.language)

        self.set_status(202) # Updated
        self.finish(status)


    @transport_security_check('wb')
    @unauthenticated
    @inlineCallbacks
    def delete(self, submission_id):
        """
        Parameter: submission_id
        Request:
        Response: None
        Errors: SubmissionIdNotFound, SubmissionConcluded

        A whistleblower is deleting a Submission because has understand that won't really 
        be an hero. :P

        This operation is available and tested but not implemented in the GLClient
        """

        yield delete_submission(submission_id)

        self.set_status(200) # Accepted
        self.finish()

