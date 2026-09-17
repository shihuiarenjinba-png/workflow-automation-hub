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
- [x] `CODE_OPERATOR_HANDOFF.md` defines the Windows/package/Google acceptance boundary

## Code/package operator gates / 実Windows + 実Google + 最終ZIP

- [ ] Build the exact approved branch/commit on Windows and run all tests + source/packaged self-tests
- [ ] Create and inspect the RC/customer ZIP only after build/self-test success
- [ ] Include EXE, required user/setup docs, checklist, dependency/license evidence, `CODE_OPERATOR_HANDOFF.md`, and source-commit release information
- [ ] Scan the package for OAuth JSON, tokens, client secrets, API keys, passwords, and private test data
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
- [ ] Run Windows Defender/AV scan
- [ ] Prepare LICENSE/NOTICE/SBOM and lock dependency versions
- [ ] Perform Google Testing-project → Production-project/new Desktop OAuth JSON → reauthorization migration once
- [ ] Recheck current Google OAuth/Blogger API commercial, verification, privacy-policy, and user-data requirements immediately before sale
- [ ] Record the SHA-256 of the **exact ZIP actually distributed**

## Authenticode / Microsoft signing status / 署名の扱い

- **DEFERRED / NOT VERIFIED for this handoff.** The owner's signing path is currently unavailable.
- Do not mark signing as passed and do not fabricate/bypass signature evidence.
- An unsigned RC may be used for controlled acceptance. If an unsigned customer ZIP is ultimately distributed, disclose that state and expect possible Windows reputation/security warnings.
- If signing becomes available later, sign the exact final binary and regenerate the customer ZIP SHA-256.

This repository is considered **GitHub-side handoff ready**, not sales-approved. Final packaging and real-account/real-Windows acceptance belong to the code/package operator.

mainへ販売版としてマージする判断は、コード担当の実機受入・最終ZIP確定後に行います。
