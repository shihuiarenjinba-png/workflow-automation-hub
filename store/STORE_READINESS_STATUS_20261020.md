# Workflow Automation Hub — Store readiness status

Updated: 2026-11-16 JST

**GITHUB ENGINEERING COMPLETE / LOCAL GOOGLE-BLOGGER QA HOLD / STORE WRITE HOLD**

Repository branch: `codex/hub-standard-consumer-ui-20261113`  
Draft PR: #12

## GitHub-side completed

- bilingual first-run workflow;
- preview-before-live and fail-closed write guards;
- Task Scheduler approval contract;
- Windows GUI smoke and simulated DPI-layout tests;
- source self-test and packaged EXE self-test;
- privacy-conscious diagnostics check;
- CycloneDX SBOM + THIRD_PARTY_NOTICES + locked dependencies;
- unsigned MSIX build and Store identity validation;
- SBOM/notices/requirements embedded into the MSIX and checked after pack/unpack;
- exact-package `store-product-handoff/2` generation;
- local final-QA runbook and Store documents bundled with the Store artifact.

Local QA must use the exact GitHub artifact; do not rebuild before acceptance.

## Canonical Store identity

- Store ID: `9P6SXJNNB5KK`
- Identity: `OkinawaDesktopTools.WorkflowAutomationHub`
- Publisher: `CN=46263F21-A700-41DB-8C9B-114C22FB82FC`
- PFN: `OkinawaDesktopTools.WorkflowAutomationHub_j8yefg9jgfh58`
- technical MSIX version: `1.0.0.0`

Repository identity remains evidence only. Live Partner Center must be reverified.

## Commercial position

Launch model: FREE candidate.

No Partner Center price/market change or Blogger production mutation is authorized by
this repository state.

## Local-only remaining gates

Use only a controlled non-production Google/Blogger environment:

- physical JP/EN + 100/125/150% DPI;
- OAuth Desktop app connection;
- manageable-blog selection;
- Dry Run;
- one controlled test-blog mutation;
- backup-before-write;
- duplicate-link prevention;
- ambiguous-write behavior requiring a fresh preview;
- Task Scheduler register/run/unregister;
- restart/normal exit;
- diagnostics privacy;
- live Partner Center reverify;
- owner assets/security/audience review.

Return local PASS through an exact-package `local-final-qa-receipt/1`.

After that: live reverify -> owner fields -> VALIDATE_ONLY -> DRY_RUN -> separate upload
approval. Certification and Publish remain separate gates.
