# Store readiness status — updated 2026-10-21

**DRAFT / NOT READY FOR SUBMISSION**

Validated functional source head: `4bfaccaf2f3e41c8932bc6abfdfbe750b7a69d8a`.

## Verified

- Local code tests: 99 passed; 10 subtests passed.
- Windows CI run `39442627683` at head `64a3f5c5573e2343f2fd579da9fa618cce512682`: PASS, including tests, GUI evidence, EXE build, and unsigned MSIX draft/upload.
- Fresh unsigned MSIX build/round-trip: PASS; SHA256 `f13d6cc86f3dd8f08f62195fe4a1a883c8532b3f3896839f2af5818d76135ebc`.
- Local-validation signed copy SHA256 `6b4b02848d181b30685466e792df1799dc4b6d80f2ad535ca89dbc24aab3fc49`; signer matched thumbprint `60BB363D9BE876439137DFB31247952463106BDD`.
- Owner-confirmed Partner Center Identity Name, Publisher, and PFN now match the manifest and Windows API calculation exactly. The historical 12-character PFN transcription is archived and excluded from builds.

## Not yet verified

MSIX installation, Start-menu launch, installed JP/EN UI, persistence/restart, safe local I/O, Store screenshots, WACK, and Partner Center package upload validation are NOT TESTED. Google OAuth/Blogger live use remains prohibited without an owner-authorized non-production account. External production OAuth also needs a public privacy-policy URL on an owner-verified domain. No certificate-store change is authorized.

## Submission safeguards

- Microsoft Standard Application License Terms (SALT) are the default when **Additional license terms** is left blank. A custom EULA is not an engineering prerequisite unless the owner chooses different terms.
- Prices and Japan/United States markets remain proposals only. Disable future-market automatic expansion.
- Immediately before certification submission, select **Don't publish this submission until I select Publish now**. The default can publish automatically after certification.
- AI-generated icons remain unapproved concepts and are not package or Store assets.
- Certificate-store changes, certification submission, publication, and main/release merges remain unauthorized.
- Package upload is a separate Gate A action after a final MSIX, installed-package verification, completed assets/notices, fixed SHA256, and owner confirmation.
