# -*- coding: UTF-8
#
#   mailutils
#   *********
#
# GlobaLeaks Utility used to handle Mail, format, exception, etc

import binascii
import logging
import traceback
import StringIO
from datetime import datetime
from calendar import timegm
from email import utils as mailutils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email import Charset

import re
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet import reactor, protocol, error
from twisted.internet.defer import Deferred, AlreadyCalledError, fail
from twisted.mail.smtp import ESMTPSenderFactory, SMTPClient, SMTPError
from twisted.internet.ssl import ClientContextFactory
from twisted.protocols import tls
from twisted.python.failure import Failure
from OpenSSL import SSL
from txsocksx.client import SOCKS5ClientEndpoint
from cryptography.hazmat.primitives import hashes
from globaleaks import __version__
from globaleaks.utils.utility import log
from globaleaks.settings import GLSetting
from globaleaks.security import crypto_backend


# Relevant errors from http://tools.ietf.org/html/rfc4954
smtp_errors = {
    '535 5.7.8': "Authentication credentials invalid"
}

def rfc822_date():
    """
    holy stackoverflow:
    http://stackoverflow.com/questions/3453177/convert-python-datetime-to-rfc-2822
    """
    nowdt = datetime.utcnow()
    nowtuple = nowdt.utctimetuple()
    nowtimestamp = timegm(nowtuple)
    return mailutils.formatdate(nowtimestamp)

