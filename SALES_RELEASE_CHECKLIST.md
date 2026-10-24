# Sales release checklist / 販売直前チェック

## Automated / code gates

- [x] Japanese / English i18n resources
- [x] Persistent locale setting
- [x] Explicit 言語 / Language selector in both locales
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
- [x] Privacy-safe --diagnose support report; no credential contents, username, hostname, or full paths
- [x] One-click 02_SUPPORT_DIAGNOSTICS.bat customer support path
- [x] Package MANIFEST_SHA256.txt + VERIFY_FILES.ps1 verifies every distributed file
- [x] `package_release.ps1` verifies a staged ZIP manifest, extracted EXE self-test, and diagnostics when packaging is permitted
- [x] `package_release.ps1` fails closed for RC and Sales modes without a product LICENSE, committed NOTICE/SBOM/lock, and (for Sales) exact-commit manual acceptance
- [x] CODE_OPERATOR_HANDOFF.md defines the Windows/package/Google acceptance boundary

## Code/package operator gates / 実Windows + 実Google + 商用ZIP

- [x] GitHub Actions builds the exact PR head with the committed SHA-256 dependency lock; ZIP generation is disabled until legal gates are complete
- [ ] After the product LICENSE is approved, generate one RC ZIP and compare the outer SHA-256 with its sidecar
- [ ] On the owner's Windows machine, fully extract that exact RC ZIP and run VERIFY_FILES.ps1
- [ ] Run 02_SUPPORT_DIAGNOSTICS.bat and retain a privacy-safe support_report.txt as acceptance evidence
- [ ] Scan the exact RC/customer package for OAuth JSON, tokens, client secrets, API keys, passwords, and private test data
- [ ] Windows 10 smoke test if Windows 10 is claimed as supported
- [ ] Windows 11 owner-machine smoke test
- [ ] Switch 日本語 → English → 日本語; restart and confirm the locale is retained
- [ ] Check 100%, 125%, and 150% display scaling for clipped labels/buttons
- [ ] Import a real Google Desktop app OAuth JSON and verify DPAPI persistence after restart
- [ ] Authorize a dedicated test Google account and run Blogger Connection Test
- [ ] Verify a wrong Web-application JSON and malformed JSON are rejected clearly in both languages
- [ ] Run Dry Run against a controlled test blog and confirm no remote write occurs
- [ ] Run one controlled live Blogger update; verify the local pre-write backup exists and the expected post changed once
- [ ] Simulate backup failure and verify the Blogger patch is not sent
- [ ] Verify duplicate-link prevention and an entity/HTML edge case on controlled posts
- [ ] Register Daily, Weekly, and Logon schedules on Windows; inspect Task Scheduler properties
- [ ] Verify a disabled job cannot be registered/run by the scheduler
- [ ] Verify two concurrent/manual starts of the same job are blocked by the job lock
- [ ] Inspect %LOCALAPPDATA%\WorkflowAutomationHub\ permissions/data and confirm no plaintext OAuth token/client JSON
- [ ] Verify audit logs redact credentials/Bearer/API-key-like values
- [ ] Build the packaged EXE from a path containing spaces/non-ASCII characters; packaged self-test must pass
- [ ] Run Windows Defender/AV scan on the exact candidate ZIP/EXE
- [ ] Add the owner-approved product `LICENSE` (no license has been selected yet)
- [x] Generate `THIRD_PARTY_NOTICES.md` with dependency license/NOTICE text
- [x] Generate and validate CycloneDX 1.6 `SBOM.cyclonedx.json`
- [x] Pin build/runtime dependencies and SHA-256 hashes in `requirements-lock.txt`; enforce it in local/CI builds
- [ ] Obtain the owner/legal review of the exact packaged dependency notices before packaging
- [ ] Perform Google Testing-project → Production-project/new Desktop OAuth JSON → reauthorization migration once
- [ ] Recheck current Google OAuth/Blogger API commercial, verification, privacy-policy, and user-data requirements immediately before sale
- [ ] Create SALES_RELEASE_APPROVED.txt for the exact accepted source commit with manual_acceptance=PASS
- [ ] Run package_release.ps1 -Mode Sales against that exact commit and record the SHA-256 of the exact ZIP actually distributed

