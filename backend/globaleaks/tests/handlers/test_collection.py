# -*- coding: utf-8 -*-
import shutil

from twisted.internet.defer import inlineCallbacks
from globaleaks.settings import GLSetting, transact_ro
from globaleaks.tests import helpers
from globaleaks.handlers import collection
from globaleaks.models import ReceiverTip

class TestCollectionDownload(helpers.TestHandlerWithPopulatedDB):
    _handler = collection.CollectionDownload

    @inlineCallbacks
    def setUp(self):
        yield helpers.TestHandlerWithPopulatedDB.setUp(self)
        yield self.perform_full_submission_actions()

    @transact_ro
    def get_rtips(self, store):
        rtips_desc = []
        rtips = store.find(ReceiverTip)
        for rtip in rtips:
            rtips_desc.append({'rtip_id': rtip.id, 'receiver_id': rtip.receiver_id})

        return rtips_desc

    @inlineCallbacks
    def download(self, compression):
        rtips_desc = yield self.get_rtips()

        for rtip_desc in rtips_desc:
            handler = self.request({}, role='receiver')
            handler.current_user.user_id = rtip_desc['receiver_id']
            yield handler.post(rtip_desc['rtip_id'], compression)

    @inlineCallbacks
    def test_post_download_zipstored(self):
        yield self.download('zipstored')

    @inlineCallbacks
    def test_post_download_zipdeflated(self):
        yield self.download('zipdeflated')

    @inlineCallbacks
    def test_post_download_tar(self):
        yield self.download('tar')

    @inlineCallbacks
    def test_post_download_targz(self):
        yield self.download('targz')

    @inlineCallbacks
    def test_post_download_tarbz2(self):
        yield self.download('tarbz2')

    @inlineCallbacks
    def test_post_download_zipstored_with_files_removed_due_to_whatever(self):
        shutil.rmtree(GLSetting.submission_path)
        yield self.download('zipstored')

    @inlineCallbacks
    def test_post_download_zipdeflated_with_files_removed_due_to_whatever(self):
        shutil.rmtree(GLSetting.submission_path)
        yield self.download('zipdeflated')

    @inlineCallbacks
    def test_post_download_tar_with_files_removed_due_to_whatever(self):
        shutil.rmtree(GLSetting.submission_path)
        yield self.download('tar')

    @inlineCallbacks
    def test_post_download_targz_with_files_removed_due_to_whatever(self):
        shutil.rmtree(GLSetting.submission_path)
        yield self.download('targz')

    @inlineCallbacks
    def test_post_download_tarbz2_with_files_removed_due_to_whatever(self):
        shutil.rmtree(GLSetting.submission_path)
        yield self.download('tarbz2')
