# Store readiness status — 2026-10-20

**DRAFT / NOT READY FOR SUBMISSION**

Validated source head: `4bfaccaf2f3e41c8932bc6abfdfbe750b7a69d8a`.

## Verified

- Local code tests: 99 passed; 10 subtests passed.
- Current-head Windows CI run `39400020791`: PASS, including checkout, dependency checks, unit tests, GUI evidence, EXE build, unsigned MSIX draft, and artifact uploads.
- Fresh unsigned MSIX build/round-trip: PASS; SHA256 `f13d6cc86f3dd8f08f62195fe4a1a883c8532b3f3896839f2af5818d76135ebc`.
- Local-validation signed copy SHA256 `6b4b02848d181b30685466e792df1799dc4b6d80f2ad535ca89dbc24aab3fc49`; signer matched thumbprint `60BB363D9BE876439137DFB31247952463106BDD`.

## PFN discrepancy — submission blocker

Captured `store/product_identity.json` contains `OkinawaDesktopTools.WorkflowAutomationHub_j8yefg9jgh58`, whose PublisherId suffix is 12 characters. Microsoft fixes PublisherId at 13 characters. Windows `PackageFamilyNameFromId`, using the package's Identity Name and Publisher, returned `OkinawaDesktopTools.WorkflowAutomationHub_j8yefg9jgfh58`. The captured file is intentionally unchanged; live Partner Center product `9P6SXJNNB5KK` must be recopied after owner sign-in before any package upload. Do not guess-correct the formal value.

## Not yet verified

MSIX installation, Start-menu launch, installed JP/EN UI, persistence/restart, safe local I/O, Store screenshots, WACK, and live Partner Center identity are NOT TESTED. Google OAuth/Blogger live use remains prohibited without an owner-authorized non-production account. External production OAuth also needs a public privacy-policy URL on an owner-verified domain. No certificate-store change is authorized.

## Submission safeguards

- Microsoft Standard Application License Terms (SALT) are the default when **Additional license terms** is left blank. A custom EULA is not an engineering prerequisite unless the owner chooses different terms.
- Prices and Japan/United States markets remain proposals only. Disable future-market automatic expansion.
- Immediately before certification submission, select **Don't publish this submission until I select Publish now**. The default can publish automatically after certification.
- AI-generated icons remain unapproved concepts and are not package or Store assets.
- Certificate-store changes, Store upload/submission/publication, and main/release merges remain unauthorized.
