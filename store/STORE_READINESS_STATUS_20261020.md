# Store readiness status — 2026-10-20

**DRAFT / NOT READY FOR SUBMISSION**

Source head reviewed before this documentation commit: `4bfaccaf2f3e41c8932bc6abfdfbe750b7a69d8a`.

## Verified

- Code tests: 99 passed; 10 subtests passed locally; current-head Windows CI completed all relevant steps successfully.
- Fresh MSIX build/round-trip validation: PASS.
- Package hashes: unsigned f13d6cc86f3dd8f08f62195fe4a1a883c8532b3f3896839f2af5818d76135ebc; local-validation signed 6b4b02848d181b30685466e792df1799dc4b6d80f2ad535ca89dbc24aab3fc49.
- The local-validation signer matched the intended code-signing certificate thumbprint `60BB363D9BE876439137DFB31247952463106BDD`.

## Not yet verified

- Local signed MSIX installation.
- Launch from the Windows Start menu.
- Installed-package Japanese/English UI, setting persistence, close/restart, and real safe input/output.
- Installed-package Store screenshots.
- Windows App Certification Kit report.
- Live Partner Center identity re-copy and final listing review.
- Owner-approved logo, price, markets, IARC answers, privacy/support identity, EULA, and final third-party notices.

The first Scheduled API Runner install attempt failed with `0x800B0109` because the test certificate is not in `LocalMachine\\TrustedPeople`. No certificate-store change is authorized by this document. Never use `CurrentUser\\Root` or `LocalMachine\\Root`, and never weaken Windows security controls.

Local preview/config/audit behavior may be tested after installation. Google OAuth and Blogger live updates remain prohibited until an owner-authorized non-production account/environment is supplied.

Store submission, publication, main/release merge, external account access, and destructive customer-data operations are not authorized by this status note.
