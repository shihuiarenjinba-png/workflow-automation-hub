# Workflow Automation Hub

Windows向けの**決定論的・ローカル優先**自動化デスクトップアプリです。AI/LLMに処理判断を任せず、ユーザーが指定したルールだけを実行します。  
A **deterministic, local-first** Windows automation desktop app. It does not delegate workflow decisions to an AI/LLM; it executes only user-configured rules.

## v0.1 — Blogger Automation Pack integrated

v0.1で正式対応する外部APIは **Google Blogger APIのみ**です。接続確認もBlogger API専用で、任意APIを入力すれば任意処理を実行できる汎用APIクライアントではありません。将来のAPIは、それぞれ専用Connector・Action・規約確認・接続確認を実装してから追加します。  
The only production connector in v0.1 is **Google Blogger API**. Its Connection Test is Blogger-specific; this is not a generic client that can automate an arbitrary API without an implemented connector/action.

- 日本語 / English UI
- Google OAuth 2.0 Desktop flow
- **Google OAuth Desktop app JSON only** — strict format validation
- OAuth client config + refresh token encrypted with Windows DPAPI
- Blogger API 接続確認 / Blogger API connection test
- 管理可能ブログ一覧 / list manageable blogs
- Blogger内部リンク自動挿入 / deterministic Blogger internal-link insertion
- 同一URL重複防止 / duplicate-URL protection
- Dry Run
- 実更新前のローカル記事バックアップ / local pre-write Blogger backup
- 同一ジョブ二重実行防止 / duplicate-run lock
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
  google_client.dpapi
  google_token.dpapi
  logs\audit.jsonl
  backups\blogger\*.json
  locks\*.lock
```

- `google_client.dpapi`: Googleから取得したDesktop app OAuth JSONを検証後、Windows DPAPIで暗号化インポートしたもの。
- `google_token.dpapi`: Google OAuth access/refresh credentialをWindows DPAPIで暗号化したもの。
- `settings.json`: 言語やClient IDの表示用ヒントなど**非秘密情報のみ**。API key/token等の任意secretは保存しません。
- Bloggerを実更新する場合、元HTMLを `backups\blogger` に保存してからAPI patchを実行します。バックアップ保存に失敗した場合は更新しません。

The original Google JSON file is needed only for import/re-import. After a successful import, normal operation does not depend on its original path.

## Google setup / Google初期設定

現在は **Bring Your Own Google OAuth Client** 方式です。利用者自身がGoogle Cloudで所定のDesktop app OAuth clientを作成します。

1. Google CloudでBlogger APIを有効化します。
2. OAuth clientのApplication typeを **Desktop app** にして作成します。
3. GoogleからJSON credentialsをダウンロードします。
4. アプリの `Google / Blogger` 画面で **OAuth JSONをインポート**します。
5. アプリは次を検証します。
   - `installed` 形式であること
   - Google OAuth client ID形式であること
   - Google公式 `auth_uri` / `token_uri` であること
   - redirect URIがlocalhost / loopbackであること
6. 検証に成功したJSONだけをDPAPIへ暗号化保存します。Web application用JSON、任意JSON、外部redirectは拒否します。
7. **Googleに接続 / Connect Google** を押します。
8. **接続確認 / Connection Test** でBlogger APIまで実通信を確認します。

Desktop apps use the system browser and a local loopback redirect. Manual copy/paste OAuth is not used.

Public/commercial distribution can trigger additional OAuth production requirements. See `COMPLIANCE.md` before release.

## Blogger automation / Blogger自動化

ジョブごとに Blog、検索文字、リンク文字、リンクURL、最大確認記事数を設定します。記事HTMLの通常テキストを確認し、最初の一致部分へリンクを1回だけ挿入します。`a`, `script`, `style`, `code`, `pre`, `textarea` の**配下全体**は変更しません。同じURLが記事内に既にある場合、その記事は変更しません。

同じジョブがWindows Schedulerと手動実行で同時に開始されても、ロックにより二重実行を拒否します。異常終了後に残った古いロックは一定時間後に回復可能です。

**最初にDry Runを実行してください。 / Always run Dry Run first.**

## Windows scheduling / Windowsスケジュール

GUIからDaily / Weekly / Windows logonを設定し、Windows標準 `schtasks.exe` へ登録します。

- Run level: `LIMITED`
- Interactive-user only: `/IT`
- Task action: this application only
- Argument: validated `--run-job <job-id>` only
- Job ID: `[A-Za-z0-9_.-]`, 1–64 chars only; unsafe IDs are rejected rather than rewritten
- No arbitrary shell/PowerShell command configuration
- Windowsアカウントのパスワードをアプリへ保存しません / the app does not store the Windows account password

初版ではユーザーがWindowsへログオン中のときだけ実行します。PCにログオンしていない状態での無人実行は対象外です。  
The first release runs scheduled jobs only while the user is logged on; logged-out unattended execution is intentionally out of scope.

アプリを移動すると既存タスクのEXEパスが古くなるため、移動後はスケジュールを再登録してください。  
If the EXE is moved, re-register schedules so Windows receives the new executable path.

## Failure handling / 破損・失敗時

- `settings.json` が破損している場合、元ファイルを `settings.json.corrupt-*` として隔離し、既定値で起動します。
- `jobs.json` が不正な場合は勝手に初期化せず、読み込みエラーとして停止して内容消失を防ぎます。
- settings/jobs/DPAPI payload/Blogger backupは可能な範囲で一時ファイルからの置換を使い、途中書き込みを避けます。
- OAuth Client IDを別のものへ差し替えた場合、古いGoogle tokenは自動削除し、再認証を要求します。

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
3. Fixed connector behavior; an API credential alone does not define an action
4. Google OAuth Desktop app JSON is strictly validated before import
5. OAuth client config and tokens encrypted with Windows DPAPI
6. Dry Run before remote writes
7. Local backup before each live Blogger patch
8. Duplicate execution lock per job
9. Blogger uses the official API, not scraping
10. Every production connector must expose a Connector-specific Connection Test
11. Connector policy/commercial-use review is required before release

See `COMPLIANCE.md` for current policy notes. / 規約確認は `COMPLIANCE.md` を参照してください。
