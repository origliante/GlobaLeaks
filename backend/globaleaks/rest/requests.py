# -*- coding: UTF-8
#   Requests
#   ********
#
# This file contains the specification of all the requests that can be made by a
# GLClient to a GLBackend.
# These specifications may be used with rest.validateMessage() inside each of the API
# handler in order to verify if the request is correct.

uuid_regexp                       = r'^([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})$'
uuid_regexp_or_empty              = r'^([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})$|^$'
receiver_img_regexp               = r'^([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}).png$'
email_regexp                      = r'^([\w-]+\.)*[\w-]+@([\w-]+\.)+[a-z]{2,9}$|^$'
email_regexp_or_empty             = r'^([\w-]+\.)*[\w-]+@([\w-]+\.)+[a-z]{2,9}$|^$'
hidden_service_regexp             = r'^http://[0-9a-z]{16}\.onion$'
hidden_service_regexp_or_empty    = r'^http://[0-9a-z]{16}\.onion$$|^$'
https_url_regexp                  = r'^https://([0-9a-z\-]+)\.(.*)$'
https_url_regexp_or_empty         = r'^https://([0-9a-z\-]+)\.(.*)$|^$'
landing_page_regexp               = r'^homepage$|^submissionpage$'

dateType = r'(.*)'

# contentType = r'(application|audio|text|video|image)'
# via stackoverflow:
# /^(application|audio|example|image|message|model|multipart|text|video)\/[a-zA-Z0-9]+([+.-][a-zA-z0-9]+)*$/
contentType = r'(.*)'

fileDict = {
    'name': unicode,
    'description': unicode,
    'size': int,
    'content_type': contentType,
    'date': dateType,
    }

formFieldsDict = {
    'key': unicode,
    'presentation_order': int,
    'name': unicode,
    'required': bool,
    'preview': bool,
    'hint': unicode,
    'type': unicode,
}

authDict = {
    'username' : unicode,
    'password' : unicode,
    'role' : unicode
}

wbSubmissionDesc = {
    'wb_steps' : list,
    'context_id' : uuid_regexp,
    'receivers' : [ uuid_regexp ],
    'files' : [ uuid_regexp ],
    'finalize' : bool,
}

receiverReceiverDesc = {
    'name' : unicode,
    'password' : unicode,
    'old_password': unicode,
    # 'username' : unicode, XXX at creation time is the same of mail_address
    'mail_address' : email_regexp,
    # mail_address contain the 'admin' inserted mail
    "ping_mail_address": email_regexp,
    # ping_mail_address is a copy of 'mail_address' if unset.
    'description' : unicode,
    'gpg_key_remove': bool,
    'gpg_key_fingerprint': unicode,
    'gpg_key_expiration': unicode,
    'gpg_key_info': unicode,
    'gpg_key_armor': unicode,
    'gpg_key_status': unicode,
    'pgp_key_armor_priv': unicode,
    'pgp_glkey_pub': unicode,
    'pgp_glkey_priv': unicode,
    "comment_notification": bool,
    "file_notification": bool,
    "tip_notification": bool,
    "message_notification": bool,
    "ping_notification": bool,
    "language": unicode,
    "timezone": int,
}

actorsCommentDesc = {
    'content' : unicode,
}

actorsTipOpsDesc = {
    'global_delete' : bool,
    'extend': bool,
}

adminStepDesc = {
    'label': unicode,
    'hint': unicode,
    'description': unicode,
    'children': list
}

adminNodeDesc = {
    'name': unicode,
    'description' : unicode,
    'presentation' : unicode,
    'footer': unicode,
    'security_awareness_title': unicode,
    'security_awareness_text': unicode,
    'whistleblowing_question': unicode,
    'whistleblowing_button': unicode,
    'hidden_service' : hidden_service_regexp_or_empty,
    'public_site' : https_url_regexp_or_empty,
    'stats_update_time' : int,
    'email' : email_regexp_or_empty, # FIXME old versions of globaleaks have an empty value
    'password' : unicode,            # and in addition the email is not set before wizard.
    'old_password' : unicode,
    'languages_enabled': [ unicode ],
    'languages_supported': list,
    'default_language' : unicode,
    'maximum_namesize': int,
    'maximum_textsize': int,
    'maximum_filesize': int,
    'tor2web_admin': bool,
    'tor2web_submission': bool,
    'tor2web_receiver': bool,
    'tor2web_unauth': bool,
    'postpone_superpower': bool,
    'can_delete_submission': bool,
    'exception_email': email_regexp,
    'ahmia': bool,
    'allow_unencrypted': bool,
    'wizard_done': bool,
    'disable_privacy_badge': bool,
    'disable_security_awareness_badge': bool,
    'disable_security_awareness_questions': bool,
    'configured': bool,
    'admin_language': unicode,
    'admin_timezone': int,
    'enable_custom_privacy_badge': bool,
    'custom_privacy_badge_tor': unicode,
    'custom_privacy_badge_none': unicode,
    'header_title_homepage': unicode,
    'header_title_submissionpage': unicode,
    'landing_page': landing_page_regexp
}

