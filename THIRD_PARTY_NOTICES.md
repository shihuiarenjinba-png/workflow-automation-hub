# Third-Party Dependency Notes

Last reviewed: 2026-09-15

This is an engineering inventory, not a substitute for the exact license files shipped by each dependency version.

## google-auth

- License: Apache License 2.0
- Commercial use: permitted under the license terms.
- Release action: preserve applicable copyright/license notices.
- Upstream: https://github.com/googleapis/google-cloud-python/tree/main/packages/google-auth

## google-auth-oauthlib

- License: Apache License 2.0
- Commercial use: permitted under the license terms.
- The historical standalone repository was archived in 2026 and the package source moved to the Google Cloud Python monorepo.
- Release action: preserve applicable copyright/license notices and verify the exact packaged version.
- Upstream: https://github.com/googleapis/google-cloud-python/tree/main/packages/google-auth-oauthlib

## keyring

- License: MIT
- Commercial use: permitted under the license terms.
- Release action: include the license/copyright notice for the packaged version.
- Upstream: https://github.com/jaraco/keyring

## pywin32

- License: mixed permissive licenses; individual source/license files are authoritative.
- Commercial redistribution is generally permitted by the principal license terms, subject to notice/redistribution conditions.
- Release action: pin the tested version before release and include the license files/notices required by that exact distribution.
- Upstream: https://github.com/mhammond/pywin32

## Release gate

Before a paid binary is published:

1. Freeze exact dependency versions.
2. Export the dependency tree.
3. Collect license metadata and upstream license texts for the exact versions.
4. Block release on GPL/AGPL/SSPL or unknown-license additions until reviewed for product compatibility.
5. Include the required third-party notices in the installer/portable package.
