import time

import re
from twisted.trial import unittest
from globaleaks.utils import utility
from globaleaks.settings import GLSetting


class TestUtility(unittest.TestCase):
    def test_log_encode_html_str(self):
        self.assertEqual(utility.log_encode_html("<"), '&lt;')
        self.assertEqual(utility.log_encode_html(">"), '&gt;')
        self.assertEqual(utility.log_encode_html("'"), '&#39;')
        self.assertEqual(utility.log_encode_html("/"), '&#47;')
        self.assertEqual(utility.log_encode_html("\\"), '&#92;')

        self.assertEqual(utility.log_encode_html("<>'/\\"), '&lt;&gt;&#39;&#47;&#92;')

    def test_log_remove_escapes(self):
        for c in map(chr, range(32)):
            self.assertNotEqual(utility.log_remove_escapes(c), c)

        for c in map(chr, range(127, 140)):
            self.assertNotEqual(utility.log_remove_escapes(c), c)

        start = ''.join(map(chr, range(32))) + ''.join(map(chr, range(127, 140)))

        end = ''
        for c in map(chr, range(32)):
            end += utility.log_remove_escapes(c)

        for c in map(chr, range(127, 140)):
            end += utility.log_remove_escapes(c)

        self.assertEqual(utility.log_remove_escapes(start), end)

    def test_uuid4(self):
        self.assertIsNotNone(re.match(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})',
                                      utility.uuid4()))

    def test_uuid4_debug(self):
        GLSetting.debug_option_UUID_human = "antani"
        self.assertEqual(utility.uuid4(), "antani00-0000-0000-0000-000000000001")
        self.assertEqual(utility.uuid4(), "antani00-0000-0000-0000-000000000002")
        self.assertEqual(utility.uuid4(), "antani00-0000-0000-0000-000000000003")
        self.assertEqual(utility.uuid4(), "antani00-0000-0000-0000-000000000004")
        self.assertEqual(utility.uuid4(), "antani00-0000-0000-0000-000000000005")

    def test_randint(self):
        self.assertEqual(utility.randint(0), 0)
        self.assertEqual(utility.randint(0, 0), 0)
        self.assertEqual(utility.randint(9, 9), 9)

        number = self.assertTrue(utility.randint(1, 2))
        self.assertTrue(0 < number < 3)

    def test_randbits(self):
        self.assertEqual(len(utility.randbits(4)), 0)
        self.assertEqual(len(utility.randbits(8)), 1)
        self.assertEqual(len(utility.randbits(9)), 1)
        self.assertEqual(len(utility.randbits(16)), 2)

    def test_choice(self):
        population = [0, 1, 2, 3, 4, 5]
        self.assertTrue(utility.choice(population) in population)

    def test_shuffle(self):
        ordered = [0, 1, 2, 3, 4, 5]
        shuffle = utility.shuffle(ordered)
        self.assertEqual(len(ordered), len(shuffle))
        for i in ordered:
            self.assertTrue(i in shuffle)

    def test_utc_dynamic_date(self):
        a = utility.utc_dynamic_date(utility.datetime_null())
        b = utility.utc_dynamic_date(utility.datetime_null(), seconds=0, minutes=0, hours=0)
        self.assertTrue(a == b)

        c = utility.utc_dynamic_date(utility.datetime_null(), seconds=121, minutes=120, hours=0)
        d = utility.utc_dynamic_date(utility.datetime_null(), seconds=61, minutes=61, hours=1)
        e = utility.utc_dynamic_date(utility.datetime_null(), seconds=1, minutes=2, hours=2)
        self.assertEqual(c, d)
        self.assertEqual(d, e)

        f = utility.utc_dynamic_date(c, seconds=121, minutes=120, hours=0)
        g = utility.utc_dynamic_date(d, seconds=61, minutes=61, hours=1)
        h = utility.utc_dynamic_date(e, seconds=1, minutes=2, hours=2)
        self.assertEqual(c, d)
        self.assertEqual(d, e)

    def test_utc_past_date(self):
        a = utility.datetime_now()
        b = utility.utc_past_date(seconds=99)
        c = utility.utc_past_date(minutes=99)
        d = utility.utc_past_date(hours=99)
        self.assertTrue(a > b)
        self.assertTrue(b > c)
        self.assertTrue(c > d)

    def test_utc_future_date(self):
        a = utility.datetime_now()
        b = utility.utc_future_date(seconds=99)
        c = utility.utc_future_date(minutes=99)
        d = utility.utc_future_date(hours=99)
        self.assertTrue(a < b)
        self.assertTrue(b < c)
        self.assertTrue(c < d)

    def test_get_future_epoch(self):
        a = time.time()
        b = utility.get_future_epoch(seconds=1)
        c = utility.get_future_epoch(seconds=2)
        d = utility.get_future_epoch(seconds=3)
        self.assertTrue(a < b)
        self.assertTrue(b < c)
        self.assertTrue(c < d)

    def test_is_expired(self):
        self.assertFalse(utility.is_expired(None))
        self.assertTrue(utility.is_expired(utility.datetime_null()))
        self.assertTrue(utility.is_expired(utility.datetime_now()))
        self.assertFalse(utility.is_expired(utility.utc_future_date(seconds=1337)))

    def test_datetime_to_ISO8601_to_datetime_to_dot_dot_dot(self):
        a = utility.datetime_null()
        b = utility.datetime_to_ISO8601(a)
        c = utility.ISO8601_to_datetime(b)
        d = utility.datetime_to_ISO8601(c)
        self.assertTrue(a, c)
        self.assertTrue(b, d)

    def test_datetime_to_pretty_str(self):
        self.assertEqual(utility.datetime_to_pretty_str(None), 'Thursday 01 January 1970 00:00 (UTC)')
        self.assertEqual(utility.datetime_to_pretty_str(utility.datetime_null()),
            'Thursday 01 January 1970 00:00 (UTC)')

    def test_ISO8601_to_pretty_str(self):
        self.assertEqual(utility.ISO8601_to_pretty_str(None), 'Thursday 01 January 1970 00:00 (UTC)')
        self.assertEqual(utility.ISO8601_to_pretty_str('1970-01-01T00:00:00Z'), 'Thursday 01 January 1970 00:00 (UTC)')

    def test_ISO8601_to_pretty_str_tz(self):
        self.assertEqual(utility.ISO8601_to_pretty_str_tz(None, 1), 'Thursday 01 January 1970 01:00')
        self.assertEqual(utility.ISO8601_to_pretty_str_tz(None, 2), 'Thursday 01 January 1970 02:00')
        self.assertEqual(utility.ISO8601_to_pretty_str_tz('1970-01-01T00:00:00Z', 1), 'Thursday 01 January 1970 01:00')
        self.assertEqual(utility.ISO8601_to_pretty_str_tz('1970-01-01T00:00:00Z', 2), 'Thursday 01 January 1970 02:00')

    def test_acquire_bool(self):
        self.assertTrue(utility.acquire_bool('true'))
        self.assertTrue(utility.acquire_bool(u'true'))
        self.assertTrue(utility.acquire_bool(True))
        self.assertFalse(utility.acquire_bool('false'))
        self.assertFalse(utility.acquire_bool(None))
        self.assertFalse(utility.acquire_bool('antani'))

    def test_bytes_to_pretty_str(self):
        self.assertEqual(utility.bytes_to_pretty_str("60000000001"), "60GB")
        self.assertEqual(utility.bytes_to_pretty_str("5000000001"), "5GB")
        self.assertEqual(utility.bytes_to_pretty_str("40000001"), "40MB")
        self.assertEqual(utility.bytes_to_pretty_str("3000001"), "3MB")
        self.assertEqual(utility.bytes_to_pretty_str("20001"), "20KB")
        self.assertEqual(utility.bytes_to_pretty_str("1001"), "1KB")

    def test_log(self):
        utility.log.info("info")
        utility.log.err("err")
        utility.log.debug("debug")
        utility.log.msg("msg")
