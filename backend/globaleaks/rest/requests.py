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
tip_operation_regexp              = r'^postpone$'

DateType = r'(.*)'

# ContentType = r'(application|audio|text|video|image)'
# via stackoverflow:
# /^(application|audio|example|image|message|model|multipart|text|video)\/[a-zA-Z0-9]+([+.-][a-zA-z0-9]+)*$/
ContentType = r'(.*)'

FileDesc = {
    'name': unicode,
    'description': unicode,
    'size': int,
    'content_type': ContentType,
    'date': DateType
}

AuthDesc = {
    'username': unicode,
    'password': unicode,
    'role': unicode
}

<<<<<<< HEAD
SubmissionDesc = {
    'wb_steps': list,
    'human_captcha_answer': int,
    'receivers': [uuid_regexp],
    'wb_e2e_public': unicode,
    'wb_signature': unicode,
=======
wbSubmissionDesc = {
    'wb_steps' : list,
    'context_id' : uuid_regexp,
    'receivers' : [ uuid_regexp ],
    'files' : [ uuid_regexp ],
    'finalize' : bool,
    'pgp_glkey_pub': unicode,
    'pgp_glkey_priv': unicode
>>>>>>> 03d2b2e94f2a61176fb07e127ef60b89944ea235
}

ReceiverReceiverDesc = {
    'name': unicode,
    'password': unicode,
    'old_password': unicode,
<<<<<<< HEAD
    'mail_address': email_regexp,
    'ping_mail_address': email_regexp,
    'description': unicode,
    'pgp_key_remove': bool,
    'pgp_key_fingerprint': unicode,
    'pgp_key_expiration': unicode,
    'pgp_key_info': unicode,
    'pgp_key_public': unicode,
    'pgp_key_status': unicode,
    'pgp_e2e_public': unicode,
    'pgp_e2e_private': unicode,
=======
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
>>>>>>> 03d2b2e94f2a61176fb07e127ef60b89944ea235
    "tip_notification": bool,
    "ping_notification": bool,
    "language": unicode,
    "timezone": int
}

CommentDesc = {
    'content': unicode
}

TipOpsDesc = {
    'operation': tip_operation_regexp,
}

AdminStepDesc = {
    'label': unicode,
    'hint': unicode,
    'description': unicode,
    'children': list
}

AdminNodeDesc = {
    'name': unicode,
    'description': unicode,
    'presentation': unicode,
    'footer': unicode,
    'security_awareness_title': unicode,
    'security_awareness_text': unicode,
    'whistleblowing_question': unicode,
    'whistleblowing_button': unicode,
    'hidden_service': hidden_service_regexp_or_empty,
    'public_site': https_url_regexp_or_empty,
    'email': email_regexp_or_empty, # FIXME old versions of globaleaks have an empty value
    'password': unicode,            # and in addition the email is not set before wizard.
    'old_password': unicode,
    'languages_enabled': [unicode],
    'languages_supported': list,
    'default_language': unicode,
    'maximum_namesize': int,
    'maximum_textsize': int,
    'maximum_filesize': int,
    'tor2web_admin': bool,
    'tor2web_submission': bool,
    'tor2web_receiver': bool,
    'tor2web_unauth': bool,
    'can_postpone_expiration': bool,
    'can_delete_submission': bool,
    'exception_email': email_regexp,
    'ahmia': bool,
    'allow_unencrypted': bool,
    'wizard_done': bool,
    'disable_privacy_badge': bool,
    'disable_security_awareness_badge': bool,
    'disable_security_awareness_questions': bool,
    'disable_key_code_hint': bool,
    'configured': bool,
    'admin_language': unicode,
    'admin_timezone': int,
    'enable_custom_privacy_badge': bool,
    'custom_privacy_badge_tor': unicode,
    'custom_privacy_badge_none': unicode,
    'header_title_homepage': unicode,
    'header_title_submissionpage': unicode,
    'header_title_receiptpage': unicode,
    'landing_page': landing_page_regexp,
	'show_contexts_in_alphabetical_order': bool,
    'file_encryption_e2e': bool,
    'submission_data_e2e': bool,
}

AdminNotificationDesc = {
    'server': unicode,
    'port': int,
    'security': unicode, # 'TLS' or 'SSL' only
    'username': unicode,
    'password': unicode,
    'source_name': unicode,
    'source_email': email_regexp,
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
    'disable_receivers_notification_emails': bool,
    'send_email_for_every_event': bool
}

AdminContextDesc = {
    'name': unicode,
    'description': unicode,
    'receiver_introduction': unicode,
    'can_postpone_expiration': bool,
    'can_delete_submission': bool,
    'maximum_selectable_receivers': int,
    'tip_timetolive': int,
    'receivers': [uuid_regexp],
    'steps': list,
    'select_all_receivers': bool,
    'show_small_cards': bool,
    'show_receivers': bool,
    'enable_private_messages': bool,
    'presentation_order': int,
    'show_receivers_in_alphabetical_order': bool,
    'reset_steps': bool
}

AdminContextFieldTemplateCopyDesc = {
    'template_id': uuid_regexp,
    'context_id': uuid_regexp,
    'step_id': uuid_regexp_or_empty
}

AdminReceiverDesc = {
    'password': unicode,
    'mail_address': email_regexp,
    'name': unicode,
    'description': unicode,
    'contexts': [uuid_regexp],
    'can_delete_submission': bool,
    'can_postpone_expiration': bool,
    'tip_notification': bool,
<<<<<<< HEAD
    'ping_notification': bool,
    'pgp_key_remove': bool,
    'pgp_key_fingerprint': unicode,
    'pgp_key_expiration': unicode,
    'pgp_key_info': unicode,
    'pgp_key_public': unicode,
    'pgp_key_status': unicode,
    'pgp_key_public': unicode,
    'pgp_e2e_public': unicode,
    'pgp_e2e_private': unicode,
=======
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
>>>>>>> 03d2b2e94f2a61176fb07e127ef60b89944ea235
    'presentation_order': int,
    "language": unicode,
    "timezone": int
}

NodeDesc = {
    'name': unicode,
    'description': unicode,
    'presentation': unicode,
    'footer': unicode,
    'security_awareness_title': unicode,
    'security_awareness_text': unicode,
    'hidden_service': hidden_service_regexp_or_empty,
    'public_site': https_url_regexp_or_empty,
    'email': email_regexp,
    'languages_enabled': [unicode],
    'languages_supported': list,
    'default_language': unicode,
    'maximum_namesize': int,
    'maximum_textsize': int,
    'maximum_filesize': int,
    'tor2web_admin': bool,
    'tor2web_submission': bool,
    'tor2web_receiver': bool,
    'tor2web_unauth': bool,
    'can_postpone_expiration': bool,
    'can_delete_submission': bool,
    'ahmia': bool,
    'allow_unencrypted': bool,
    'wizard_done': bool,
    'configured': bool,
    'disable_privacy_badge': bool,
    'disable_security_awareness_badge': bool,
    'disable_security_awareness_questions': bool,
    'disable_key_code_hint': bool,
    'enable_custom_privacy_badge': bool,
    'custom_privacy_badge_tor': unicode,
    'custom_privacy_badge_none': unicode
}

TipOverviewDesc = {
    'context_id': uuid_regexp,
    'creation_lifetime': DateType,
    'receivertips': list,
    'creation_date': DateType,
    'context_name': unicode,
    'id': uuid_regexp,
    'wb_access_counter': int,
    'internalfiles': list,
    'comments': list,
    'wb_last_access': unicode,
    'expiration_date': DateType
}

TipsOverviewDesc = [TipOverviewDesc]

UserOverviewDesc = {
    'receivertips': list,
    'receiverfiles': list,
    'pgp_key_status': unicode,
    'id': uuid_regexp,
    'name': unicode
}

UsersOverviewDesc = [UserOverviewDesc]

FileOverviewDesc = {
    'rfiles': int,
    'stored': bool,
    'name': unicode,
    'content_type': unicode,
    'itip': uuid_regexp,
    'path': unicode,
    'creation_date': DateType,
    'id': uuid_regexp,
    'size': int
}

FilesOverviewDesc = [FileOverviewDesc]

StatsDesc = {
     'file_uploaded': int,
     'new_submission': int,
     'finalized_submission': int,
     'anon_requests': int,
     'creation_date': DateType
}

StatsCollectionDesc = [StatsDesc]

AnomalyDesc = {
     'message': unicode,
     'creation_date': DateType
}

AnomaliesCollectionDesc = [AnomalyDesc]

ReceiverDesc = {
     'update_date': unicode,
     'name': unicode,
     'contexts': [uuid_regexp],
     'description': unicode,
     'presentation_order': int,
     'pgp_key_status': unicode,
     'id': uuid_regexp,
     'creation_date': DateType
}

ReceiverCollectionDesc = [ReceiverDesc]

ContextDesc = {
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
    'id': uuid_regexp,
    'receivers': [uuid_regexp],
    'submission_disclaimer': unicode,
    'show_receivers_in_alphabetical_order': bool
}

ContextCollectionDesc = [ContextDesc]

AhmiaDesc = {
    'description': unicode,
    'language': unicode,
    'title': unicode,
    'contactInformation': unicode,
    'relation': unicode,
    'keywords': unicode,
    'type': unicode
}

StaticFileDesc = {
    'size': int,
    'filelocation': unicode,
    'content_type': unicode,
    'filename': unicode
}

InternalTipDesc = {
    'wb_steps': list,
    'receivers': [uuid_regexp],
    'context_id': uuid_regexp,
    'creation_date': DateType,
    'new': bool,
    'id': uuid_regexp,
    'files': [uuid_regexp],
    'expiration_date': DateType
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
    'is_template': bool
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
    'is_template': bool
}

FieldFromTemplateDesc = {
    'step_id': uuid_regexp_or_empty,
    'template_id': uuid_regexp
}

WizardStepDesc = {
    'label': dict,
    'hint': dict,
    'description': dict,
    'children': list
}

WizardNodeDesc = {
    'presentation': dict,
    'footer': dict
}

WizardAppdataDesc = {
    'version': int,
    'fields': [WizardStepDesc],
    'node': WizardNodeDesc
}

WizardFirstSetupDesc = {
    'receiver': AdminReceiverDesc,
    'context': AdminContextDesc,
    'node': AdminNodeDesc
}