adminNotificationDesc = {
    'server': unicode,
    'port': int,
    'security': unicode, # 'TLS' or 'SSL' only
    'username': unicode,
    'password': unicode,
    'source_name' : unicode,
    'source_email' : email_regexp,
    'admin_anomaly_template': unicode,
    'encrypted_tip_template': unicode,
    'encrypted_tip_mail_title': unicode,
    'plaintext_tip_template': unicode,
    'plaintext_tip_mail_title': unicode,
    'encrypted_file_template': unicode,
    'encrypted_file_mail_title': unicode,
    'plaintext_file_template': unicode,
    'plaintext_file_mail_title': unicode,
    'encrypted_comment_template': unicode,
    'encrypted_comment_mail_title': unicode,
    'plaintext_comment_template': unicode,
    'plaintext_comment_mail_title': unicode,
    'encrypted_message_template': unicode,
    'encrypted_message_mail_title': unicode,
    'plaintext_message_template': unicode,
    'plaintext_message_mail_title': unicode,
    'admin_pgp_alert_mail_template': unicode,
    'admin_pgp_alert_mail_title': unicode,
    'pgp_alert_mail_template': unicode,
    'pgp_alert_mail_title': unicode,
    'zip_description': unicode,
    'ping_mail_template': unicode,
    'ping_mail_title': unicode,
    'disable_admin_notification_emails': bool,
    'disable_receivers_notification_emails': bool
}

adminContextDesc = {
    'name': unicode,
    'description': unicode,
    'receiver_introduction': unicode,
    'postpone_superpower': bool,
    'can_delete_submission': bool,
    'maximum_selectable_receivers': int,
    'tip_max_access' : int,
    'tip_timetolive' : int,
    'file_max_download' : int,
    'receivers' : [ uuid_regexp ],
    'steps': list,
    'select_all_receivers': bool,
    'show_small_cards': bool,
    'show_receivers': bool,
    'enable_private_messages': bool,
    'presentation_order': int,
}

adminContextFieldTemplateCopy = {
    'template_id': uuid_regexp,
    'context_id': uuid_regexp,
    'step_id': uuid_regexp,
}

adminReceiverDesc = {
    'password': unicode,
    'mail_address': email_regexp,
    'name': unicode,
    'description': unicode,
    'contexts': [ uuid_regexp ],
    'can_delete_submission': bool,
    'postpone_superpower': bool,
    'tip_notification': bool,
    'file_notification': bool,
    'comment_notification': bool,
    'message_notification': bool,
    'gpg_key_remove': bool,
    'gpg_key_fingerprint': unicode,
    'gpg_key_expiration': unicode,
    'gpg_key_info': unicode,
    'gpg_key_armor': unicode,
    'gpg_key_status': unicode,
    'pgp_key_armor_priv': unicode,
    'pgp_glkey_pub': unicode,
    'pgp_glkey_priv': unicode,
    'presentation_order': int,
    "language": unicode,
    "timezone": int,
}

anonNodeDesc = {
    'name': unicode,
    'description': unicode,
    'presentation': unicode,
    'footer': unicode,
    'security_awareness_title': unicode,
    'security_awareness_text': unicode,
    'hidden_service' : hidden_service_regexp_or_empty,
    'public_site' : https_url_regexp_or_empty,
    'email' : email_regexp,
    'languages_enabled': [ unicode ],
    'languages_supported': list,
    'default_language' : unicode,
    'maximum_namesize': int,
    'maximum_textsize': int,
    'maximum_filesize': int,
    'tor2web_admin': bool,
    'tor2web_submission': bool,
    'tor2web_receiver': bool,
    'tor2web_unauth': bool,
    'postpone_superpower': bool,
    'can_delete_submission': bool,
    'ahmia': bool,
    'allow_unencrypted': bool,
    'wizard_done': bool,
    'configured': bool,
    'disable_privacy_badge': bool,
    'disable_security_awareness_badge': bool,
    'disable_security_awareness_questions': bool,
    'enable_custom_privacy_badge': bool,
    'custom_privacy_badge_tor': unicode,
    'custom_privacy_badge_none': unicode,
}

adminStats = {
    'week_delta': int,
    # 'report_link': unicode,
}

TipOverview = {
    'status': unicode,
    'context_id': uuid_regexp,
    'creation_lifetime': dateType,
    'receivertips': list,
    'creation_date': dateType,
    'context_name': unicode,
    'id': uuid_regexp,
    'wb_access_counter': int,
    'internalfiles': list,
    'comments': list,
    'wb_last_access': unicode,
    'expiration_date': dateType,
}

