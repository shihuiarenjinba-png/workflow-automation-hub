# Connector Compliance Gate

Last reviewed: 2026-09-15

This file is an engineering compliance checklist, not legal advice. Before a commercial release, re-check the current official terms because API policies and pricing can change.

## Global rules

1. Use documented APIs only. No reverse-engineered or undocumented endpoints.
2. Request the minimum OAuth scope needed for the enabled feature.
3. Never use BYOC as a mechanism to evade Google production OAuth verification.
4. Store refresh tokens in the OS credential store, not plaintext JSON, `.env`, logs, or the repository.
5. Connection tests must be read-only or token/scope validation. A connection test must not publish, upload, send mail, delete, or mutate user data.
6. Each connector must show its outbound-data status and applicable policy warning in the UI.
7. Commercial release is blocked if the connector's terms review is stale or unresolved.

## Blogger

Status: **Allowed with Google terms / production OAuth requirements**

- Official API documentation explicitly supports desktop applications/plugins that create and edit Blogger posts.
- Blogger API Terms incorporate the Google APIs Terms of Service.
- Use OAuth 2.0 for private user data.
- Connection test: `GET /blogger/v3/users/self` (read-only request using the granted Blogger scope).

Official references:
- https://developers.google.com/blogger
- https://developers.google.com/blogger/terms
- https://developers.google.com/blogger/docs/3.0/using
- https://developers.google.com/terms/api-services-user-data-policy
- https://developers.google.com/identity/protocols/oauth2/policies

## Google Drive

Status: **Allowed only for reviewed use cases**

- Use `drive.file` by default. It is Google's recommended narrow, non-sensitive per-file scope.
- Do not ship a generic "backup everything to Drive" feature by default. Drive API terms identify certain backup-to-Drive use cases as requiring Google's express prior written consent.
- Prefer user-selected files/folders and user-visible upload actions/workflows.
- Connection test: `about.get(fields=user(...))` with `drive.file`.

Official references:
- https://developers.google.com/workspace/drive/api/guides/api-specific-auth
- https://developers.google.com/workspace/drive/api/terms
- https://developers.google.com/workspace/drive/api/guides/limits

## Google Sheets

Status: **Allowed with narrow scopes / production verification rules**

- Prefer `drive.file` where the user explicitly selects or shares a spreadsheet with the app.
- Avoid broad `drive` / `drive.readonly` scopes.
- `spreadsheets` and `spreadsheets.readonly` are sensitive scopes and can require additional verification for public apps.
- Connection test: if a Spreadsheet ID is supplied, perform `spreadsheets.get` for minimal metadata; otherwise validate the OAuth token/scope only.

Official references:
- https://developers.google.com/workspace/sheets/api/scopes
- https://developers.google.com/workspace/sheets/api/limits

## Gmail

Status: **Sensitive / release only after OAuth review**

- For a send-only automation, request `gmail.send` only.
- `gmail.send` is a sensitive scope. Public production apps can require OAuth verification.
- Avoid `gmail.readonly`, `gmail.modify`, `gmail.compose`, `gmail.metadata`, or full-mail scope unless a feature genuinely requires them; several are restricted scopes and can trigger stronger verification/security-assessment requirements.
- Connection test: validate the access token and presence of `gmail.send`; do not send a test email automatically.

Official references:
- https://developers.google.com/workspace/gmail/api/auth/scopes
- https://developers.google.com/workspace/gmail/api/reference/quota
- https://developers.google.com/terms/api-services-user-data-policy

## YouTube Data API

Status: **Strictly conditional**

- Default quota is available, but quota increases require a compliance audit.
- Do not automate or trigger uploads, comments, likes, dislikes, views, or similar user actions without the user's prior specific and express consent.
- Uploads from unverified API projects can be restricted to private viewing until the project passes the applicable audit.
- Use `youtube.upload` for upload-only functionality; do not request broader access without need.
- Connection test: token/scope validation only. It must not upload a test video.

Official references:
- https://developers.google.com/youtube/terms/developer-policies
- https://developers.google.com/youtube/v3/getting-started
- https://developers.google.com/youtube/v3/guides/quota_and_compliance_audits
- https://developers.google.com/youtube/v3/docs/videos/insert

## Windows Task Scheduler

Status: **Local Windows feature; no external API charge**

- Use Task Scheduler 2.0, the documented Windows API for new development.
- UI may create/update/delete only tasks owned by this application.
- Register one fixed signed runner executable plus a validated workflow ID. Do not expose arbitrary command, PowerShell, shell, or executable registration to end users.
- Default to the current user's context. Do not store Windows account passwords.
- Do not request elevation unless a specific feature actually requires it.
- Connection test is read-only: connect to `Schedule.Service` and read the root task folder.

Official references:
- https://learn.microsoft.com/windows/win32/taskschd/task-scheduler-start-page
- https://learn.microsoft.com/windows/win32/taskschd/taskfolder-registertaskdefinition
- https://learn.microsoft.com/windows/win32/taskschd/about-the-task-scheduler

## Pricing gate

"Free setup" means the connector can be configured without a mandatory paid API plan at ordinary/standard usage at the time of review. It does **not** mean unlimited or permanently free. Google Workspace API pricing and quota models changed in 2026, and standard usage can be free while over-quota usage may later be billed. The product must therefore expose quota errors clearly and must never auto-enable paid quota or billing.
