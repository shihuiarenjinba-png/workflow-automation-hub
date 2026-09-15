# Compliance Notes / 規約・利用条件メモ

Reviewed / 確認日: **2026-09-15**

> This is an engineering compliance checklist, not legal advice. Re-check the current official terms before commercial release.  
> これは開発上の規約確認チェックであり、法的助言ではありません。商用リリース前に最新の公式規約を再確認してください。

## Google Blogger API

**Intended use / 想定用途**

- User explicitly connects their own Google account through OAuth 2.0.
- The app lists blogs/posts the user is authorized to manage.
- The app modifies post content only for user-configured deterministic jobs.
- No scraping and no browser automation are used for Blogger.

- ユーザー自身がOAuth 2.0でGoogleアカウントを明示的に接続します。
- ユーザーに管理権限があるブログ・記事のみ取得します。
- ユーザーが設定した決定論的ジョブに限り記事本文を変更します。
- Bloggerではスクレイピングやブラウザ自動操作を使用しません。

**Scope / 権限**

- `https://www.googleapis.com/auth/blogger` — required for Blogger write operations.
- Do not add unrelated Google scopes unless a feature actually requires them.

**Production requirements / 公開時の注意**

- Follow Google APIs Terms of Service, Google API Services User Data Policy, and OAuth production/verification policies.
- Public production distribution can require OAuth branding/verification and a public privacy policy depending on app configuration and requested scopes.
- Store tokens securely. This project uses Windows DPAPI for the current Windows user.
- The repository never contains an OAuth client secret or refresh token.

**Official references / 公式資料**

- https://developers.google.com/blogger/docs/3.0/using
- https://developers.google.com/resources/api-libraries/documentation/blogger/v3/python/latest/blogger_v3.posts.html
- https://developers.google.com/identity/protocols/oauth2/scopes
- https://developers.google.com/identity/protocols/oauth2/production-readiness/policy-compliance
- https://developers.google.com/identity/verification/authentication-verification
- https://developers.google.com/terms/api-services-user-data-policy

## Windows Task Scheduler

- Use Windows built-in `schtasks.exe` only to register/query/remove this application's own tasks.
- Registered actions are fixed to this application runner plus a sanitized job ID.
- Arbitrary PowerShell, shell commands, or user-supplied executables are not accepted.
- Tasks are registered with `LIMITED` run level by default.

- Windows標準の `schtasks.exe` を、本アプリ自身のタスク登録・確認・削除だけに利用します。
- 登録するActionは本アプリのRunnerと検証済みJob IDに固定します。
- 任意PowerShell、任意シェルコマンド、ユーザー指定EXEの登録機能は提供しません。
- タスクは既定で `LIMITED` 権限として登録します。

**Official references / 公式資料**

- https://learn.microsoft.com/en-us/windows/win32/taskschd/schtasks
- https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks-create

## Connector admission rule / Connector採用基準

A future connector is not production-ready unless all are documented:

1. Official API or officially supported automation interface.
2. Initial setup without a paid API subscription unless clearly labeled otherwise.
3. UI **Connection Test / 接続確認** implemented.
4. Intended commercial use and automation restrictions reviewed against official policies.
5. Least-privilege scopes/permissions.
6. Secrets/tokens excluded from Git.
7. Dry Run or another safe preview for remote writes where practical.
