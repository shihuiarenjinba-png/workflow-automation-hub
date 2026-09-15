from __future__ import annotations

import unittest

from connectors import CONNECTORS


class ConnectorPolicyTests(unittest.TestCase):
    def test_all_connectors_have_explicit_scopes(self) -> None:
        for connector in CONNECTORS.values():
            self.assertTrue(connector.scopes, connector.connector_id)

    def test_drive_uses_narrow_file_scope_only(self) -> None:
        self.assertEqual(
            CONNECTORS["drive"].scopes,
            ("https://www.googleapis.com/auth/drive.file",),
        )

    def test_sheets_uses_narrow_file_scope_only(self) -> None:
        self.assertEqual(
            CONNECTORS["sheets"].scopes,
            ("https://www.googleapis.com/auth/drive.file",),
        )

    def test_gmail_is_send_only(self) -> None:
        self.assertEqual(
            CONNECTORS["gmail_send"].scopes,
            ("https://www.googleapis.com/auth/gmail.send",),
        )

    def test_youtube_is_upload_only(self) -> None:
        self.assertEqual(
            CONNECTORS["youtube_upload"].scopes,
            ("https://www.googleapis.com/auth/youtube.upload",),
        )

    def test_no_broad_drive_scope_is_present(self) -> None:
        blocked = {
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/drive.readonly",
            "https://www.googleapis.com/auth/drive.metadata",
            "https://www.googleapis.com/auth/drive.metadata.readonly",
        }
        for connector in CONNECTORS.values():
            self.assertTrue(blocked.isdisjoint(connector.scopes), connector.connector_id)

    def test_no_restricted_gmail_scope_is_present(self) -> None:
        blocked = {
            "https://mail.google.com/",
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.compose",
            "https://www.googleapis.com/auth/gmail.modify",
            "https://www.googleapis.com/auth/gmail.metadata",
        }
        self.assertTrue(blocked.isdisjoint(CONNECTORS["gmail_send"].scopes))


if __name__ == "__main__":
    unittest.main()
