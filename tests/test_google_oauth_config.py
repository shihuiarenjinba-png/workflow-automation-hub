import json
import tempfile
import unittest
from pathlib import Path

from automation_hub.google_blogger import GoogleBloggerError, load_google_desktop_client_file, validate_google_desktop_client_config


VALID = {
    'installed': {
        'client_id': '1234567890-abcdef.apps.googleusercontent.com',
        'project_id': 'example-project',
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'client_secret': 'not-a-real-secret',
        'redirect_uris': ['http://localhost'],
    }
}


class GoogleOAuthConfigTests(unittest.TestCase):
    def test_valid_desktop_config(self):
        metadata = validate_google_desktop_client_config(VALID)
        self.assertEqual(metadata.project_id, 'example-project')

    def test_rejects_web_application_json(self):
        with self.assertRaises(GoogleBloggerError):
            validate_google_desktop_client_config({'web': dict(VALID['installed'])})

    def test_rejects_remote_redirect(self):
        config = json.loads(json.dumps(VALID))
        config['installed']['redirect_uris'] = ['https://example.com/callback']
        with self.assertRaises(GoogleBloggerError):
            validate_google_desktop_client_config(config)

    def test_loader_rejects_oversized_file(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'client.json'
            path.write_text(' ' * (70 * 1024), encoding='utf-8')
            with self.assertRaises(GoogleBloggerError):
                load_google_desktop_client_file(path)


if __name__ == '__main__':
    unittest.main()
