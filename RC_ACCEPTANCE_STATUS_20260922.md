# Workflow Automation Hub RC acceptance status - 2026-09-22

- Sales release: **NO** / `sales_release=false`
- Status: **BLOCKED**
- Branch: `feature/desktop-blogger-v1`
- Source commit: `27b2e3a6e360e37c5ffd284b3ec4cad084e11b2a`
- Artifact: `Workflow-Automation-Hub-Windows-v1.0.0-RC.exe`
- Artifact bytes: `37709310`
- SHA-256: `7d62952e5b81008ff11e641673724aa8df3e01075d7cc54d37e41e85c5c64724`
- Authenticode: **DEFERRED** (`NotSigned`)
- ZIP: not generated

## Automated acceptance completed

- Hash-locked dependency installation and `pip check`: PASS.
- Unit/integration/regression suite: PASS, 38/38.
- Source self-test: PASS, including DPAPI, strict Google OAuth validation, JA/EN resources, and Task Scheduler availability.
- Clean PyInstaller one-file build: PASS.
- Packaged EXE self-test: PASS.
- Source-free standalone self-test from a path containing Japanese characters and spaces: PASS.
- Privacy-safe diagnostics JSON: PASS; JSON parse and secret-value, username, and absolute-path scan passed.
- GUI process survival: PASS.
- Windows Defender custom scan of the exact EXE: PASS, zero artifact-related detections.
- Committed dependency evidence verification: PASS for `requirements-lock.txt`, CycloneDX SBOM, and third-party NOTICE.
- Customer artifact scan: PASS; no OAuth JSON, token, client secret value, API key, private key, local developer path, ZIP, source cache, `.git`, or temporary log was staged.

## External acceptance blocker

The supplied test OAuth JSON was inspected only through the product's strict parser and was correctly rejected because it is a Google **Web application** client. Workflow Automation Hub requires a Google OAuth client whose Application type is **Desktop app**. No credential was imported, copied, logged, committed, embedded, or staged, and no token was created. API review is also unfinished.

Provide a Desktop app OAuth JSON before continuing with human consent, real Blogger connection, dry run, one controlled live update, real backup-failure behavior, and JA/EN restart-persistence acceptance. Windows 10/11 visual inspection at 100/125/150% remains a human final check. Formal product LICENSE text remains pending owner approval but is not the current blocker.

No `main` merge, rebase, force-push, security-policy bypass, signed-status claim, or ZIP generation occurred.