def sendmail(authentication_username, authentication_password, from_address,
             to_address, message_file, smtp_host, smtp_port, security, event=None):
    """
    Sends an email using SMTPS/SMTP+TLS and torify the connection

    @param authentication_username: account username
    @param authentication_secret: account password
    @param from_address: the from address field of the email
    @param to_address: the to address field of the email
    @param message_file: the message content its a StringIO
    @param smtp_host: the smtp host
    @param smtp_port: the smtp port
    @param security: may need to be STRING, here is converted at start
    @param event: the event description, needed to keep track of failure/success
    """

    notif_retries = 2
    notif_timeout = 10

    def printError(method, reason, event):
        if event:
            log.err("** failed notification within event %s" % event.type)

        if isinstance(reason, Failure):
            log.err("Failed to connect to %s:%d (Sock Error: %s) (Method: %s)" %
                    (smtp_host, smtp_port, reason.value, method))
            log.debug(reason)

    def esmtp_errback(reason, *args, **kwargs):
        printError("ESMTP", reason, event)
        return result_deferred.errback(reason)

    def socks_errback(reason, *args, **kwargs):
        printError("SOCKS5", reason, event)
        return result_deferred.errback(reason)

    def tcp4_errback(reason, *args, **kwargs):
        printError("TCP4", reason, event)
        return result_deferred.errback(reason)

    def result_errback(reason, *args, **kwargs):
        "To not report an error as unexpected in the log files"
        return True

    def esmtp_sendError(self, exc):
        if exc.code and exc.resp:
            error = re.match(r'^([0-9\.]+) ', exc.resp)
            error_str = ""
            key = str(exc.code) + " " + error.group(1)
            if key in smtp_errors:
                error_str +=  " " + smtp_errors[key]

            verb = '[unknown]'
            if 'authentication' in exc.resp:
                verb = 'autenticate'
            if 'not support secure' in exc.resp:
                verb = 'negotiate TLS'

            log.err("Failed to %s to %s:%d (SMTP Code: %.3d) (%s)" %
                    (verb, smtp_host, smtp_port, exc.code, error_str))

        SMTPClient.sendError(self, exc)

    def esmtp_connectionLost(self, reason=protocol.connectionDone):
        """We are no longer connected"""
        if isinstance(reason, Failure):
            if not isinstance(reason.value, error.ConnectionDone):
                verb = 'unknown_verb'
                if 'OpenSSL' in str(reason.type):
                    verb = 'negotiate SSL'

                log.err("Failed to %s to %s:%d (%s)"
                        % (verb, smtp_host, smtp_port, reason.type))
                log.debug(reason)

        self.setTimeout(None)
        self.mailFile = None

    # TODO: validation?
    if from_address == '' or to_address == '':
        log.err("Failed to init sendmail to %s:%s (Invalid from/to addresses)" %
                (from_address, to_address))
        return

    if security != "SSL" and security != "disabled":
        requireTransportSecurity = True
    else:
        requireTransportSecurity = False

    try:
        security = str(security)
        result_deferred = Deferred()
        result_deferred.addErrback(result_errback, event)

        context_factory = ClientContextFactory()

        # evilaliv3:
        #   this is the same solution I applied to tor2web:
        #     as discussed on https://trac.torproject.org/projects/tor/ticket/11598
        #     there is no way of enabling all TLS methods excluding SSL.
        #     the problem lies in the fact that SSL.TLSv1_METHOD | SSL.TLSv1_1_METHOD | SSL.TLSv1_2_METHOD
        #     is denied by OpenSSL.
        #
        #     As spotted by nickm the only good solution right now is to enable SSL.SSLv23_METHOD then explicitly
        #     use options: SSL_OP_NO_SSLv2 and SSL_OP_NO_SSLv3
        #
        #     This trick make openssl consider valid all TLS methods.
        #
        context_factory.method = SSL.SSLv23_METHOD

        esmtp_deferred = Deferred()
        esmtp_deferred.addErrback(esmtp_errback, event)
        esmtp_deferred.addCallback(result_deferred.callback)
    except Exception as excep:
        log.err("Error in Twisted objects init - unexpected exception in sendmail: %s" % str(excep))
        return fail()

    try:
        factory = ESMTPSenderFactory(
            authentication_username,
            authentication_password,
            from_address,
            to_address,
            message_file,
            esmtp_deferred,
            contextFactory=context_factory,
            requireAuthentication=(authentication_username and authentication_password),
            requireTransportSecurity=requireTransportSecurity,
            retries=notif_retries,
            timeout=notif_timeout)

        factory.protocol.sendError = esmtp_sendError
        factory.protocol.connectionLost = esmtp_connectionLost

        if security == "SSL":
            factory = tls.TLSMemoryBIOFactory(context_factory, True, factory)

    except Exception as excep:
        log.err("Error in factory init - unexpected exception in sendmail: %s" % str(excep))
        return fail()

    try:
        if not GLSetting.disable_email_torification and GLSetting.memory_copy.notif_uses_tor:
            socksProxy = TCP4ClientEndpoint(reactor, GLSetting.socks_host, GLSetting.socks_port, timeout=notif_timeout)
            endpoint = SOCKS5ClientEndpoint(smtp_host.encode('utf-8'), smtp_port, socksProxy)
            d = endpoint.connect(factory)
            d.addErrback(socks_errback, event)
        else:
            endpoint = TCP4ClientEndpoint(reactor, smtp_host, smtp_port, timeout=notif_timeout)
            d = endpoint.connect(factory)
            d.addErrback(tcp4_errback, event)
    except Exception as excep:
        # we strongly need to avoid raising exception inside email logic to avoid chained errors
        log.err("unexpected exception in sendmail: %s" % str(excep))
        return fail()

    return result_deferred


def MIME_mail_build(src_name, src_mail, dest_name, dest_mail, title, mail_body):

    # Override python's weird assumption that utf-8 text should be encoded with
    # base64, and instead use quoted-printable (for both subject and body).  I
    # can't figure out a way to specify QP (quoted-printable) instead of base64 in
    # a way that doesn't modify global state. :-(

    Charset.add_charset('utf-8', Charset.QP, Charset.QP, 'utf-8')

    # This example is of an email with text and html alternatives.
    multipart = MIMEMultipart('alternative')

    # We need to use Header objects here instead of just assigning the strings in
    # order to get our headers properly encoded (with QP).
    # You may want to avoid this if your headers are already ASCII, just so people
    # can read the raw message without getting a headache.
    multipart['Subject'] = Header(title.encode('utf-8'), 'UTF-8').encode()
    multipart['Date'] = rfc822_date()

    multipart['To'] = Header(dest_name.encode('utf-8'), 'UTF-8').encode() + \
                        " <" + dest_mail + ">"

    multipart['From'] = Header(src_name.encode('utf-8'), 'UTF-8').encode() + \
                        " <" + src_mail + ">"

    multipart['X-Mailer'] = "fnord"

    # Attach the parts with the given encodings.
    # html = '<html>...</html>'
    # htmlpart = MIMEText(html.encode('utf-8'), 'html', 'UTF-8')
    # multipart.attach(htmlpart)

    textpart = MIMEText(mail_body.encode('utf-8'), 'plain', 'UTF-8')
    multipart.attach(textpart)

    return StringIO.StringIO(multipart.as_string())


