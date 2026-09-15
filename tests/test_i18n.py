import unittest

from automation_hub.i18n import tr


class I18nTests(unittest.TestCase):
    def test_both_languages(self):
        self.assertNotEqual(tr('ja', 'tab_jobs'), tr('en', 'tab_jobs'))
        self.assertIn('Workflow', tr('en', 'app_title'))


if __name__ == '__main__':
    unittest.main()
