from storm.exceptions import DatabaseError
from twisted.internet.defer import inlineCallbacks

from globaleaks.db.datainit import db_update_memory_variables
from globaleaks.handlers.base import BaseHandler
from globaleaks.handlers.authentication import authenticated, transport_security_check
from globaleaks.models import Notification
from globaleaks.rest import errors, requests
from globaleaks.settings import transact, transact_ro
from globaleaks.utils.structures import fill_localized_keys, get_localized_values
from globaleaks.utils.utility import log


def admin_serialize_notification(notif, language):
    ret_dict = {
        'server': notif.server if notif.server else u"",
        'port': notif.port if notif.port else u"",
        'username': notif.username if notif.username else u"",
        'password': notif.password if notif.password else u"",
        'security': notif.security if notif.security else u"",
        'source_name' : notif.source_name,
        'source_email' : notif.source_email,
        'disable_admin_notification_emails': notif.disable_admin_notification_emails,
        'disable_receivers_notification_emails': notif.disable_receivers_notification_emails,
        'send_email_for_every_event': notif.send_email_for_every_event
    }

    return get_localized_values(ret_dict, notif, notif.localized_strings, language)

@transact_ro
def get_notification(store, language):
    try:
        notif = store.find(Notification).one()
    except Exception as excep:
        log.err("Database error when getting Notification table: %s" % str(excep))
        raise excep

    return admin_serialize_notification(notif, language)

@transact
def update_notification(store, request, language):

    try:
        notif = store.find(Notification).one()
    except Exception as excep:
        log.err("Database error or application error: %s" % excep )
        raise excep

    fill_localized_keys(request, Notification.localized_strings, language)

    notif.security = request['security']

    try:
        notif.update(request)
    except DatabaseError as dberror:
        log.err("Unable to update Notification: %s" % dberror)
        raise errors.InvalidInputFormat(dberror)

    db_update_memory_variables(store)

    return admin_serialize_notification(notif, language)


class NotificationInstance(BaseHandler):
    """
    Manage Notification settings (account details and template)
    """

    @transport_security_check('admin')
    @authenticated('admin')
    @inlineCallbacks
    def get(self):
        """
        Parameters: None
        Response: AdminNotificationDesc
        Errors: None (return empty configuration, at worst)
        """
        notification_desc = yield get_notification(self.request.language)
        self.set_status(200)
        self.finish(notification_desc)

    @transport_security_check('admin')
    @authenticated('admin')
    @inlineCallbacks
    def put(self):
        """
        Request: AdminNotificationDesc
        Response: AdminNotificationDesc
        Errors: InvalidInputFormat

        Changes the node notification settings.
        """

        request = self.validate_message(self.request.body,
            requests.AdminNotificationDesc)

        response = yield update_notification(request, self.request.language)

        self.set_status(202) # Updated
        self.finish(response)
