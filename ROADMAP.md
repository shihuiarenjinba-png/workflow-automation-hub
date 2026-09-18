# Roadmap / ロードマップ

## v0.1 — Desktop Blogger Automation（実装済み / Implemented）

- 日本語 / English desktop GUI
- Google OAuth 2.0 Desktop Flow
- Blogger API Connection Test / 接続確認
- Windows DPAPI token storage
- automatic access-token refresh
- Blogger blog/post listing
- deterministic internal-link insertion
- duplicate-link prevention
- Dry Run before remote write
- local original-post backup before every live Blogger patch
- audit log under LocalAppData
- Windows Task Scheduler Connection Test
- Daily / Weekly / Windows logon scheduling
- `LIMITED` + interactive-user (`/IT`) scheduling
- fixed runner + sanitized job ID only
- Windows GitHub Actions test + PyInstaller EXE build

## v0.1 Release Candidate Gate / リリース候補確認

コード側で実施済み:

- unit tests
- Windows dependency installation
- Windows unit-test execution
- Windows DPAPI encrypt/decrypt round-trip test
- Blogger backup-before-patch regression tests
- PyInstaller EXE build
- build artifact generation
- secret-file `.gitignore` rules
- connector compliance notes

実アカウント・販売前に必要:

- 実際のGoogle OAuth Desktop client JSONで接続確認
- ユーザー自身のBloggerでDry Run
- テスト記事1件でcontrolled live update
- 生成されたローカルbackupの内容確認
- Windows 10 / Windows 11 smoke test
- malware / AV scan
- Authenticode signing before commercial distribution
- signing後SHA256記録
- Google OAuth consent/branding/verification/privacy-policy requirementsの最終確認

## v0.2 — Safety & Preview

- 記事ごとの変更前/変更後preview
- backup一覧・GUI restore support
- per-post allow/skip selection
- richer deterministic match rules
- rollback workflow

## v0.3 — Additional Connectors

Connector採用条件を満たしたものだけ追加:

- Google Drive
- Google Sheets
- YouTube management features that comply with YouTube API policies
- other official APIs with free initial setup and commercial-use review

全Connectorに以下を必須化:

- Connection Test / 接続確認
- official API/supported interface
- least privilege
- commercial/automation policy review
- secure token/secret handling
- Dry Run where practical

## Future Core

- folder trigger integration
- workflow templates
- import/export
- step retry / timeout policies
- result summary / notifications
- signed installer/update path

## Principle / 原則

**判断させない。条件を定義する。 / Define conditions; do not delegate operational decisions to AI.**
