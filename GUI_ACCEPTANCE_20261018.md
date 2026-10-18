# Workflow Automation Hub — GUI review and Windows QA (2026-10-18)

**Status: HOLD — NOT APPROVED FOR SALE OR MERGE.**

## What the customer sees
Product purpose is stated before configuration: find a phrase in the user's own
Google Blogger posts and insert one chosen link, without generating articles.
The primary journey is Connection → Save a rule → Dry Run → Confirm and update.
Advanced Windows scheduling is optional. The GUI no longer places LocalAppData
or EXE deployment details in the top bar.

## Changes in this PR
- A live preview is consumed **before** a Blogger PATCH starts. A lost response
  or partial update cannot leave the same preview ready for another write.
- The UI blocks editing, job deletion, import/disconnect, locale changes, and
  schedule edits during an asynchronous operation.
- Job list shows customer-facing names only, with an internal row-to-ID map.
  Even duplicate visible names cannot redirect execution to a different job.
- The Blogger rule editor has a vertical scrolling viewport and a scrollable
  saved-jobs list. Reduced fixed widths accommodate higher DPI.
- Seven **mock-only** screenshots (JP start, connection, rules, schedule,
  150%-relative rules top and bottom, EN start) plus a geometry report are
  created by the GitHub Windows workflow. This captures a real Tk window,
  without reading user credentials or accessing Google Blogger.

## Automated QA evidence
Run: https://github.com/shihuiarenjinba-png/workflow-automation-hub/actions/runs/39088168845

- Exact code SHA tested: `314ec8a0bba5a75295e7e9dc53859c2c2c32e1d5`.
- 89 unittest tests: **PASS** on GitHub-hosted Windows.
- Windows EXE build and packaged EXE self-test: **PASS**.
- Dependency, source self-test and privacy diagnostics: **PASS**.
- Screenshot artifact: `WorkflowAutomationHub-GUI-Review`.
- Windows runner display: 964×678 captured area; native Tk DPI scale
  ~1.333. Editor screenshot at native ×1.5 uses Tk scale 2.0.
- Reported inner editor width at native ×1.5: 800 pixels, within a
  899-pixel visible canvas. Scroll-to-bottom exercised.
- **Not the same as validating 150% Windows system display scaling on
  customer hardware.** A Tk scale change tests layout behavior but does not
  simulate every Windows per-monitor DPI condition.

## Acceptance steps still required before release
- [ ] Windows 10 (if supported) and Windows 11 on a physical or interactive
  acceptance PC; confirm readable fonts, keyboard focus and screen-reader
  labels, 100%/125%/150% real display scaling, and window resizing.
- [ ] Verify text is readable on all five tabs, including the compliance tab;
  no horizontally clipped controls, and scrolling reaches all instructions.
- [ ] Disconnect/reconnect test Google account; cancel OAuth; corrupt JSON;
  deny permissions; verify clear errors without credentials in logs.
- [ ] On a **dedicated private test blog**, confirm preview makes zero changes,
  then apply one user-approved live change and examine the original-content
  backup and audit trail.
- [ ] Simulate a Blogger PATCH that applies remotely but loses its response;
  GUI must demand a fresh preview and actual remote state review before
  repeating a write.
- [ ] Register Daily/Weekly/Logon tasks on real Windows; verify approval
  fingerprint, changed-rule refusal, unregister/deletion failure, and
  shutdown/reboot behavior.
- [ ] Confirm OAuth/Blogger production permission, privacy policy, license,
  dependency notices, signing/packaging and Microsoft Store submission gates.
- [ ] Perform hands-on beginner usability trial: an unfamiliar user should
  identify the app's purpose and complete the first mock workflow without
  spoken coaching.

These screenshots are developer QA evidence, not marketing screenshots.
Old main and existing published releases have not been modified.
