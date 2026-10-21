# Package Family Name identity audit — updated 2026-10-21

**IDENTITY DATA RESOLVED / INSTALLATION AND UPLOAD STILL NOT TESTED**

The owner recopied the following values from the existing Microsoft Partner Center product identity page on 2026-10-21:

- Store ID: `9P6SXJNNB5KK`
- Package Identity Name: `OkinawaDesktopTools.WorkflowAutomationHub`
- Publisher: `CN=46263F21-A700-41DB-8C9B-114C22FB82FC`
- Package Family Name: `OkinawaDesktopTools.WorkflowAutomationHub_j8yefg9jgfh58`

These values match the current MSIX manifest inputs. Windows `PackageFamilyNameFromId`, called with the round-tripped manifest Name and Publisher, independently returned the same PFN with API return `0x00000000`. The PublisherId suffix is 13 characters.

The earlier 12-character value `OkinawaDesktopTools.WorkflowAutomationHub_j8yefg9jgh58` was a transcription error. It remains preserved in Git history and in `store/archive/product_identity_20261018_pfn_typo.json`; it is not used for current builds.

No manifest Identity change was needed because its Name and Publisher already matched the confirmed Partner Center values. `store/product_identity.json` and the regression test were updated to the confirmed PFN. `submission_allowed` remains `false`: identity resolution does not prove installation, launch, functionality, listing completeness, upload validation, certification, or publication.

Prior evidence retained:

- round-tripped manifest SHA256 `90c6801bde1f44c50e11fdc35faa1c1b14bd95d7c16d65d005a7abe6ab79e6fe`
- pre-correction identity JSON SHA256 `73f01e5ab60c4634b64ace93765d0455376a2495e28263d3c4cfcb454035ecaa`
- unsigned MSIX SHA256 `f13d6cc86f3dd8f08f62195fe4a1a883c8532b3f3896839f2af5818d76135ebc`

References:

- https://learn.microsoft.com/en-us/windows/apps/desktop/modernize/package-identity-overview
- https://learn.microsoft.com/en-us/windows/win32/appxpkg/identity-constants
- https://learn.microsoft.com/en-us/windows/win32/api/appmodel/nf-appmodel-packagefamilynamefromid
