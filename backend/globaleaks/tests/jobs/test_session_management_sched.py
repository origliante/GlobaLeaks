# -*- coding: utf-8 -*-
from twisted.internet.defer import inlineCallbacks

from globaleaks.tests import helpers
from globaleaks.settings import GLSetting

from globaleaks.handlers import authentication
from globaleaks.jobs import session_management_sched

class TestSessionManagementSched(helpers.TestGL):

    @inlineCallbacks
    def test_session_management_sched(self):

        authentication.GLSession('admin', 'admin', 'enabled') # 1!
        authentication.GLSession('admin', 'admin', 'enabled') # 2!
        authentication.GLSession('admin', 'admin', 'enabled') # 3!

        self.assertEqual(len(GLSetting.sessions), 3)
        authentication.reactor_override.advance(GLSetting.defaults.lifetimes['admin'])
        self.assertEqual(len(GLSetting.sessions), 0)

        yield session_management_sched.SessionManagementSchedule().operation()