TipsOverview = [ TipOverview ]

UserOverview = {
    'receivertips': list,
    'receiverfiles': list,
    'gpg_key_status': unicode,
    'id': uuid_regexp,
    'name': unicode,
}

UsersOverview = [ UserOverview ]

FileOverview = {
    'rfiles': int,
    'stored': bool,
    'name': unicode,
    'content_type': unicode,
    'itip': uuid_regexp,
    'path': unicode,
    'creation_date': dateType,
    'id': uuid_regexp,
    'size': int,
}

FilesOverview = [ FileOverview ]

StatsLine = {
     'file_uploaded': int,
     'new_submission': int,
     'finalized_submission': int,
     'anon_requests': int,
     'creation_date': dateType,
}

StatsCollection = [ StatsLine ]

AnomalyLine = {
     'message': unicode,
     'creation_date': dateType,
}

AnomaliesCollection = [ AnomalyLine ]

nodeReceiver = {
     'update_date': unicode,
     'name': unicode,
     'contexts': [ uuid_regexp ],
     'description': unicode,
     'presentation_order': int,
     'gpg_key_status': unicode,
     'id': uuid_regexp,
     'creation_date': dateType,
}

nodeReceiverCollection = [ nodeReceiver ]

# TODO - TO be removed when migration is complete
field = {
    'incremental_number': int,
    'name': unicode,
    'hint': unicode,
    'required': bool,
    'presentation_order': int,
    'trigger': list,
    'key': uuid_regexp,
    'preview': bool,
    'type': unicode,
}

nodeContext = {
    'select_all_receivers': bool,
    'name': unicode,
    'presentation_order': int,
    'description': unicode,
    'tip_timetolive': int,
    'submission_introduction': unicode,
    'maximum_selectable_receivers': int,
    'show_small_cards': bool,
    'show_receivers': bool,
    'enable_private_messages': bool,
    'file_max_download': int,
    'tip_max_access': int,
    'id': uuid_regexp,
    'receivers': [ uuid_regexp ],
    'submission_disclaimer': unicode,
}

nodeContextCollection = [ nodeContext ]

ahmiaDesc = {
    'description': unicode,
    'language': unicode,
    'title': unicode,
    'contactInformation': unicode,
    'relation': unicode,
    'keywords': unicode,
    'type': unicode,
}

staticFile = {
    'elapsed_time': float,
    'size': int,
    'filelocation': unicode,
    'content_type': unicode,
    'filename': unicode,
}

staticFileCollectionElem = {
    'size': int,
    'filename': unicode,
}

staticFileCollection = [ staticFileCollectionElem ]

internalTipDesc = {
    'wb_steps': list,
    'receivers': [ uuid_regexp ],
    'context_id': uuid_regexp,
    'access_limit': int,
    'creation_date': dateType,
    'mark': unicode,
    'id': uuid_regexp,
    'files': [ uuid_regexp ],
    'expiration_date': dateType,
    'download_limit': int,
}

FieldDesc = {
    'step_id': uuid_regexp_or_empty,
    'fieldgroup_id': uuid_regexp_or_empty,
    'label': unicode,
    'description': unicode,
    'hint': unicode,
    'multi_entry': bool,
    'x': int,
    'y': int,
    'required': bool,
    'preview': bool,
    'stats_enabled': bool,
    'type': (r'^('
             'inputbox|'
             'textarea|'
             'selectbox|'
             'checkbox|'
             'modal|'
             'dialog|'
             'tos|'
             'fileupload|'
             'fieldgroup)$'),
    'options': list,
    'children': list,
    'is_template': bool,
}

FieldTemplateDesc = {
    'fieldgroup_id': uuid_regexp_or_empty,
    'label': unicode,
    'description': unicode,
    'hint': unicode,
    'multi_entry': bool,
    'x': int,
    'y': int,
    'required': bool,
    'preview': bool,
    'stats_enabled': bool,
    'type': (r'^('
             'inputbox|'
             'textarea|'
             'selectbox|'
             'checkbox|'
             'modal|'
             'dialog|'
             'tos|'
             'fileupload|'
             'fieldgroup)$'),
    'options': list,
    'children': list,
    'is_template': bool,
}

FieldFromTemplateDesc = {
    'step_id': uuid_regexp,
    'template_id': uuid_regexp
}

wizardStepDesc = {
    'label': dict,
    'hint': dict,
    'description': dict,
    'children': list,
}

wizardNodeDesc = {
    'presentation': dict,
    'footer': dict,
}

wizardAppdataDesc = {
    'version': int,
    'fields': [ wizardStepDesc ],
    'node': wizardNodeDesc,
}

wizardFirstSetup = {
    'receiver' : adminReceiverDesc,
    'context' : adminContextDesc,
    'node' : adminNodeDesc,
}