def mail_exception(etype, value, tback):
    """
    Formats traceback and exception data and emails the error,
    This would be enabled only in the testing phase and testing release,
    not in production release.
    """
    h = hashes.Hash(hashes.SHA256(), 
                    backend=crypto_backend)
    h.update(str(value))
    sha256 = binascii.b2a_hex(h.finalize())

    if isinstance(value, GeneratorExit) or \
       isinstance(value, AlreadyCalledError) or \
       isinstance(value, SMTPError) or \
       etype == AssertionError and value.message == "Request closed":
        # we need to bypass email notification for some exception that:
        # 1) raise frequently or lie in a twisted bug;
        # 2) lack of useful stacktraces;
        # 3) can be cause of email storm amplification
        #
        # this kind of exception can be simply logged error logs.
        log.err("exception mail suppressed for exception (%s) [reason: special exception]" % str(etype))
        return
    elif sha256 in GLSetting.exceptions:
        GLSetting.exceptions[sha256] += 1
        if GLSetting.exceptions[sha256] > 5:
            # if the threashold has been exceeded
            log.err("exception mail suppressed for exception (%s) [reason: threshold exceeded]" % str(etype))
            return
    else:
        GLSetting.exceptions[sha256] = 1

    # collection of the stacktrace info
    exc_type = re.sub("(<(type|class ')|'exceptions.|'>|__main__.)",
                      "", str(etype))
    error_message = "%s %s" % (exc_type.strip(), etype.__doc__)
    traceinfo = '\n'.join(traceback.format_exception(etype, value, tback))

    if GLSetting.loglevel == logging.DEBUG:
        log.err(error_message)
        log.err(traceinfo)

    # this function can be called and used only when GLBackend is running,
    # if an exception is raise before GLSetting has been instanced and setup
    # everything will go badly. Therefore there are checked the integrity of GLSettings
    if not hasattr(GLSetting.memory_copy, 'notif_source_name') or \
        not hasattr(GLSetting.memory_copy, 'notif_source_email') or \
        not hasattr(GLSetting.memory_copy, 'exception_email'):
        log.err("Exception before of GLSetting initialization")
        print "**", error_message
        print "**", traceinfo
        return

    try:

        mail_exception.mail_counter += 1

        log.err("Exception mail! [%d]" % mail_exception.mail_counter)

        mail_body = error_message + "\n\n" + traceinfo

        message = MIME_mail_build(GLSetting.memory_copy.notif_source_name,
                                  GLSetting.memory_copy.notif_source_email,
                                  "Admin",
                                  GLSetting.memory_copy.exception_email,
                                  "Subject:%s %s [%d]" % \
                                    (" %s's development Exception" %
                                        GLSetting.developer_name if GLSetting.devel_mode else " GlobaLeaks Exception",
                                     __version__,
                                     mail_exception.mail_counter),
                                  mail_body)

        sendmail(authentication_username=GLSetting.memory_copy.notif_username,
                 authentication_password=GLSetting.memory_copy.notif_password,
                 from_address=GLSetting.memory_copy.notif_username,
                 to_address=GLSetting.memory_copy.exception_email,
                 message_file=message,
                 smtp_host=GLSetting.memory_copy.notif_server,
                 smtp_port=GLSetting.memory_copy.notif_port,
                 security=GLSetting.memory_copy.notif_security)
                 
    except Exception as excep:
        # we strongly need to avoid raising exception inside email logic to avoid chained errors
        log.err("Unexpected exception in mail_exception: %s" % excep)

mail_exception.mail_counter = 0

