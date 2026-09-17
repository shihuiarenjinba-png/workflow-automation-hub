# Code / Package Operator Handoff — Workflow Automation Hub

Updated: 2026-09-17

## Current boundary

The GitHub-side candidate is prepared for a controlled Windows build and Blogger acceptance test. The repository currently builds and self-tests `WorkflowAutomationHub.exe`; the final customer ZIP is intentionally left to the code/package operator.

## GitHub-side work already prepared

- Desktop OAuth JSON validation and DPAPI-protected config/token storage.
- Blogger Connection Test and manageable-blog discovery.
- Deterministic internal-link insertion and duplicate-link prevention.
- Dry Run, JSONL audit, backup-before-live-patch, job lock, strict settings/jobs validation, atomic save.
- Task Scheduler is constrained to the fixed runner and interactive/LIMITED execution.
- Japanese/English language contract and build/self-test gates.
- Sales checklist documents remaining Windows/Google gates.

## Code/package operator responsibilities

1. Build the exact approved branch/commit on a controlled Windows machine.
2. Run the repository tests, source self-test, PyInstaller build, and packaged EXE self-test.
3. Create the customer/RC ZIP only after the above succeeds.
4. Include the EXE, required user/setup documentation, release checklist, dependency/license notices, and a release information file identifying the exact source commit.
5. Scan the package for accidental OAuth JSON, access/refresh tokens, client secrets, API keys, passwords, personal test data, and other secrets before distribution.
6. Test Windows 10/11, JA/EN persistence, and 100% / 125% / 150% scaling.
7. Use a controlled Google Cloud Testing project with a Desktop app OAuth client and a test Blogger blog.
8. Verify import/authorize/restart persistence, Blogger Connection Test, Dry Run, controlled live update, local backup, and backup-failure fail-closed behavior.
9. Verify Scheduler behavior and restart behavior.
10. Run Defender/AV and complete LICENSE / NOTICE / SBOM / dependency-lock review.
11. Recheck the current Google/Blogger production/verification requirements immediately before sale.
12. Record the SHA-256 of the exact ZIP actually distributed.

## Authenticode / Microsoft signing

Authenticode is **deferred** in this handoff because the owner's signing path is currently unavailable. Do not mark signing as passed.

Unsigned RC packages may be used for controlled acceptance. If the final customer package is distributed unsigned, document that state clearly and expect possible Windows reputation/security warnings. If signing becomes available later, sign the exact final binary and regenerate the package SHA-256 afterward.

## Sales status

This handoff does not mark the product sales-ready. Packaging and real Google/Windows acceptance belong to the next operator, and unresolved checklist items remain release blockers unless the owner explicitly accepts a documented exception.
