# Roadmap

## Phase 1 — Deterministic Core（現在）

- file copy / move / write
- HTTPS API action
- `base_dir` path boundary
- host allowlist
- Dry Run
- audit log
- default no-overwrite

## Phase 2 — Workflow機能

- Condition（拡張子、存在確認、文字列一致）
- step output variables
- per-step retry / timeout
- workflow result summary
- schema validation

## Phase 3 — Google / Blogger

- Google OAuth Desktop Flow
- OS secure credential storage
- automatic access-token refresh
- Blogger posts list / insert / patch / publish Connector
- duplicate-link prevention
- internal-link rule templates

## Phase 4 — GUI / Packaging

- Windows GUI configuration
- workflow templates
- import/export
- signed Windows build

## Release Gate

販売版にする前に、unit test、fixture regression、通信監査、秘密情報監査、Windows 10/11 smoke test、署名後ハッシュ確認を行う。
