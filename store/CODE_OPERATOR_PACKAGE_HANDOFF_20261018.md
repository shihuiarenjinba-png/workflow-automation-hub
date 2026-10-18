# Code operator → Microsoft Store packaging handoff (2026-10-18)

## Decision and role boundary

The owner requests **UI/feature/integration-first source development**, then
delegates Windows launch tests, build/package creation and technical validation
to the separate code operator. A Draft PR is the handoff source, not a
certified binary. Do not claim a PASS without a log from the exact commit.

Use **the indicated existing GitHub branch only** in an isolated new Windows
working directory. Do not edit `main`, overwrite any published EXE/MSIX,
delete source branches, alter customer files, reuse another SKU's Store
identity, or merge a layered PR out of order. Preserve logs and test fixtures
without secrets. All source fixes must be committed to a dedicated branch
and linked to a reviewable PR; do not quietly patch a packaged artifact.

## Standard Windows acceptance gate

1. Capture the current branch's **exact full Git SHA**. Run:
   `python -m compileall -q .`
   and `python -m unittest discover -s tests -v`.
   Do not ship if even one test fails, skips a required Windows feature or
   if expected GUI actions do not execute. Keep the complete redacted logs.
2. Open the real GUI at 100%, 125%, 150% DPI in Japanese and English. Verify
   no clipping, unusable hidden actions, labels inconsistent with features,
   keyboard-only tab navigation, and that user data persists as described.
3. Exercise the exact UI → configuration → offline preview → explicit
   live confirmation → safe output → restart flow on authorized synthetic
   fixtures. Repeat, fail mid-operation, change settings after preview, and
   test existing-file collisions. Never use real customers' data.
4. Build fresh EXE in a unique new output path; test both source and packaged
   `--self-test` modes and any product-specific runtime smoke.
5. Build a **Store-appropriate MSIX / MSIXBundle** with the exact reserved
   Name and Publisher copied from Partner Center. Validate signing requirements,
   required assets/rights, dependencies, icons, package architecture,
   install, launch, update, uninstall and Windows App Certification Kit/Store
   validations. Store upload requires the MSIX file, **not** merely an EXE ZIP.
6. Validate file/secret protection, logs, startup registrations and persistence
   across the install/update/uninstall lifecycle, including different users.
7. Prepare actual JP/EN Store screenshots from the built UI, final listing,
   support/privacy URL, license/third-party notice evidence and pricing
   review. Use the owner's existing product slot only.
8. Report in one evidence table: SHA; Python tests; GUI JP/EN 100/125/150%;
   live synthetic workflow; frozen EXE; MSIX manifest; Windows install/update;
   WACK/Store certification; security and data; license and screenshots;
   all PASS/FAIL/BLOCKED with log/artifact paths. If a gate fails, send the
   exact failure back for repair without claiming sales readiness.

**GitHub Actions caveat:** private sibling repositories' hosted CI jobs have
failed before allocating any runner steps (and the job logs could not be
downloaded); this is not proof that test code failed. Investigate Actions
billing/permissions/runner allocation without buying more allowance without
the owner's approval. Use local Windows operator verification meanwhile.

Do not submit to Partner Center automatically; owner reviews the completed
package and explicitly authorizes the actual submission.

## This product

- Product: **Workflow Automation Hub**
- Reserved Microsoft Store ID: `9P6SXJNNB5KK`
- Package Identity Name: `OkinawaDesktopTools.WorkflowAutomationHub`
- Package Publisher: `CN=46263F21-A700-41DB-8C9B-114C22FB82FC`
- Publisher display name: `Okinawa Desktop Tools`
- Source: `shihuiarenjinba-png/workflow-automation-hub` / Draft PR #7: https://github.com/shihuiarenjinba-png/workflow-automation-hub/pull/7
- Full source branch (do not use only PR base): `feat/workflow-safe-stale-locks-20261018`
- Actual desktop GUI entrypoint: `desktop_app.py`
- Initial non-sales validation command: `powershell -ExecutionPolicy Bypass -File .\build_windows.ps1`
- This source can be handed over for operator verification, but do not mark binary PASS until logs exist.

## Product-specific end-to-end scenario

**This precise PR #7 commit previously passed the Windows CI test/build
pipeline**, including a draft unsigned Store MSIX builder. Re-run the full
suite on the final checked-out SHA and do not reuse old success from a
different SHA. GUI is Blogger-focused: Google OAuth configuration, approved
Blog selection, link-insertion target, no-write preview, explicit edit approval,
real mutation on a disposable authorized Blogger post, old-body backup,
audit trail, rollback/recovery guidance, partial/uncertain error handling,
and Windows scheduled tasks. Simulate a long-running job: the safety lock must
never expire while its recorded owner process remains alive. Unreadable lock
fails closed, and manual verification is required to reclaim any orphan.
Include `tests/test_locks.py` and Blogger mutation regression suite.

Use `build_windows.ps1` for validation and
`store/build_msix_draft.ps1` for the known unsigned candidate, matching the
exact Store identity. Replace draft placeholder logos with approved commercial
art. Validate OAuth consent/publishing/app-verification requirements,
credential DPAPI isolation, Store sandbox file locations, executable path used
by Windows scheduled tasks after MSIX updates, and customer support procedures.
Do not upload unfinished unsigned MSIX as a public sale package.

## Where to send evidence

Record build report, SHA256 of tested binaries, new MSIX name/version,
real JP/EN GUI screenshots, redacted test results and final QA decision in
an additional dated file under `store/` on the same product branch. Surface
every discovered source defect in a follow-up PR. Keep `main` and any
previous release unchanged until separately authorized.
