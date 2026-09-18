# Compliance Notes / 規約・利用条件メモ

Reviewed / 確認日: **2026-09-16**

> This is an engineering compliance checklist, not legal advice. Re-check the current official terms before commercial release.  
> これは開発上の規約確認チェックであり、法的助言ではありません。商用リリース前に最新の公式規約を再確認してください。

## Supported API boundary / 対応API境界

v0.1 implements **Google Blogger API only** as a production connector. A successful credential or HTTP connection does not imply that an arbitrary API can be automated; the app must contain a connector/action that defines the API behavior.

v0.1で正式実装する外部APIは **Google Blogger APIのみ**です。認証情報を入力して疎通できても、動作を実装していない任意APIを自動化できるという意味ではありません。各APIは専用Connector/Actionとして実装し、規約確認後に追加します。

## Google OAuth Desktop client

**Credential model / 認証設定**

- Current release uses Bring Your Own Google OAuth Client.
- User creates an OAuth client with Application type **Desktop app** in Google Cloud.
- The app accepts only the downloaded Desktop app JSON shape (`installed`).
- Web application JSON (`web`) and arbitrary JSON are rejected.
- `auth_uri` and `token_uri` are checked against Google's expected OAuth endpoints.
- Redirect URIs are restricted to local loopback (`localhost`, `127.0.0.1`, `::1`).
- After validation, the OAuth client JSON is encrypted with Windows DPAPI as `google_client.dpapi`.
- Refresh/access credentials are separately encrypted as `google_token.dpapi`.
- The original downloaded JSON path is not required for normal operation after a successful import.
- If a newly imported client has a different Client ID, the old Google token is deleted and reauthorization is required.

**OAuth flow / OAuthフロー**

- Uses the system browser and a local loopback callback.
- Manual copy/paste (OOB) authorization is not implemented.
- Request only the Blogger scope required by current functionality.

**Official references / 公式資料**

- https://developers.google.com/workspace/guides/create-credentials
- https://developers.google.com/identity/protocols/oauth2/native-app
- https://developers.google.com/youtube/v3/guides/auth/installed-apps
- https://developers.google.com/identity/protocols/oauth2/production-readiness/policy-compliance
- https://developers.google.com/terms/api-services-user-data-policy

## Google Blogger API

**Intended use / 想定用途**

- User explicitly connects their own Google account through OAuth 2.0.
- The app lists blogs/posts the user is authorized to manage.
- The app modifies post content only for user-configured deterministic jobs.
- No scraping and no browser automation are used for Blogger.
- A local pre-change backup is created before every live remote patch. If backup creation fails, the remote patch is not sent.
- A per-job lock prevents simultaneous scheduled/manual duplicate execution.

**Scope / 権限**

- `https://www.googleapis.com/auth/blogger` — required for Blogger write operations.
- Do not add unrelated Google scopes unless a feature actually requires them.

**Production requirements / 公開時の注意**

- Follow Google APIs Terms of Service, Google API Services User Data Policy, and OAuth production/verification policies.
- Public production distribution can require OAuth branding/verification and a public privacy policy depending on app configuration and requested scopes.
- Store tokens securely. This project uses Windows DPAPI for the current Windows user.
- The repository never contains a user OAuth client JSON, OAuth client secret file, or refresh token.

**Official references / 公式資料**

- https://developers.google.com/blogger/docs/3.0/using
- https://developers.google.com/identity/protocols/oauth2/scopes
- https://developers.google.com/terms/api-services-user-data-policy

## Windows Task Scheduler

- Use Windows built-in `schtasks.exe` only to register/query/remove this application's own tasks.
- Registered actions are fixed to this application runner plus a strictly validated job ID.
- Unsafe job IDs are rejected rather than rewritten, preventing task-name collisions.
- Arbitrary PowerShell, shell commands, or user-supplied executables are not accepted.
- Tasks are registered with `LIMITED` run level and `/IT` interactive-user execution.
- The app does not store a Windows account password.

**Official references / 公式資料**

- https://learn.microsoft.com/en-us/windows/win32/taskschd/schtasks
- https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks-create

## Connector admission rule / Connector採用基準

A future connector is not production-ready unless all are documented:

1. Official API or officially supported automation interface.
2. Exact supported actions are implemented; credentials alone never imply arbitrary behavior.
3. Initial setup without a paid API subscription unless clearly labeled otherwise.
4. UI **Connection Test / 接続確認** implemented for that connector's real endpoint.
5. Intended commercial use and automation restrictions reviewed against official policies.
6. Least-privilege scopes/permissions.
7. Secrets/tokens excluded from Git and plaintext settings.
8. Dry Run or another safe preview for remote writes where practical.
9. Retry/rate-limit/pagination behavior implemented explicitly when that connector needs it.
10. Unit/regression tests and a release-time terms review date are recorded.
