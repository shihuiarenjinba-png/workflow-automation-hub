from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import keyring
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


KEYRING_SERVICE = "PrivateAutomationHub"


class AuthError(RuntimeError):
    pass


@dataclass(frozen=True)
class StoredConnection:
    connector_id: str
    scopes: tuple[str, ...]


class GoogleAuthStore:
    """Stores OAuth credentials in the OS credential store, never in plaintext files."""

    def _key(self, connector_id: str) -> str:
        return f"google:{connector_id}"

    def connect(self, connector_id: str, client_secrets_file: str | Path, scopes: list[str]) -> Credentials:
        path = Path(client_secrets_file).expanduser().resolve()
        if not path.is_file():
            raise AuthError(f"OAuth client file not found: {path}")

        flow = InstalledAppFlow.from_client_secrets_file(str(path), scopes=scopes)
        credentials = flow.run_local_server(
            host="127.0.0.1",
            port=0,
            open_browser=True,
            authorization_prompt_message="",
            success_message="認証が完了しました。このブラウザ画面は閉じて構いません。",
        )
        self._save(connector_id, credentials)
        return credentials

    def _save(self, connector_id: str, credentials: Credentials) -> None:
        keyring.set_password(KEYRING_SERVICE, self._key(connector_id), credentials.to_json())

    def get(self, connector_id: str, expected_scopes: list[str]) -> Credentials:
        raw = keyring.get_password(KEYRING_SERVICE, self._key(connector_id))
        if not raw:
            raise AuthError("未接続です。先に Google 接続を行ってください。")

        try:
            info = json.loads(raw)
            credentials = Credentials.from_authorized_user_info(info, scopes=expected_scopes)
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            raise AuthError("保存済み認証情報を読み込めません。再接続してください。") from exc

        if credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
            except Exception as exc:
                raise AuthError("Google トークンの更新に失敗しました。再接続してください。") from exc
            self._save(connector_id, credentials)

        if not credentials.valid:
            raise AuthError("Google 認証が無効です。再接続してください。")
        return credentials

    def is_connected(self, connector_id: str) -> bool:
        return bool(keyring.get_password(KEYRING_SERVICE, self._key(connector_id)))

    def disconnect(self, connector_id: str) -> None:
        try:
            keyring.delete_password(KEYRING_SERVICE, self._key(connector_id))
        except keyring.errors.PasswordDeleteError:
            pass
