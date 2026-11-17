# Workflow Automation Hub — local final QA and Store handoff

Use the exact successful GitHub artifact. Do not rebuild before QA.

## Required artifacts

- `WorkflowAutomationHub-Store-MSIX-UNSIGNED-DRAFT`
- `WorkflowAutomationHub-Windows`
- `WorkflowAutomationHub-GUI-Review`

The Store MSIX artifact must also contain `store-product-handoff.json` and the
customer-facing Store/privacy/runFullTrust evidence.

## Exact artifact staging

Use Windows-all-auto's checked-in Group B registry rather than manually typing the
repository/artifact name:

```powershell
python scripts/pull_group_b_store_product.py `
  --product-id workflow-automation-hub `
  --run-id <exact successful GitHub Actions run id> `
  --target-root C:\path\to\group-b-local-inbox `
  --receipt C:\path\to\evidence\artifact-pull-receipt.json
```

The pull receipt is immutable evidence only. It must record no Store submission,
certification, or publication.

## Local preflight

GitHub CI is the primary test environment. Do not rerun the full unit suite locally
as a mandatory Store gate after the exact artifact has already passed CI.

1. Use the exact successful GitHub Store artifact and `store-product-handoff.json`.
2. Confirm the local MSIX exists and re-hash it against the handoff + checksum file.
3. Use Windows-all-auto's common local pre-upload conveyor to unpack the same MSIX and
   verify Manifest Identity / Publisher / Version / Architecture and the unpacked EXE SHA.
4. Do not rebuild the product locally and do not substitute a different package.
5. Do not weaken Windows trust policy or add a temporary certificate merely to run an
   unsigned draft.
6. Perform only Windows-specific/product-specific checks GitHub CI cannot prove,
   including JP/EN, real OS DPI, real OAuth/test-blog behavior and Task Scheduler.

The common local entrypoint is Windows-all-auto
`scripts/run_store_preupload_readiness.ps1`. The only successful pre-upload state is
`READY_FOR_MSIX_UPLOAD_APPROVAL`; it is an upload-approval boundary only and performs
no Store upload/certification/publish.

## Controlled integration acceptance

Use only a non-production Blogger account/blog:
- Desktop OAuth connection;
- manageable-blog selection;
- Dry Run;
- explicit one-time live mutation on test content;
- backup created before mutation;
- duplicate-link prevention;
- ambiguous failure requires a new preview;
- Task Scheduler register/run/unregister;
- diagnostics contain no OAuth token/client secret/full private paths.

Any mismatch is HOLD.

After PASS, reverify Partner Center identity/submission state, complete owner-confirmed
Store fields, run VALIDATE_ONLY and DRY_RUN, then request separate upload approval.
Certification and Publish remain later gates.
