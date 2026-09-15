# Workflow Automation Hub

Windows向けの**決定論的・ローカル優先**自動化デスクトップアプリです。AI/LLMに処理判断を任せず、ユーザーが指定したルールだけを実行します。  
A **deterministic, local-first** Windows automation desktop app. It does not delegate workflow decisions to an AI/LLM; it executes only user-configured rules.

## v0.1 — Blogger Automation Pack integrated

- 日本語 / English UI
- Google OAuth 2.0 Desktop flow
- OAuth JSONファイル選択 / OAuth JSON file picker
- Refresh tokenをWindows DPAPIで暗号化保存 / refresh-token storage encrypted with Windows DPAPI
- Blogger API 接続確認 / Blogger API connection test
- 管理可能ブログ一覧 / list manageable blogs
- Blogger内部リンク自動挿入 / deterministic Blogger internal-link insertion
- 同一URL重複防止 / duplicate-URL protection
- Dry Run
- 実更新前のローカル記事バックアップ / local pre-write Blogger backup
- 実行監査ログ / audit log
- Windows Task Scheduler 接続確認・登録・削除
- Daily / Weekly / Windows logon scheduling
- 固定Runnerのみ登録。任意コマンド実行なし / fixed runner only; no arbitrary command execution

## Data location / データ保存場所

`WorkflowAutomationHub.exe` はデスクトップに置けます。認証情報や設定はEXEの隣には保存しません。  
The EXE may be kept on Desktop. Credentials and settings are not stored next to the EXE.

```text
%LOCALAPPDATA%\WorkflowAutomationHub\
  settings.json
  jobs.json
  google_token.dpapi
  logs\audit.jsonl
  backups\blogger\*.json
```

`google_token.dpapi` は現在のWindowsユーザーに紐づくDPAPI暗号化データです。Bloggerを実更新する場合、変更対象記事の元HTMLを `backups\blogger` に保存してからAPI patchを実行します。バックアップ保存に失敗した場合は、その記事を更新しません。  
`google_token.dpapi` is protected by Windows DPAPI for the current user. Before a live Blogger patch, the original post HTML is saved under `backups\blogger`; if backup creation fails, the remote post is not patched.

## Google setup / Google初期設定

1. Google CloudでBlogger APIを有効化します。
2. OAuth client type **Desktop app** を作成します。
3. JSON credentialsをダウンロードします。
4. アプリの `Google / Blogger` 画面でJSONファイルを選択します。
5. **Googleに接続 / Connect Google** を押します。
6. **接続確認 / Connection Test** でBlogger APIまで実通信を確認します。

Public/commercial distribution can trigger additional OAuth production requirements. See `COMPLIANCE.md` before release.

## Blogger automation / Blogger自動化

ジョブごとに Blog、検索文字、リンク文字、リンクURL、最大確認記事数を設定します。記事HTMLの通常テキストを確認し、最初の一致部分へリンクを1回だけ挿入します。`a`, `script`, `style`, `code`, `pre`, `textarea` 内は変更しません。同じURLが記事内に既にある場合、その記事は変更しません。

**最初にDry Runを実行してください。 / Always run Dry Run first.**

## Windows scheduling / Windowsスケジュール

GUIからDaily / Weekly / Windows logonを設定し、Windows標準 `schtasks.exe` へ登録します。

- Run level: `LIMITED`
- Interactive-user only: `/IT`
- Task action: this application only
- Argument: sanitized `--run-job <job-id>` only
- No arbitrary shell/PowerShell command configuration
- Windowsアカウントのパスワードをアプリへ保存しません / the app does not store the Windows account password

初版ではユーザーがWindowsへログオン中のときだけ実行します。PCにログオンしていない状態での無人実行は対象外です。  
The first release runs scheduled jobs only while the user is logged on; logged-out unattended execution is intentionally out of scope.

アプリを移動すると既存タスクのEXEパスが古くなるため、移動後はスケジュールを再登録してください。  
If the EXE is moved, re-register schedules so Windows receives the new executable path.

## Development / 開発

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python desktop_app.py
python -m unittest discover -s tests -v
```

## Windows EXE build / EXEビルド

```powershell
powershell -ExecutionPolicy Bypass -File .\build_windows.ps1
```

GitHub Actionsの `Windows build / Windowsビルド` でもWindows EXEをArtifactとして生成します。

## Security principles / セキュリティ原則

1. No AI decision engine / AI判断エンジンなし
2. No arbitrary command scheduler / 任意コマンドのスケジュール登録なし
3. OAuth tokens encrypted with Windows DPAPI
4. Dry Run before remote writes
5. Local backup before each live Blogger patch
6. Blogger uses the official API, not scraping
7. Every production connector must expose a Connection Test
8. Connector policy/commercial-use review is required before release

See `COMPLIANCE.md` for current policy notes. / 規約確認は `COMPLIANCE.md` を参照してください。
