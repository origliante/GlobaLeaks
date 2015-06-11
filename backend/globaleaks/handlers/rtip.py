# -*- coding: UTF-8
#
# rtip
# ****
#
# Contains all the logic for handling tip related operations, for the
# receiver side. These classes are executed in the /rtip/* URI PATH

from twisted.internet.defer import inlineCallbacks
from storm.expr import Desc, And

from globaleaks.handlers.base import BaseHandler
from globaleaks.handlers.authentication import transport_security_check, authenticated
from globaleaks.rest import requests

from globaleaks.utils.utility import log, utc_future_date, datetime_now, \
    datetime_to_ISO8601, datetime_to_pretty_str

from globaleaks.utils.structures import Rosetta
from globaleaks.settings import transact, transact_ro
from globaleaks.models import Node, Notification, Comment, Message, \
    ReceiverFile, ReceiverTip, EventLogs
from globaleaks.rest import errors


def receiver_serialize_tip(internaltip, language):
    ret_dict = {
        'id': internaltip.id,
        'context_id': internaltip.context.id,
        'creation_date': datetime_to_ISO8601(internaltip.creation_date),
        'expiration_date': datetime_to_ISO8601(internaltip.expiration_date),
        'wb_steps': internaltip.wb_steps,
        # this field "inform" the receiver of the new expiration date that can
        # be set, only if PUT with postpone = True is updated
        'potential_expiration_date': \
            datetime_to_ISO8601(utc_future_date(seconds=internaltip.context.tip_timetolive)),
        'enable_comments': internaltip.context.enable_comments,
        'enable_private_messages': internaltip.context.enable_private_messages,
<<<<<<< HEAD
        'wb_e2e_public': internaltip.wb_e2e_public
=======
        'pgp_glkey_pub': internaltip.pgp_glkey_pub,
        'pgp_glkey_priv': internaltip.pgp_glkey_priv,
>>>>>>> 03d2b2e94f2a61176fb07e127ef60b89944ea235
    }

    # context_name and context_description are localized fields
    mo = Rosetta(internaltip.context.localized_strings)
    mo.acquire_storm_object(internaltip.context)
    for attr in ['name', 'description']:
        key = "context_%s" % attr
        ret_dict[key] = mo.dump_localized_attr(attr, language)

    return ret_dict


def receiver_serialize_file(internalfile, receiverfile, receivertip_id):
    """
    ReceiverFile is the mixing between the metadata present in InternalFile
    and the Receiver-dependent, and for the client sake receivertip_id is
    required to create the download link
    """

    if receiverfile.status != 'unavailable':

        ret_dict = {
            'id': receiverfile.id,
            'ifile_id': internalfile.id,
            'status': receiverfile.status,
            'href': "/rtip/" + receivertip_id + "/download/" + receiverfile.id,
            # if the ReceiverFile has encrypted status, we append ".pgp" to the filename, to avoid mistake on Receiver side.
            'name': ("%s.pgp" % internalfile.name) if receiverfile.status == u'encrypted' else internalfile.name,
            'content_type': internalfile.content_type,
            'creation_date': datetime_to_ISO8601(internalfile.creation_date),
            'size': receiverfile.size,
            'downloads': receiverfile.downloads
        }

    else:  # == 'unavailable' in this case internal file metadata is returned.

        ret_dict = {
            'id': receiverfile.id,
            'ifile_id': internalfile.id,
            'status': 'unavailable',
            'href': "",
            'name': internalfile.name,  # original filename
            'content_type': internalfile.content_type,  # original content size
            'creation_date': datetime_to_ISO8601(internalfile.creation_date),  # original creation_date
            'size': int(internalfile.size),  # original filesize
            'downloads': unicode(receiverfile.downloads)  # this counter is always valid
        }

    return ret_dict


