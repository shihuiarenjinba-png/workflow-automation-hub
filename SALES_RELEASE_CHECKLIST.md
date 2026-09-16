# Sales release checklist / 販売直前チェック

## Automated / code gates

- [x] Japanese / English i18n resources
- [x] Persistent locale setting
- [x] Explicit **`言語 / Language`** selector in both locales
- [x] Desktop OAuth JSON strict validation
- [x] OAuth config/token protected with Windows DPAPI
- [x] Blogger connection test uses official API
- [x] Dry Run available before live mutation
- [x] Local backup required before live Blogger patch
- [x] Duplicate-link prevention and deterministic HTML insertion
- [x] Per-job lock and audit log
- [x] Task Scheduler uses fixed runner, LIMITED + interactive user; no arbitrary command scheduling
- [x] Redirect hardening regression test for HTTP helper
- [x] Source and packaged EXE self-test gate

## Real Windows + real Google account gates

- [ ] Windows 10 smoke test
- [ ] Windows 11 smoke test
- [ ] Switch 日本語 → English → 日本語; restart and confirm the locale is retained
- [ ] Check 100%, 125%, and 150% display scaling for clipped labels/buttons
- [ ] Import a real Google **Desktop app** OAuth JSON and verify DPAPI persistence after restart
- [ ] Authorize a dedicated test Google account and run Blogger Connection Test
- [ ] Verify a wrong Web-application JSON and malformed JSON are rejected clearly in both languages
- [ ] Run Dry Run against a controlled test blog and confirm no remote write occurs
- [ ] Run one controlled live Blogger update; verify the local pre-write backup exists and the expected post changed once
- [ ] Simulate backup failure and verify the Blogger patch is not sent
- [ ] Verify duplicate-link prevention and an entity/HTML edge case on controlled posts
- [ ] Register Daily, Weekly, and Logon schedules on Windows; inspect Task Scheduler properties
- [ ] Verify a disabled job cannot be registered/run by the scheduler
- [ ] Verify two concurrent/manual starts of the same job are blocked by the job lock
- [ ] Inspect `%LOCALAPPDATA%\WorkflowAutomationHub\` permissions/data and confirm no plaintext OAuth token/client JSON
- [ ] Verify audit logs redact credentials/Bearer/API-key-like values
- [ ] Build the packaged EXE from a path containing spaces/non-ASCII characters; packaged self-test must pass
- [ ] Run Windows Defender/AV scan and record the final artifact SHA-256
- [ ] Prepare LICENSE/NOTICE/SBOM and lock dependency versions
- [ ] Perform Google Testing-project → Production-project/new Desktop OAuth JSON → reauthorization migration once
- [ ] Recheck current Google OAuth/Blogger API commercial, verification, privacy-policy, and user-data requirements immediately before sale
- [ ] Authenticode-sign the final installer/executable if commercially distributed

Do not merge/release as a commercial build until every applicable unchecked item is completed on a controlled Windows machine/account.

未チェック項目が残っている間は販売完成扱いにしません。
