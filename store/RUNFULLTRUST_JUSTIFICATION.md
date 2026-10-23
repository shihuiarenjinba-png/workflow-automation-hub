# Workflow Automation Hub — runFullTrust justification draft

The package contains a packaged Win32 desktop application. `runFullTrust` is required for normal desktop execution, Windows DPAPI-protected local credential storage, local backup and log file access, launching the system browser for OAuth, and optional registration, query, or removal of this application's own Windows Task Scheduler entries.

Scheduled tasks are designed for the signed-in user with limited run level. The application does not accept arbitrary shell commands or user-supplied executables for scheduled execution and does not use this capability to bypass Windows security controls.
