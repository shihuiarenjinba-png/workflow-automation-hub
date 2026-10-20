# Package Family Name identity audit — 2026-10-20

**OPEN / LIVE PARTNER CENTER RECHECK REQUIRED**

No value in `store/product_identity.json`, the package manifest, or Partner Center was edited by this audit.

Microsoft documents PFN as `<Name>_<PublisherId>` and PublisherId as exactly 13 Crockford-base32 characters. Windows `PackageFamilyNameFromId` was called with the round-tripped MSIX manifest values:

- Name: `OkinawaDesktopTools.WorkflowAutomationHub`
- Publisher: `CN=46263F21-A700-41DB-8C9B-114C22FB82FC`
- API result: `OkinawaDesktopTools.WorkflowAutomationHub_j8yefg9jgfh58`
- API return: `0x00000000`
- calculated PublisherId length: 13

The captured Partner Center record in `store/product_identity.json` says `OkinawaDesktopTools.WorkflowAutomationHub_j8yefg9jgh58`; its suffix is 12 characters and differs by the missing `f` after `jg`.

Evidence:

- round-tripped manifest SHA256 `90c6801bde1f44c50e11fdc35faa1c1b14bd95d7c16d65d005a7abe6ab79e6fe`
- captured identity JSON SHA256 before this audit `73f01e5ab60c4634b64ace93765d0455376a2495e28263d3c4cfcb454035ecaa`
- unsigned MSIX SHA256 `f13d6cc86f3dd8f08f62195fe4a1a883c8532b3f3896839f2af5818d76135ebc`

The existing JSON identifies its evidence as an owner-provided Partner Center screenshot dated 2026-10-18. Live product `9P6SXJNNB5KK` remains behind owner sign-in and has not been recopied. Before any upload, copy live Identity Name, Publisher, and PFN character-for-character and resolve the mismatch. Do not reserve a replacement product or guess-correct the formal value.

References:

- https://learn.microsoft.com/en-us/windows/apps/desktop/modernize/package-identity-overview
- https://learn.microsoft.com/en-us/windows/win32/appxpkg/identity-constants
- https://learn.microsoft.com/en-us/windows/win32/api/appmodel/nf-appmodel-packagefamilynamefromid
