from twisted.internet import reactor

from globaleaks.utils.utility import log
from globaleaks.utils.mailutils import MIME_mail_build, sendmail





def result_debug_callback(ret):
        if type(ret) == type(tuple()):
            num, vals = ret
            sender, code, code_str = vals[0]
            print sender, code, code_str
        return ret



def do_test(notif_server='a.b.c', notif_port=123, notif_security='disabled', notif_username='abc', notif_password='abc'):
    admin_email = 'a@b.c'
    message = 'test'
    notif_source_name = 'a@b.c'
    notif_source_email = 'a@b.c'
    notif_username = notif_username
    notif_password = notif_password

    notif_security = notif_security
    notif_server = notif_server
    notif_port = notif_port


    message = MIME_mail_build(notif_source_name,
                                  notif_source_email,
                                  "Admin",
                                  admin_email,
                                  "ALERT: Anomaly detection",
                                  message)

    res = sendmail( authentication_username=notif_username,
                    authentication_password=notif_password,

                    from_address=notif_source_email,
                    to_address=admin_email,
                    message_file=message,

                    smtp_host=notif_server,
                    smtp_port=notif_port,
                    security=notif_security,
                    event=None,
                    result_debug_callback=result_debug_callback)
    #try:
    #    reactor.run()
    #except: pass
    return res



def send_test(smtp_test_server):
    #Alarm.last_alarm_email = datetime_now()
    notif_server = '1.2.3.444'
    notif_port = 225
    notif_security = 'disabled'
    do_test(notif_server=notif_server, notif_port=notif_port, notif_security=notif_security)


    notif_server = 'jabba.jabba.ugh'
    notif_port = 225
    do_test(notif_server=notif_server, notif_port=notif_port, notif_security=notif_security)


    notif_server = smtp_test_server
    notif_port = 225
    do_test(notif_server=notif_server, notif_port=notif_port, notif_security=notif_security)


    notif_port = 25
    notif_security = 'disabled'
    do_test(notif_server=notif_server, notif_port=notif_port, notif_security=notif_security)

    notif_security = 'SSL'
    do_test(notif_server=notif_server, notif_port=notif_port, notif_security=notif_security)


    notif_security = 'TLS'
    do_test(notif_server=notif_server, notif_port=notif_port, notif_security=notif_security)


    # auth ok
    notif_security = 'disabled'
    do_test(notif_server=notif_server, notif_port=notif_port, notif_security=notif_security, notif_username='mailtest', notif_password='mailtest')



    reactor.callLater(10, reactor.stop)
    reactor.run()


if __name__ == '__main__':
    import sys
    send_test( sys.argv[1] )


