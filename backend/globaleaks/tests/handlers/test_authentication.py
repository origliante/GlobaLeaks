from twisted.internet.defer import inlineCallbacks

from globaleaks.tests import helpers
from globaleaks.handlers import authentication, admin, base
from globaleaks.rest import errors
from globaleaks.settings import GLSetting
from globaleaks.utils import utility

FUTURE = 100


class ClassToTestUnauthenticatedDecorator(base.BaseHandler):
    @authentication.unauthenticated
    def get(self):
        self.set_status(200)
        self.finish("test")


class ClassToTestAuthenticatedDecorator(base.BaseHandler):
    @authentication.authenticated('admin')
    def get(self):
        self.set_status(200)
        self.finish("test")


class TestSessionUpdateOnUnauthRequests(helpers.TestHandlerWithPopulatedDB):
    _handler = ClassToTestUnauthenticatedDecorator

    @inlineCallbacks
    def test_successful_session_update_on_unauth_request(self):
        session = authentication.GLSession('admin', 'admin', 'enabled')
        date1 = session.getTime()
        authentication.reactor_override.advance(FUTURE)
        handler = self.request({}, headers={'X-Session': session.id})
        yield handler.get()
        date2 = GLSetting.sessions[session.id].getTime()
        self.assertEqual(date1 + FUTURE, date2)


class TestSessionUpdateOnAuthRequests(helpers.TestHandlerWithPopulatedDB):
    _handler = ClassToTestAuthenticatedDecorator

    @inlineCallbacks
    def test_successful_session_update_on_auth_request(self):
        session = authentication.GLSession('admin', 'admin', 'enabled')
        date1 = session.getTime()
        authentication.reactor_override.advance(FUTURE)
        handler = self.request({}, headers={'X-Session': session.id})
        yield handler.get()
        date2 = GLSetting.sessions[session.id].getTime()
        self.assertEqual(date1 + FUTURE, date2)


