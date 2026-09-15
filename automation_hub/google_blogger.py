from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .storage import DPAPITokenVault

BLOGGER_SCOPE = "https://www.googleapis.com/auth/blogger"
SCOPES = [BLOGGER_SCOPE]


class GoogleBloggerError(RuntimeError):
    pass


@dataclass
class ConnectionResult:
    ok: bool
    blogs: list[dict[str, str]]
    detail: str = ""


class GoogleBloggerConnector:
    def __init__(self, credentials_file: Path, vault: DPAPITokenVault | None = None) -> None:
        self.credentials_file = credentials_file.expanduser().resolve()
        self.vault = vault or DPAPITokenVault()

    def authenticate(self, locale: str = "ja") -> Credentials:
        if not self.credentials_file.is_file():
            raise GoogleBloggerError(f"OAuth credentials file not found: {self.credentials_file}")
        flow = InstalledAppFlow.from_client_secrets_file(str(self.credentials_file), SCOPES)
        success = "Authentication completed. You may close this window." if locale == "en" else "認証が完了しました。このウィンドウを閉じて構いません。"
        credentials = flow.run_local_server(
            port=0,
            open_browser=True,
            access_type="offline",
            prompt="consent",
            success_message=success,
        )
        self.vault.save_text(credentials.to_json())
        return credentials

    def disconnect(self) -> None:
        self.vault.delete()

    def _load_credentials(self) -> Credentials:
        raw = self.vault.load_text()
        if not raw:
            raise GoogleBloggerError("Google account is not authenticated")
        info = json.loads(raw)
        credentials = Credentials.from_authorized_user_info(info, SCOPES)
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            self.vault.save_text(credentials.to_json())
        if not credentials.valid:
            raise GoogleBloggerError("Google credentials are not valid; reconnect the account")
        return credentials

    def _service(self):
        return build("blogger", "v3", credentials=self._load_credentials(), cache_discovery=False)

    def check_connection(self) -> ConnectionResult:
        try:
            response = self._service().blogs().listByUser(userId="self").execute(num_retries=2)
            blogs = [
                {"id": str(item.get("id", "")), "name": str(item.get("name", "")), "url": str(item.get("url", ""))}
                for item in response.get("items", [])
            ]
            return ConnectionResult(True, blogs, "ok")
        except (HttpError, OSError, ValueError) as exc:
            raise GoogleBloggerError(str(exc)) from exc

    def list_blogs(self) -> list[dict[str, str]]:
        return self.check_connection().blogs

    def list_posts(self, blog_id: str, status: str = "LIVE", max_posts: int = 50) -> list[dict[str, Any]]:
        service = self._service()
        collected: list[dict[str, Any]] = []
        page_token: str | None = None
        remaining = max(1, min(int(max_posts), 500))
        while remaining > 0:
            batch = min(remaining, 50)
            request = service.posts().list(blogId=blog_id, status=[status], maxResults=batch, fetchBodies=True, pageToken=page_token)
            response = request.execute(num_retries=2)
            items = response.get("items", [])
            collected.extend(items[:remaining])
            remaining -= len(items[:remaining])
            page_token = response.get("nextPageToken")
            if not page_token or not items:
                break
        return collected

    def patch_post_content(self, blog_id: str, post_id: str, content: str) -> dict[str, Any]:
        try:
            return self._service().posts().patch(blogId=blog_id, postId=post_id, body={"content": content}, fetchBody=False).execute(num_retries=2)
        except HttpError as exc:
            raise GoogleBloggerError(str(exc)) from exc