def db_get_files_receiver(store, user_id, tip_id):
    rtip = db_access_tip(store, user_id, tip_id)

    receiver_files = store.find(ReceiverFile,
                                (ReceiverFile.internaltip_id == rtip.internaltip_id,
                                 ReceiverFile.receiver_id == rtip.receiver_id))

    files_list = []
    for receiverfile in receiver_files:
        internalfile = receiverfile.internalfile
        files_list.append(receiver_serialize_file(internalfile, receiverfile, tip_id))

    return files_list


def db_get_tip_receiver(store, user_id, tip_id, language):
    rtip = db_access_tip(store, user_id, tip_id)

    notif = store.find(Notification).one()
    if not notif.send_email_for_every_event:
        # Events related to this tip and for which the email have been sent can be removed
        store.find(EventLogs, And(EventLogs.receivertip_id == tip_id,
                                  EventLogs.mail_sent == True)).remove()

    tip_desc = receiver_serialize_tip(rtip.internaltip, language)

    # are added here because part of ReceiverTip, not InternalTip
    tip_desc['access_counter'] = rtip.access_counter
    tip_desc['id'] = rtip.id
    tip_desc['receiver_id'] = user_id
    tip_desc['label'] = rtip.label

    node = store.find(Node).one()

    tip_desc['can_postpone_expiration'] = (node.can_postpone_expiration or
                                           rtip.internaltip.context.can_postpone_expiration or
                                           rtip.receiver.can_postpone_expiration)

    tip_desc['can_delete_submission'] = (node.can_delete_submission or
                                         rtip.internaltip.context.can_delete_submission or
                                         rtip.receiver.can_delete_submission)

    return tip_desc


def db_increment_receiver_access_count(store, user_id, tip_id):
    rtip = db_access_tip(store, user_id, tip_id)

    rtip.access_counter += 1
    rtip.last_access = datetime_now()

    log.debug("Tip %s access garanted to user %s (%d)" %
              (rtip.id, rtip.receiver.name, rtip.access_counter))

    return rtip.access_counter


def db_access_tip(store, user_id, tip_id):
    rtip = store.find(ReceiverTip, ReceiverTip.id == unicode(tip_id),
                      ReceiverTip.receiver_id == user_id).one()

    if not rtip:
        raise errors.TipIdNotFound

    return rtip

@transact
def delete_internal_tip(store, user_id, tip_id):
    """
    Delete internalTip is possible only to Receiver with
    the dedicated property.
    """
    rtip = db_access_tip(store, user_id, tip_id)

    node = store.find(Node).one()

    if not (node.can_delete_submission or
                rtip.internaltip.context.can_delete_submission or
                rtip.receiver.can_delete_submission):
        raise errors.ForbiddenOperation

    store.remove(rtip.internaltip)


@transact
def postpone_expiration_date(store, user_id, tip_id):
    rtip = db_access_tip(store, user_id, tip_id)

    node = store.find(Node).one()

    if not (node.can_postpone_expiration or
                rtip.internaltip.context.can_postpone_expiration or
                rtip.receiver.can_postpone_expiration):

        raise errors.ExtendTipLifeNotEnabled()
    else:
        log.debug("Postpone check: Node %s, Context %s, Receiver %s" % (
            "True" if node.can_postpone_expiration else "False",
            "True" if rtip.internaltip.context.can_postpone_expiration else "False",
            "True" if rtip.receiver.can_postpone_expiration else "False"
        ))

    rtip.internaltip.expiration_date = \
        utc_future_date(seconds=rtip.internaltip.context.tip_timetolive)

    log.debug(" [%s] in %s has postponeed expiration time to %s" % (
        rtip.receiver.name,
        datetime_to_pretty_str(datetime_now()),
        datetime_to_pretty_str(rtip.internaltip.expiration_date)))

    comment = Comment()
    comment.system_content = dict({
        'type': "1",  # the first kind of structured system_comments
        'receiver_name': rtip.receiver.name,
        'expire_on': datetime_to_ISO8601(rtip.internaltip.expiration_date)
    })

    # remind: this is put just for debug, it's never used in the flow
    # and a system comment may have nothing to say except the struct
    comment.content = "%s %s %s (UTC)" % (
        rtip.receiver.name,
        datetime_to_pretty_str(datetime_now()),
        datetime_to_pretty_str(rtip.internaltip.expiration_date))

    comment.internaltip_id = rtip.internaltip.id
    comment.author = u'System'
    comment.type = u'system'

    rtip.internaltip.comments.add(comment)


