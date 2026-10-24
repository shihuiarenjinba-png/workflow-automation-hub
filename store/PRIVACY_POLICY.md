# Workflow Automation Hub — Privacy Policy

Status: Store preparation text. A public URL can be assigned later if the submission form requires one.

Workflow Automation Hub is a Windows desktop application that connects to Google Blogger using a Google OAuth Desktop client supplied by the user and applies user-approved link insertion rules to Blogger posts.

The application may process the user's Google OAuth Desktop client configuration, OAuth access or refresh credentials, Blogger account, blog and post information returned by the Blogger API, job configuration, destination URLs, schedules, local backups, logs, and diagnostic information.

After validation, Google OAuth client data and tokens are stored using Windows DPAPI for the current Windows user. The repository does not contain a user's OAuth credentials.

The application uses the Google Blogger API for its current connector. Live changes occur only after user configuration, preview, and confirmation. Before a live Blogger update, the current design creates a local backup of the original post HTML.

Support diagnostics are designed not to include OAuth tokens, client secrets, Windows usernames, hostnames, or absolute paths. Google processing is also subject to Google's terms and privacy policies.
