# -*- encoding: utf-8 -*-
#
# this file contain the class converting the %KeyWords% with data.
# perhaps exists something python-stable-portable-well know, this
# class has just be written down easily and fit our needs.
#
# If you know something better, please tell to us. At the moment,
# supporter KeyWords are here documented:
# https://github.com/globaleaks/GlobaLeaks/wiki/Customization-guide#customize-notification

from globaleaks.settings import GLSetting
from globaleaks.utils.utility import ISO8601_to_pretty_str_tz, ISO8601_to_day_str

def dump_submission_steps(wb_steps):
    dumptext = u"FIELD_MAIL_DUMP_STILL_NEED_TO_BE_IMPLEMENTED"

    return dumptext

def dump_file_list(filelist, files_n):
    info = "%s%s%s\n" % ("Filename",
                             " "*(40-len("Filename")),
                             "Size (Bytes)")

    for i in xrange(files_n):
        info += "%s%s%i\n" % (filelist[i]['name'],
                                " "*(40 - len(filelist[i]['name'])),
                                filelist[i]['size'])

    return info

class Templating(object):
    def format_template(self, raw_template, event_dicts):
        """
        TODO research on integration of http://docs.python.org/2/library/email
        """

        supported_event_types = {
                                  u'encrypted_tip': EncryptedTipKeyword,
                                  u'plaintext_tip': TipKeyword,
                                  u'encrypted_file': EncryptedFileKeyword,
                                  u'plaintext_file': FileKeyword,
                                  u'encrypted_comment': EncryptedCommentKeyword,
                                  u'plaintext_comment': CommentKeyword,
                                  u'encrypted_message': EncryptedMessageKeyword,
                                  u'plaintext_message': MessageKeyword,
                                  u'zip_collection': ZipFileKeyword,
                                  u'ping_mail': PingMailKeyword,
                                  u'admin_pgp_expiration_alert': AdminPGPAlertKeyword,
                                  u'pgp_expiration_alert': PGPAlertKeyword,
                                  # Upcoming expire use the same templates of Tip
                                  # and currently only one template is defined
                                  # considering exportable only not non sensitive info
                                  u'upcoming_tip_expiration': TipKeyword,
                                }

        if event_dicts.type not in supported_event_types.keys():
            raise AssertionError("%s at the moment supported: [%s] is NOT " %
                                 (supported_event_types.keys(), event_dicts.type))

        # For each Event type, we've to dispatch the right _KeyWord class
        TemplatClass = supported_event_types[event_dicts.type]
        keyword_converter = TemplatClass(event_dicts.node_info, event_dicts.context_info,
                                         event_dicts.steps_info, event_dicts.receiver_info,
                                         event_dicts.tip_info, event_dicts.subevent_info)

        # we've now:
        # 1) template => directly from Notification.*_template
        # 2) keyword_converter => object aligned with Event type and data

        for kw in keyword_converter.keyword_list:

            if raw_template.count(kw):
                # if %SomeKeyword% matches, call keyword_converter.SomeKeyword function
                variable_content = getattr(keyword_converter, kw[1:-1])()
                raw_template = raw_template.replace(kw, variable_content)

        # Is no more Raw, because all the keywords that shall be converted in
        # the Event.type, has been converted. So if you have request %TipFields% in
        # a Comment notification template, you would get just a message with a not
        # converted keyword.
        return raw_template



# Below you can see an inheritance dance!¹!!eleven!

class _KeyWord(object):
    """
    This class define the base keyword list supported by all the events,
    in example, %NodeName% is a keyword always available. Other keywords can
    be used only in specific Event.
    """

    shared_keywords = [
        '%NodeName%',
        '%HiddenService%',
        '%PublicSite%',
        '%ReceiverName%',
        '%ContextName%',
        '%NodeSignature%'
    ]

    def __init__(self, node_desc, context_desc, fields_desc, receiver_desc):

        self.keyword_list = _KeyWord.shared_keywords

        self.node = node_desc
        self.context = context_desc
        self.fields = fields_desc
        self.receiver = receiver_desc

    def NodeName(self):
        return self.node['name']

    def HiddenService(self):
        return self.node['hidden_service']

    def PublicSite(self):
        return self.node['public_site']

    def ReceiverName(self):
        return self.receiver['name']

    def ContextName(self):
        return self.context['name']

    def NodeSignature(self):
        # FIXME currently the NodeSignature is mapped on node name;
        # in future we could evaluate to introduce a different
        # variable to permit better customizations.
        return self.node['name']