class TestAuthentication(helpers.TestHandlerWithPopulatedDB):
    _handler = authentication.AuthenticationHandler

    @inlineCallbacks
    def test_successful_admin_login(self):
        handler = self.request({
            'username': 'admin',
            'password': 'globaleaks',
            'role': 'admin'
        })
        success = yield handler.post()
        self.assertTrue('session_id' in self.responses[0])
        self.assertEqual(len(GLSetting.sessions.keys()), 1)

    @inlineCallbacks
    def test_accept_admin_login_in_tor2web(self):
        handler = self.request({
            'username': 'admin',
            'password': 'globaleaks',
            'role': 'admin'
        }, headers={'X-Tor2Web': 'whatever'})
        GLSetting.memory_copy.tor2web_admin = True
        success = yield handler.post()
        self.assertTrue('session_id' in self.responses[0])
        self.assertEqual(len(GLSetting.sessions.keys()), 1)

    def test_deny_admin_login_in_tor2web(self):
        handler = self.request({
            'username': 'admin',
            'password': 'globaleaks',
            'role': 'admin'
        }, headers={'X-Tor2Web': 'whatever'})
        GLSetting.memory_copy.tor2web_admin = False
        self.assertFailure(handler.post(), errors.TorNetworkRequired)

    @inlineCallbacks
    def test_successful_receiver_login(self):
        handler = self.request({
            'username': self.dummyReceiver_1['id'],
            'password': helpers.VALID_PASSWORD1,
            'role': 'receiver'
        })
        success = yield handler.post()
        self.assertTrue('session_id' in self.responses[0])
        self.assertEqual(len(GLSetting.sessions.keys()), 1)

    @inlineCallbacks
    def test_accept_receiver_login_in_tor2web(self):
        handler = self.request({
            'username': self.dummyReceiver_1['id'],
            'password': helpers.VALID_PASSWORD1,
            'role': 'receiver'
        }, headers={'X-Tor2Web': 'whatever'})
        GLSetting.memory_copy.tor2web_receiver = True
        yield handler.post()
        self.assertTrue('session_id' in self.responses[0])
        self.assertEqual(len(GLSetting.sessions.keys()), 1)

    def test_deny_receiver_login_in_tor2web(self):
        handler = self.request({
            'username': self.dummyReceiver_1['id'],
            'password': helpers.VALID_PASSWORD1,
            'role': 'receiver'
        }, headers={'X-Tor2Web': 'whatever'})
        GLSetting.memory_copy.tor2web_receiver = False
        yield handler.post()
        self.assertFailure(handler.post(), errors.TorNetworkRequired)

    @inlineCallbacks
    def test_successful_whistleblower_login(self):
        yield self.perform_full_submission_actions()
        handler = self.request({
            'username': '',
            'password': self.dummySubmission['receipt'],
            'role': 'wb'
        })
        yield handler.post()
        self.assertTrue('session_id' in self.responses[0])
        self.assertEqual(len(GLSetting.sessions.keys()), 1)

    @inlineCallbacks
    def test_accept_whistleblower_login_in_tor2web(self):
        yield self.perform_full_submission_actions()
        handler = self.request({
            'username': '',
            'password': self.dummySubmission['receipt'],
            'role': 'wb'
        })
        GLSetting.memory_copy.tor2web_submission = True
        success = yield handler.post()
        self.assertTrue('session_id' in self.responses[0])
        self.assertEqual(len(GLSetting.sessions.keys()), 1)

    def test_deny_whistleblower_login_in_tor2web(self):
        yield self.perform_full_submission_actions()
        handler = self.request({
            'username': '',
            'password': self.dummySubmission['receipt'],
            'role': 'wb'
        }, headers={'X-Tor2Web': 'whatever'})
        GLSetting.memory_copy.tor2web_submission = False
        self.assertFailure(handler.post(), errors.TorNetworkRequired)

    @inlineCallbacks
    def test_successful_admin_logout(self):
        # Login
        handler = self.request({
            'username': 'admin',
            'password': 'globaleaks',
            'role': 'admin'
        })
        yield handler.post()
        self.assertTrue(handler.current_user is None)
        self.assertTrue('session_id' in self.responses[0])
        self.assertEqual(len(GLSetting.sessions.keys()), 1)

        # Logout
        session_id = self.responses[0]['session_id']
        handler = self.request({}, headers={'X-Session': session_id})
        yield handler.delete()
        self.assertTrue(handler.current_user is None)
        self.assertEqual(len(GLSetting.sessions.keys()), 0)

        # A second logout must not be accepted (this validate also X-Session reuse)
        handler = self.request({}, headers={'X-Session': session_id})

        self.assertRaises(errors.NotAuthenticated, handler.delete)

        self.assertTrue(handler.current_user is None)
        self.assertEqual(len(GLSetting.sessions.keys()), 0)

    @inlineCallbacks
    def test_successful_receiver_logout(self):
        # Login
        handler = self.request({
            'username': self.dummyReceiver_1['id'],
            'password': helpers.VALID_PASSWORD1,
            'role': 'receiver'
        })
        yield handler.post()
        self.assertTrue(handler.current_user is None)
        self.assertTrue('session_id' in self.responses[0])
        self.assertEqual(len(GLSetting.sessions.keys()), 1)

        # Logout
        session_id = self.responses[0]['session_id']
        handler = self.request({}, headers={'X-Session': session_id})
        success = yield handler.delete()
        self.assertTrue(handler.current_user is None)
        self.assertEqual(len(GLSetting.sessions.keys()), 0)

        # A second logout must not be accepted (this validate also X-Session reuse)
        handler = self.request({}, headers={'X-Session': session_id})

        self.assertRaises(errors.NotAuthenticated, handler.delete)

        self.assertTrue(handler.current_user is None)
        self.assertEqual(len(GLSetting.sessions.keys()), 0)


    @inlineCallbacks
    def test_successful_whistleblower_logout(self):
        yield self.perform_full_submission_actions()
        handler = self.request({
            'username': '',
            'password': self.dummySubmission['receipt'],
            'role': 'wb'
        })
        yield handler.post()
        self.assertTrue(handler.current_user is None)
        self.assertTrue('session_id' in self.responses[0])
        self.assertEqual(len(GLSetting.sessions.keys()), 1)

        # Logout
        session_id = self.responses[0]['session_id']
        handler = self.request({}, headers={'X-Session': session_id})
        yield handler.delete()
        self.assertTrue(handler.current_user is None)
        self.assertEqual(len(GLSetting.sessions.keys()), 0)

        # A second logout must not be accepted (this validate also X-Session reuse)
        handler = self.request({}, headers={'X-Session': session_id})

        self.assertRaises(errors.NotAuthenticated, handler.delete)

        self.assertTrue(handler.current_user is None)
        self.assertEqual(len(GLSetting.sessions.keys()), 0)

    @inlineCallbacks
    def test_invalid_admin_login_wrong_password(self):
        handler = self.request({
            'username': 'admin',
            'password': 'INVALIDPASSWORD',
            'role': 'admin'
        })

        yield self.assertFailure(handler.post(), errors.InvalidAuthentication)

    @inlineCallbacks
    def test_invalid_receiver_login_wrong_password(self):
        handler = self.request({
            'username': 'scemo',
            'password': 'INVALIDPASSWORD',
            'role': 'receiver'
        })

        yield self.assertFailure(handler.post(), errors.InvalidAuthentication)

    @inlineCallbacks
    def test_invalid_whistleblower_login_wrong_receipt(self):
        handler = self.request({
            'username': '',
            'password': 'INVALIDPASSWORD',
            'role': 'wb'
        })

        yield self.assertFailure(handler.post(), errors.InvalidAuthentication)

    def test_invalid_input_format_missing_role(self):
        handler = self.request({
            'username': '',
            'password': '',
        })

        self.assertFailure(handler.post(), errors.InvalidInputFormat)

    def test_invalid_input_format_wrong_role(self):
        handler = self.request({
            'username': 'ratzinger',
            'password': '',
            'role': 'pope'
        })

        self.assertFailure(handler.post(), errors.InvalidAuthentication)

    @inlineCallbacks
    def test_failed_login_counter(self):
        handler = self.request({
            'username': self.dummyReceiver_1['id'],
            'password': 'INVALIDPASSWORD',
            'role': 'receiver'
        })

        failed_login = 5
        for i in xrange(0, failed_login):
            yield self.assertFailure(handler.post(), errors.InvalidAuthentication)

        receiver_status = yield admin.get_receiver(self.dummyReceiver_1['id'], 'en')
        self.assertEqual(GLSetting.failed_login_attempts, failed_login)

    @inlineCallbacks
    def test_bruteforce_login_protection(self):

        handler = self.request({
            'username': self.dummyReceiver_1['id'],
            'password': 'INVALIDPASSWORD',
            'role': 'receiver'
        })

        sleep_list = []

        def fake_deferred_sleep(seconds):
            sleep_list.append(seconds)

        utility.deferred_sleep = fake_deferred_sleep

        failed_login = 7
        for i in xrange(0, failed_login):
            yield self.assertFailure(handler.post(), errors.InvalidAuthentication)

        receiver_status = yield admin.get_receiver(self.dummyReceiver_1['id'], 'en')

        self.assertEqual(GLSetting.failed_login_attempts, failed_login)

        # validate incremental delay
        self.assertTrue(len(sleep_list), failed_login)
        for i in xrange(1, len(sleep_list)):
            self.assertTrue(i <= sleep_list[i])