@transact
def get_tip(store, user_id, tip_id, language):
    db_increment_receiver_access_count(store, user_id, tip_id)
    answer = db_get_tip_receiver(store, user_id, tip_id, language)
    answer['collection'] = '/rtip/' + tip_id + '/collection'
    answer['files'] = db_get_files_receiver(store, user_id, tip_id)

    return answer


class RTipInstance(BaseHandler):
    """
    This interface expose the Receiver Tip
    """

    @transport_security_check('receiver')
    @authenticated('receiver')
    @inlineCallbacks
    def get(self, tip_id):
        """
        Parameters: None
        Response: actorsTipDesc
        Errors: InvalidAuthentication

        tip_id can be a valid tip_id (Receiver case) or a random one (because is
        ignored, only authenticated user with whistleblower token can access to
        the wb_tip, this is why tip_is is not checked if self.is_whistleblower)

        This method is decorated as @unauthenticated because in the handler
        the various cases are managed differently.
        """

        answer = yield get_tip(self.current_user.user_id, tip_id, 'en')

        self.set_status(200)
        self.finish(answer)

    @transport_security_check('receiver')
    @authenticated('receiver')
    @inlineCallbacks
    def put(self, tip_id):
        """
        Some special operation over the Tip are handled here
        """

        request = self.validate_message(self.request.body, requests.TipOpsDesc)

        if request['operation']:
            if request['operation'] == 'postpone':
                yield postpone_expiration_date(self.current_user.user_id, tip_id)

        self.set_status(202)  # Updated
        self.finish()

    @transport_security_check('receiver')
    @authenticated('receiver')
    @inlineCallbacks
    def delete(self, tip_id):
        """
        Response: None
        Errors: ForbiddenOperation, TipIdNotFound

        delete: remove the Internaltip and all the associated data
        """
        yield delete_internal_tip(self.current_user.user_id, tip_id)

        self.set_status(200)  # Success
        self.finish()


def receiver_serialize_comment(comment):
    comment_desc = {
        'comment_id': comment.id,
        'type': comment.type,
        'content': comment.content,
        'system_content': comment.system_content if comment.system_content else {},
        'author': comment.author,
        'creation_date': datetime_to_ISO8601(comment.creation_date)
    }

    return comment_desc


@transact_ro
def get_comment_list_receiver(store, user_id, tip_id):
    rtip = db_access_tip(store, user_id, tip_id)

    comment_list = []
    for comment in rtip.internaltip.comments:
        comment_list.append(receiver_serialize_comment(comment))

    return comment_list


@transact
def create_comment_receiver(store, user_id, tip_id, request):
    rtip = db_access_tip(store, user_id, tip_id)

    comment = Comment()
    comment.content = request['content']
    comment.internaltip_id = rtip.internaltip.id
    comment.author = rtip.receiver.name
    comment.type = u'receiver'

    rtip.internaltip.comments.add(comment)

    return receiver_serialize_comment(comment)


class RTipCommentCollection(BaseHandler):
    """
    Interface use to read/write comments inside of a Tip, is not implemented as CRUD because we've not
    needs, at the moment, to delete/update comments once has been published. Comments is intended, now,
    as a stone written consideration about Tip reliability, therefore no editing and rethinking is
    permitted.
    """

    @transport_security_check('receiver')
    @authenticated('receiver')
    @inlineCallbacks
    def get(self, tip_id):
        """
        Parameters: None
        Response: actorsCommentList
        Errors: InvalidAuthentication
        """

        comment_list = yield get_comment_list_receiver(self.current_user.user_id, tip_id)

        self.set_status(200)
        self.finish(comment_list)

    @transport_security_check('receiver')
    @authenticated('receiver')
    @inlineCallbacks
    def post(self, tip_id):
        """
        Request: CommentDesc
        Response: CommentDesc
        Errors: InvalidAuthentication, InvalidInputFormat, TipIdNotFound, TipReceiptNotFound
        """

        request = self.validate_message(self.request.body, requests.CommentDesc)

        answer = yield create_comment_receiver(self.current_user.user_id, tip_id, request)

        self.set_status(201)  # Created
        self.finish(answer)


