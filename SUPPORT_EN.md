# Workflow Automation Hub — Support Guide

Target: release candidate for Windows 10 / Windows 11 64-bit (x64). ARM64, Windows Server, and centrally managed corporate PCs are unverified or may be restricted.

## If the app does not open

1. Fully extract the ZIP before starting WorkflowAutomationHub.exe. Do not run it from inside the ZIP viewer.
2. Compare the ZIP SHA-256 with the value published by the distributor.
   PowerShell example: Get-FileHash -Algorithm SHA256 .\WorkflowAutomationHub-....zip
3. If Windows Security / Defender warns or quarantines the file, do not disable Defender. Record the warning or check Protection History.
4. Run 02_SUPPORT_DIAGNOSTICS.bat from the extracted folder.
5. Send only the generated support_report.txt to support.

## Do not send

Do not send Google OAuth JSON, client secrets, access/refresh tokens, passwords, or private blog content. The portable diagnostic report intentionally excludes credential contents, Windows usernames, hostnames, and absolute paths.

## What the report contains

Windows version and CPU architecture, app version, EXE SHA-256, frozen/source runtime, app-data write check, presence-only flags for settings/jobs/encrypted Google state, and self-test PASS/FAIL.

## Triage

- Windows blocks the EXE before launch: inspect SmartScreen / Defender / corporate policy.
- EXE starts and exits: inspect support_report.txt and the EXE SHA-256.
- UI opens but Google connection fails: inspect OAuth configuration, Google Cloud setup, Blogger API, and account permissions.
- UI layout is clipped: record Windows display scaling (100/125/150%) and a screenshot.

Standard support should not instruct users to disable security protections. Diagnose the failure first.