## Authenticode / Microsoft signing status / 署名の扱い

- DEFERRED / NOT VERIFIED for this handoff. The owner's signing path is currently unavailable.
- Do not mark signing as passed and do not fabricate/bypass signature evidence.
- An unsigned RC may be used for controlled acceptance. If an unsigned customer ZIP is ultimately distributed, disclose that state and expect possible Windows reputation/security warnings.
- If signing becomes available later, sign the exact final binary and regenerate the customer ZIP SHA-256.

The repository does not generate a ZIP automatically. ZIP creation is fail-closed until the formal product LICENSE, committed dependency evidence, owner-machine/real-Google acceptance, and exact-commit approval gates are completed.

mainへ販売版としてマージする判断は、上記の商用ゲート完了後に行います。

## Beginner GUI and recurring-write approval gates (2026-10-18 branch)

The following items are **new acceptance gates**, not a declaration of a
passed Windows release. Existing checked items above describe the older
base branch; they must be revalidated for this branch at its exact SHA.

- [x] Offline pure-logic tests: 22 PASS locally against SHA-verified copies of models.py, ui_flow.py, schedule_approval.py and their two test files (Python 3.13).
- [x] Both translation dictionaries contain the the same set of keys; all explicitly referenced literal GUI keys are present (dynamic home_state_ prefix resolved by defined variants).
- [ ] Run `python -m unittest discover -s tests -v` on the exact committed checkout on Windows 11 and verify no regressions from preexisting tests.
- [ ] Run `python -m unittest discover -s tests -p test_first_run_gui_contract.py -v` on the exact branch; AST/headless checks are committed but not locally executed.
- [ ] Verify the Start Here screen clearly describes Blogger link insertion, not a general-purpose workflow.
- [ ] Click Step 1 → Google setup, Step 2 → Blogger link rule, Step 3 → Preview/Live; every button must reach the intended screen.
- [ ] Verify Google OAuth token presence alone displays **not verified**. Connection check failures must not show verified status.
- [ ] Validate Google first-time buttons and management buttons do not overlap at 100/125/150% Windows scaling.
- [ ] Create/edit a rule: the displayed action explanation must match the actual blog/text/URL/max-posts.
- [ ] Change a rule but do not save; confirm Preview and Live refuse to use stale persisted settings.
- [ ] Change the selected rule with unsaved edits and reject the discard prompt; confirm the original rule stays selected with all edits intact.
- [ ] Switch Japanese→English→Japanese while editing; confirm input, selected rule and selected tab survive.
- [ ] Fail a Dry Run, confirm Live stays blocked. Change the link after a successful preview and confirm a fresh preview is mandatory.
- [ ] Complete a successful controlled Dry Run and one user-confirmed live update, then confirm a second write requires another Dry Run.
- [ ] Choose a different job in Schedule without altering the job editor's selected rule.
- [ ] Schedule registration before preview must fail. Registration after preview and explicit warning must succeed on test Windows.
- [ ] Confirm `schedule_approvals.json` contains only job IDs/digests (no posts, URLs, OAuth tokens, or API keys).
- [ ] Edit a previously approved/scheduled job and let Windows launch its saved task; verify **no Blogger update** and the runner reports unapproved.
- [ ] Confirm old schedules without this branch's approval stamp fail closed until re-preview and re-registration.
- [ ] Corrupt/delete approval JSON and simulate permission errors; verify no remote write and a clear diagnostic.
- [ ] Remove a scheduled job; confirm the approval is revoked and no future automatic write runs.
- [ ] Test user-visible crash/error handling and focus/disabled controls after asynchronous exceptions.
- [ ] Run a dedicated non-production Google Blogger account for every live side-effect test; never test by writing to a customer blog.

**Current verdict: HOLD.** GitHub-hosted GUI/Windows runs and real Blogger verification have not passed on this branch. Do not merge, package or market it as release-ready.