@transact_ro
def get_receiver_list_receiver(store, user_id, tip_id, language):
    rtip = db_access_tip(store, user_id, tip_id)

    receiver_list = []
    for rtip in rtip.internaltip.receivertips:
        receiver_desc = {
            "pgp_key_status": rtip.receiver.pgp_key_status,
            "can_delete_submission": rtip.receiver.can_delete_submission,
            "name": unicode(rtip.receiver.name),
            "receiver_id": unicode(rtip.receiver.id),
            "access_counter": rtip.access_counter,
<<<<<<< HEAD
            "pgp_e2e_public": rtip.receiver.pgp_e2e_public
=======
            "pgp_glkey_pub": rtip.receiver.pgp_glkey_pub,
>>>>>>> 03d2b2e94f2a61176fb07e127ef60b89944ea235
        }

        mo = Rosetta(rtip.receiver.localized_strings)
        mo.acquire_storm_object(rtip.receiver)
        receiver_desc["description"] = mo.dump_localized_attr("description", language)

        receiver_list.append(receiver_desc)

    return receiver_list


class RTipReceiversCollection(BaseHandler):
    """
    This interface return the list of the Receiver active in a Tip.
    GET /tip/<auth_tip_id>/receivers
    """

    @transport_security_check('receiver')
    @authenticated('receiver')
    @inlineCallbacks
    def get(self, tip_id):
        """
        Parameters: None
        Response: actorsReceiverList
        Errors: InvalidAuthentication
        """
        answer = yield get_receiver_list_receiver(self.current_user.user_id, tip_id, self.request.language)

        self.set_status(200)
        self.finish(answer)


def receiver_serialize_message(msg):
    return {
        'id': msg.id,
        'creation_date': datetime_to_ISO8601(msg.creation_date),
        'content': msg.content,
        'visualized': msg.visualized,
        'type': msg.type,
        'author': msg.author
    }


@transact
def get_messages_list(store, user_id, tip_id):
    rtip = db_access_tip(store, user_id, tip_id)

    msglist = store.find(Message, Message.receivertip_id == rtip.id)
    msglist.order_by(Desc(Message.creation_date))

    content_list = []
    for msg in msglist:
        content_list.append(receiver_serialize_message(msg))

        if not msg.visualized and msg.type == u'whistleblower':
            log.debug("Marking as readed message [%s] from %s" % (msg.content, msg.author))
            msg.visualized = True

    return content_list


@transact
def create_message_receiver(store, user_id, tip_id, request):
    rtip = db_access_tip(store, user_id, tip_id)

    msg = Message()
    msg.content = request['content']
    msg.receivertip_id = rtip.id
    msg.author = rtip.receiver.name
    msg.visualized = False
    msg.type = u'receiver'

    store.add(msg)

    return receiver_serialize_message(msg)


class ReceiverMsgCollection(BaseHandler):
    """
    This interface return the lists of the private messages exchanged.
    """

    @transport_security_check('receiver')
    @authenticated('receiver')
    @inlineCallbacks
    def get(self, tip_id):
        answer = yield get_messages_list(self.current_user.user_id, tip_id)

        self.set_status(200)
        self.finish(answer)

    @transport_security_check('receiver')
    @authenticated('receiver')
    @inlineCallbacks
    def post(self, tip_id):
        """
        Request: CommentDesc
        Response: CommentDesc
        Errors: InvalidAuthentication, InvalidInputFormat, TipIdNotFound, TipReceiptNotFound
        """

        request = self.validate_message(self.request.body, requests.CommentDesc)

        message = yield create_message_receiver(self.current_user.user_id, tip_id, request)

        self.set_status(201)  # Created
        self.finish(message)