class TipKeyword(_KeyWord):
    tip_keywords = [
        '%TipTorURL%',
        '%TipT2WURL%',
        '%TipNum%',
        '%EventTime%',
        '%ExpirationWatch%',
                    # ExpirationWatch
                    # TODO DB, like "notify 48 hours before"
                    # can be used in template to say "will expire in 48 hours"
        '%ExpirationDate%',
    ]

    def __init__(self, node_desc, context_desc, fields_desc, receiver_desc, tip_desc, *x):

        super(TipKeyword, self).__init__(node_desc, context_desc,
                                         fields_desc, receiver_desc)

        self.keyword_list += TipKeyword.tip_keywords
        self.tip = tip_desc

    def TipTorURL(self):
        if len(self.node['hidden_service']):
            retstr = '%s/#/status/%s' % (self.node['hidden_service'], self.tip['id'])
        else:
            retstr = 'ADMIN, CONFIGURE YOUR HIDDEN SERVICE (Advanced configuration)!'
        return retstr

    def TipT2WURL(self):
        """
        we shall enhance this issue:
        https://github.com/globaleaks/GlobaLeaks/issues/268
        making that if one of these function return None, the entire line is stripped.
        This can avoid the awkward effect of 'Public Url: [Ask to your admin about Tor]'
        """
        if not GLSetting.memory_copy.tor2web_receiver:
            retstr = "[Ask to your admin about Tor]"
        elif len(self.node['public_site']):
            retstr =  '%s/#/status/%s' % ( self.node['public_site'], self.tip['id'] )
        else:
            retstr = 'ADMIN, CONFIGURE YOUR PUBLIC SITE (Advanced configuration)!'

        return retstr

    def TipNum(self):
        """
        This is just an hack to create a random number from a TipId,
        from 1 to 1000, that shall be the same among time, and
        (without caring on collisions) different from others Tips
        """
        uuid_derived_string = self.tip['id'].replace('-', '')
        retval = 1
        for x in xrange(len(uuid_derived_string)):
            try:
                retval += int(uuid_derived_string[x])
            except Exception:
                # this happen when an ascii letter is converted
                retval *= 2

        retval = (retval % 1000) + 1
        return unicode(retval)

    def EventTime(self):
        return ISO8601_to_pretty_str_tz(self.tip['creation_date'], float(self.receiver['timezone']))

    def ExpirationDate(self):
        # is not time zone dependent, is UTC for everyone
        return ISO8601_to_day_str(self.tip['expiration_date'])

    def ExpirationWatch(self):
        # Express in hours, but has to be retrieved from the Receiver not from Tip.
        return unicode(48)

class EncryptedTipKeyword(TipKeyword):
    encrypted_tip_keywords = [
        '%TipFields%'
    ]

    def __init__(self, node_desc, context_desc, fields_desc, receiver_desc, tip_desc, *x):
        super(EncryptedTipKeyword, self).__init__(node_desc, context_desc, fields_desc,
                                                  receiver_desc, tip_desc, None)
        self.keyword_list += EncryptedTipKeyword.encrypted_tip_keywords

    def TipFields(self):
        return dump_submission_steps(self.tip['wb_steps'])


class CommentKeyword(TipKeyword):
    comment_keywords = [
        '%CommentSource%',
        '%EventTime%'
    ]

    def __init__(self, node_desc, context_desc, fields_desc, receiver_desc, tip_desc, comment_desc):
        super(CommentKeyword, self).__init__(node_desc, context_desc, fields_desc, receiver_desc, tip_desc)

        self.keyword_list += CommentKeyword.comment_keywords
        self.comment = comment_desc

    def CommentSource(self):
        return self.comment['type']

    def EventTime(self):
        return ISO8601_to_pretty_str_tz(self.comment['creation_date'], float(self.receiver['timezone']))


class EncryptedCommentKeyword(CommentKeyword):
    encrypted_comment_keywords = [
        '%CommentContent%',
    ]

    def __init__(self, node_desc, context_desc, fields_desc, receiver_desc, tip_desc, comment_desc):
        super(EncryptedCommentKeyword, self).__init__(node_desc, context_desc, fields_desc,
                                                      receiver_desc, tip_desc, comment_desc)
        self.keyword_list += EncryptedCommentKeyword.encrypted_comment_keywords

    def CommentContent(self):
        """
        Think about Comment.system_content before document and insert this
        feature in the default templates
        """
        return self.comment['content']


class MessageKeyword(TipKeyword):
    message_keywords = [
        '%MessageSource%',
        '%EventTime%'
    ]

    def __init__(self, node_desc, context_desc, fields_desc, receiver_desc, tip_desc, message_desc):
        super(MessageKeyword, self).__init__(node_desc, context_desc,
                                             fields_desc, receiver_desc,
                                             tip_desc)

        self.keyword_list += MessageKeyword.message_keywords
        self.message = message_desc

    def MessageSource(self):
        return self.message['author']

    def EventTime(self):
        return ISO8601_to_pretty_str_tz(self.message['creation_date'], float(self.receiver['timezone']))

