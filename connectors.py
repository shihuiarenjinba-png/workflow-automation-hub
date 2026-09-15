from __future__ import annotations

import json
import platform
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Callable

from google.oauth2.credentials import Credentials


class ConnectorError(RuntimeError):
    pass


@dataclass(frozen=True)
class ConnectorSpec:
    connector_id: str
    label: str
    scopes: tuple[str, ...]
    cost_note: str
    commercial_status: str
    risk_note: str
    resource_prompt: str | None = None
    test_mode: str = "api"


CONNECTORS: dict[str, ConnectorSpec] = {
    "blogger": ConnectorSpec(
        connector_id="blogger",
        label="Blogger",
        scopes=("https://www.googleapis.com/auth/blogger",),
        cost_note="標準利用は Google API の割り当て内で利用。",
        commercial_status="条件付き可",
        risk_note="Google API ToS / User Data Policy / OAuth審査に従う。",
    ),
    "drive": ConnectorSpec(
        connector_id="drive",
        label="Google Drive",
        scopes=("https://www.googleapis.com/auth/drive.file",),
        cost_note="標準利用は追加料金なし（割り当て超過課金方針に注意）。",
        commercial_status="用途制限あり",
        risk_note="drive.file限定。一般的な『Driveへのバックアップ製品』用途は既定で無効。",
    ),
    "sheets": ConnectorSpec(
        connector_id="sheets",
        label="Google Sheets",
        scopes=("https://www.googleapis.com/auth/drive.file",),
        cost_note="標準利用は追加料金なし（割り当て超過課金方針に注意）。",
        commercial_status="条件付き可",
        risk_note="ユーザーがアプリに明示共有したファイルのみを扱う。",
        resource_prompt="接続確認する Spreadsheet ID（空欄ならOAuth権限のみ確認）",
    ),
    "gmail_send": ConnectorSpec(
        connector_id="gmail_send",
        label="Gmail（送信のみ）",
        scopes=("https://www.googleapis.com/auth/gmail.send",),
        cost_note="標準利用は追加料金なし（割り当て超過課金方針に注意）。",
        commercial_status="審査前提",
        risk_note="gmail.sendはセンシティブスコープ。公開商用版はOAuth確認が必要。",
        test_mode="scope",
    ),
    "youtube_upload": ConnectorSpec(
        connector_id="youtube_upload",
        label="YouTube（アップロード）",
        scopes=("https://www.googleapis.com/auth/youtube.upload",),
        cost_note="無料の既定割り当てあり。追加割り当てには監査が必要。",
        commercial_status="厳格条件付き",
        risk_note="アップロード等はユーザーの事前の具体的・明示的同意が必要。",
        test_mode="scope",
    ),
}


def _get_json(url: str, access_token: str, timeout: float = 15.0) -> dict:
    request = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read(1_000_000)
    except urllib.error.HTTPError as exc:
        detail = exc.read(2048).decode("utf-8", errors="replace")
        raise ConnectorError(f"HTTP {exc.code}: {detail[:500]}") from exc
    except urllib.error.URLError as exc:
        raise ConnectorError(f"接続エラー: {exc.reason}") from exc
    try:
        return json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ConnectorError("API応答がJSONではありません。") from exc


def _token_scopes(credentials: Credentials) -> set[str]:
    token = urllib.parse.quote(credentials.token or "", safe="")
    if not token:
        raise ConnectorError("アクセストークンがありません。")
    info = _get_json(f"https://oauth2.googleapis.com/tokeninfo?access_token={token}", credentials.token or "")
    raw_scope = str(info.get("scope", ""))
    return {item for item in raw_scope.split() if item}


def _test_scope(spec: ConnectorSpec, credentials: Credentials, _: str | None = None) -> str:
    granted = _token_scopes(credentials)
    missing = [scope for scope in spec.scopes if scope not in granted]
    if missing:
        raise ConnectorError(f"必要スコープが不足しています: {', '.join(missing)}")
    return "OAuthトークンと必要スコープを確認しました（書き込み操作は実行していません）。"


def _test_blogger(_: ConnectorSpec, credentials: Credentials, __: str | None = None) -> str:
    data = _get_json("https://www.googleapis.com/blogger/v3/users/self", credentials.token or "")
    name = data.get("displayName") or data.get("id") or "self"
    return f"Blogger API 接続成功: {name}"


def _test_drive(_: ConnectorSpec, credentials: Credentials, __: str | None = None) -> str:
    fields = urllib.parse.quote("user(displayName,emailAddress)", safe="(),")
    data = _get_json(f"https://www.googleapis.com/drive/v3/about?fields={fields}", credentials.token or "")
    user = data.get("user") or {}
    name = user.get("displayName") or user.get("emailAddress") or "Drive user"
    return f"Drive API 接続成功: {name}"


def _test_sheets(spec: ConnectorSpec, credentials: Credentials, spreadsheet_id: str | None = None) -> str:
    if not spreadsheet_id:
        return _test_scope(spec, credentials)
    sid = urllib.parse.quote(spreadsheet_id.strip(), safe="")
    data = _get_json(
        f"https://sheets.googleapis.com/v4/spreadsheets/{sid}?fields=spreadsheetId,properties.title",
        credentials.token or "",
    )
    title = ((data.get("properties") or {}).get("title")) or data.get("spreadsheetId") or "Spreadsheet"
    return f"Sheets API 接続成功: {title}"


def test_google_connector(spec: ConnectorSpec, credentials: Credentials, resource_id: str | None = None) -> str:
    if spec.test_mode == "scope":
        return _test_scope(spec, credentials, resource_id)
    handlers: dict[str, Callable[[ConnectorSpec, Credentials, str | None], str]] = {
        "blogger": _test_blogger,
        "drive": _test_drive,
        "sheets": _test_sheets,
    }
    handler = handlers.get(spec.connector_id)
    if handler is None:
        raise ConnectorError(f"接続確認が未実装です: {spec.connector_id}")
    return handler(spec, credentials, resource_id)


def test_windows_task_scheduler() -> str:
    if platform.system() != "Windows":
        raise ConnectorError("Windows Task Scheduler は Windows 上でのみ利用できます。")
    try:
        import win32com.client  # type: ignore
    except ImportError as exc:
        raise ConnectorError("pywin32 が未インストールです。requirements.txt を確認してください。") from exc

    try:
        service = win32com.client.Dispatch("Schedule.Service")
        service.Connect()
        root = service.GetFolder("\\")
        _ = root.Name
    except Exception as exc:
        raise ConnectorError(f"Task Scheduler への接続に失敗しました: {exc}") from exc
    return "Windows Task Scheduler 2.0 への読み取り接続に成功しました。"
