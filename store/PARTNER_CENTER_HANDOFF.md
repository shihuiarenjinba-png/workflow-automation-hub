# Workflow Automation Hub — Microsoft Partner Center handoff

## Product ID: recorded for all future work

- **Product:** Workflow Automation Hub
- **Partner Center type:** MSIX or PWA app
- **Current product state:** In draft (as observed in the owner's 2026-10-18 screenshot)
- **Store ID:** `9P6SXJNNB5KK`
- **Manifest Identity Name:** `OkinawaDesktopTools.WorkflowAutomationHub`
- **Manifest Publisher:** `CN=46263F21-A700-41DB-8C9B-114C22FB82FC`
- **PublisherDisplayName:** `Okinawa Desktop Tools`
- **Family name (PFN, reference):** `OkinawaDesktopTools.WorkflowAutomationHub_j8yefg9jgh58`
- **MSIX draft version:** `0.1.0.0`

The authoritative machine-readable copy is `store/product_identity.json`.
Recheck values in Partner Center before any actual upload, especially after
account changes, Store-association operations, or a product-name change.

**Important:** Creating this Partner Center product does NOT create a usable
MSIX package, does NOT confirm identity association of an existing EXE, and
does NOT constitute a submitted or accepted app.

## Completed technical work

- [x] Recorded owner-provided official Store ID, Identity Name and Publisher.
- [x] Authored desktop FullTrust MSIX manifest (`packagedClassicApp` / `mediumIL`).
- [x] Configured Windows SDK `MakeAppx.exe` to pack and unpack a candidate MSIX.
- [x] Compare unpacked manifest Identity and bundled EXE SHA-256 with input.
- [x] Fail closed if the registered Product ID, Publisher, Name or draft state changes.
- [x] Generate a separate clearly marked **UNSIGNED-DRAFT** workflow artifact.
- [x] Created draft Japanese and English Store descriptions without unsupported claims.
- [x] Original GitHub PR remains Draft and is based on earlier unmerged GUI QA work.
- [x] Initial Windows CI run proved 94/94 unit/GUI tests and MSIX roundtrip.
- [ ] Final revalidation on the latest Store preparation branch commit.
- [ ] Owner Windows 11 installed-app QA including packaged Task Scheduler, DPAPI, user-data retention and multi-monitor 100/125/150% display scaling.
- [ ] Dedicated Google Cloud **test** OAuth client and Blogger **test** blog successful preview/live/backup/error test.
- [ ] Approve final branded logo, real screenshots (not synthetic developer QA captures), support URL, privacy URL, license terms, categories, age rating and pricing.
- [ ] Validate final package certification with Microsoft Store tools and Partner Center draft upload.
- [ ] Explicit owner signoff for any Store certification submission, publishing, or sale.

## Building an unsigned candidate on Windows

1. Check out the desired exact working branch SHA in a clean, isolated build folder.
2. Run the locked tests and `build_windows.ps1` (or retrieve the exact Windows
   CI built EXE for that SHA).
3. In that same checkout, run:

   ```powershell
   pwsh -NoProfile -File .\store\build_msix_draft.ps1
   ```

4. Inspect `store-out\msix_validation.json` and `store-out\msix.sha256.txt`.
   Never overwrite an existing output directory; a new output folder is required
   to preserve the previous package/evidence.
5. The output has a temporary developer logo and is **unsigned**. Do not
   install it directly on a normal customer's PC, upload it to Store, or sell it.
   For isolated developer installation, follow Microsoft's supported test signing
   and sandbox/VM guidance without lowering normal-machine security.

CI artifact: `WorkflowAutomationHub-Store-MSIX-UNSIGNED-DRAFT`.
The existing EXE artifact and Japanese/English GUI review images are separate.

## Microsoft Partner Center handoff

The owner has created the product already. **Do not create a second product.**
When ready, open that product and use **Start submission**, keeping work
inside a saved draft. Required sections typically cover Price/Availability,
Properties, Age ratings, Packages, Store listings and Submission options.
Use `store/STORE_LISTING_DRAFT_JA_EN.md` for review and approved copy.
Pricing/trials, market coverage and brand assets require explicit owner choices.

Do not press **Submit for certification** until the final MSIX package is
validated, listing claims verified, content/licensing/compliance approved, and
owner gives explicit permission.

A Store MSIX may ultimately be submitted unsigned because Microsoft signs
packages after successful certification; this is different from distributing
an unsigned MSIX directly or using the pre-release draft in a sale.

## Commercial release decision

**HOLD.** Functional CI passing is not equal to shipped product readiness.
Formal product license is currently absent. The existing `package_release.ps1`
intentionally refuses sales packaging without license and manual acceptance.
No MSIX package has been accepted by the Microsoft Store in this workflow.