class EncryptedMessageKeyword(MessageKeyword):
    encrypted_message_keywords = [
        '%MessageContent%',
    ]

    def __init__(self, node_desc, context_desc, fields_desc, receiver_desc, tip_desc, message_desc):
        super(EncryptedMessageKeyword, self).__init__(node_desc, context_desc,
                                                      fields_desc, receiver_desc,
                                                      tip_desc, message_desc)
        self.keyword_list += EncryptedMessageKeyword.encrypted_message_keywords

    def MessageContent(self):
        return self.message['content']


class FileKeyword(TipKeyword):
    file_keywords = [
        '%FileName%',
        '%EventTime%',
        '%FileSize%',
        '%FileType%'
    ]

    def __init__(self, node_desc, context_desc, fields_desc, receiver_desc, tip_desc, file_desc):
        super(FileKeyword, self).__init__(node_desc, context_desc,
                                          fields_desc, receiver_desc,
                                          tip_desc)

        self.keyword_list += FileKeyword.file_keywords
        self.file = file_desc

    def FileName(self):
        return self.file['name']

    def EventTime(self):
        return ISO8601_to_pretty_str_tz(self.file['creation_date'], float(self.receiver['timezone']))

    def FileSize(self):
        return self.file['size']

    def FileType(self):
        return self.file['content_type']


class EncryptedFileKeyword(FileKeyword):
    """
    FileDescription not yet implemented in UI, but here has to go
    """
    encrypted_file_keywords = [
        '%FileDescription%'
    ]

    def __init__(self, node_desc, context_desc, fields_desc, receiver_desc, tip_desc, file_desc):
        super(EncryptedFileKeyword, self).__init__(node_desc, context_desc,
                                                   fields_desc, receiver_desc,
                                                   tip_desc, file_desc)
        self.keyword_list += EncryptedFileKeyword.encrypted_file_keywords

    def FileDescription(self):
        pass


class ZipFileKeyword(TipKeyword):
    zip_file_keywords = [
        '%FileList%',
        '%FilesNumber%',
        '%TotalSize%'
    ]

    def __init__(self, node_desc, context_desc, fields_desc, receiver_desc, tip_desc, zip_desc):
        super(ZipFileKeyword, self).__init__(node_desc, context_desc,
                                             fields_desc, receiver_desc,
                                             tip_desc)

        self.keyword_list += ZipFileKeyword.zip_file_keywords
        self.zip = zip_desc

    def FileList(self):
        return dump_file_list(self.zip['files'], self.zip['file_counter'])

    def FilesNumber(self):
        return str(self.zip['file_counter'])

    def TotalSize(self):
        return str(self.zip['total_size'])


class PingMailKeyword(_KeyWord):
    ping_mail_keywords = [
        '%ReceiverName%',
        '%EventCount%'
    ]

    def __init__(self, node_desc, context_desc, fields_desc, receiver_desc, tip_desc, ping_desc):
        """
        This is a reduced version because PingMail are
        thinked to have least information as possible
        """
        super(PingMailKeyword, self).__init__(node_desc, context_desc,
                                            fields_desc, receiver_desc)

        self.keyword_list += PingMailKeyword.ping_mail_keywords

        self.name = receiver_desc['name']
        self.counter = ping_desc['counter']

    def ReceiverName(self):
        return str(self.name)

    def EventCount(self):
        return str(self.counter)


class AdminPGPAlertKeyword(_KeyWord):
    admin_pgp_alert_keywords = [
        "%PGPKeyInfoList%"
    ]

    def __init__(self, node_desc, context_desc, fields_desc, receiver_desc, tip_desc, alert_desc):
        super(AdminPGPAlertKeyword, self).__init__(node_desc, context_desc,
                                                   fields_desc, receiver_desc)

        self.keyword_list += AdminPGPAlertKeyword.admin_pgp_alert_keywords

        self.alert = alert_desc

    def PGPKeyInfoList(self):
        ret = ""
        for r in self.alert['expired_or_expiring']:
            if r['pgp_key_fingerprint']:
                key = r['pgp_key_fingerprint'][:7]
            else:
                key = ""

            ret += "\t%s, %s (%s)\n" % (r['name'],
                                    key,
                                    ISO8601_to_day_str(r['pgp_key_expiration']))
        return ret


class PGPAlertKeyword(_KeyWord):
    pgp_alert_keywords = [
        "%PGPKeyInfo%"
    ]

    def __init__(self, node_desc, context_desc, fields_desc, receiver_desc, tip_desc, *x):
        super(PGPAlertKeyword, self).__init__(node_desc, context_desc,
                                              fields_desc, receiver_desc)

        self.keyword_list += PGPAlertKeyword.pgp_alert_keywords

    def PGPKeyInfo(self):
        if self.receiver['pgp_key_fingerprint']:
            key = self.receiver['pgp_key_fingerprint'][:7]
        else:
            key = ""

        return "\t0x%s (%s)" % (key, ISO8601_to_day_str(self.receiver['pgp_key_expiration']))
