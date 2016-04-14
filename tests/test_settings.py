import unittest

__author__ = 'pahaz'


class SettingsTestCase(unittest.TestCase):
    def test_get_debug_setting(self):
        from minidjango.conf import settings
        self.assertEqual(settings.DEBUG, False)

    def test_missed_setting(self):
        from minidjango.conf import settings
        with self.assertRaises(AttributeError):
            self.assertTrue(settings.FOOOBAAAR)
