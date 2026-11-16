# Workflow Automation Hub — local final QA and Store handoff

Use the exact successful GitHub artifact. Do not rebuild before QA.

## Required artifacts

- `WorkflowAutomationHub-Store-MSIX-UNSIGNED-DRAFT`
- `WorkflowAutomationHub-Windows`
- `WorkflowAutomationHub-GUI-Review`

The Store MSIX artifact must also contain `store-product-handoff.json` and the
customer-facing Store/privacy/runFullTrust evidence.

## Local preflight

1. Checkout the exact source SHA from `store-product-handoff.json`.
2. Run the full unit suite.
3. Require exact MSIX SHA match against handoff + checksum file.
4. Unpack with MakeAppx for inspection without changing Windows trust policy.
5. Require unpacked EXE SHA == handoff EXE SHA.
6. Verify JP/EN UI and 100/125/150% DPI.

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
