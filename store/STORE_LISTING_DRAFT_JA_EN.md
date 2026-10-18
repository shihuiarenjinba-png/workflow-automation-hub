# Microsoft Store listing draft — Workflow Automation Hub

**Internal working draft. DO NOT submit to certification or publish yet.**
Partner Center product exists as **In draft**, Store ID `9P6SXJNNB5KK`.
This page contains customer-facing text to review and copy later. It is not evidence
of successful Store submission, entitlement, identity signing, or package acceptance.

## 日本語 / Japanese

### 製品名
Workflow Automation Hub

### 短い説明
Google Bloggerの記事へ、指定した文字列とリンク先URLに基づきリンクを追加するWindowsアプリです。変更前の試運転に対応します。

### 製品の説明
Workflow Automation Hubは、Google Bloggerの自分が管理するブログ記事にリンクを追加するためのWindowsデスクトップアプリです。

Googleアカウントを接続してブログを選び、検索文字列、表示するリンク文字列、リンク先URL、対象記事数を設定します。「試運転」で変更予定件数を確認してから、確認画面を経て記事を更新できます。

主な機能:
- 日本語・英語の画面と初回操作ガイド
- Google Blogger APIによる管理ブログの接続・一覧表示
- 指定した文字列へのリンク追加、同一URLの重複を回避
- 変更しない試運転（件数の確認）と本実行前の確認
- 更新前の元記事HTMLをローカルへバックアップ
- Windows タスク スケジューラによる任意の定期実行（ログオン中のみ）
- 実行ログと、問題発生時のサポート診断機能

**ご利用前に必要なもの:** Windows 10（バージョン2004以降）またはWindows 11、Google Bloggerで管理できるブログ、Google Cloudでご自身が用意したDesktop app形式のOAuthクライアント設定（JSON）、Blogger APIの有効化、接続時のインターネット環境。

**機能上の制限:** 任意のAPI・ウェブサイトの自動化ツールではありません。記事本文の自動生成、AIによる記事執筆、記事ごとの全文変更差分プレビューは提供しません。定期実行はWindowsにログオン中に限られます。Google側の利用条件や認証設定は別途必要です。

## English

### Name
Workflow Automation Hub

### Short description
Add links to your own Google Blogger posts using user-defined text and target URLs. Preview counts before changes are applied.

### Description
Workflow Automation Hub is a Windows desktop application for adding links to Google Blogger posts you manage.

Connect your Google account, choose a blog, and configure the text to find, link label, destination URL, and maximum posts to scan. Run a no-write preview before explicitly confirming changes.

Features:
- Guided first-run interface in Japanese and English
- Google Blogger API connection and manageable-blog selection
- Deterministic link insertion and duplicate-URL avoidance
- Dry-run change counts and explicit live-run confirmation
- Local original-HTML backup before each update
- Optional Windows Task Scheduler integration (signed-in users only)
- Audit logs and privacy-conscious diagnostic reports

**Setup required:** Windows 10 version 2004 or later, or Windows 11; a Blogger blog you manage; your own Google Cloud OAuth **Desktop app** JSON with Blogger API enabled; internet connectivity for Blogger operations.

**Limitations:** This is not a general-purpose API automation tool, AI writer, or content generator. The preview summarizes expected counts, not a full per-post diff. Scheduled jobs require a logged-in Windows user. Google Cloud setup and Google account authorization are provided by the customer.

## Required listing completion / 掲載前に必要
- [ ] Confirm feature descriptions against an installed, Store-packaged EXE
- [ ] Owner selects supported markets, paid/free model, pricing and trial
- [ ] Final owner-approved brand logo, screenshots, and privacy-policy/support URLs
- [ ] Verify age ratings, data declarations, Google API consent-screen obligations
- [ ] Confirm right to use brand names and product license/terms
- [ ] Replace all CI-only logo placeholders with brand-approved images
- [ ] Verify real Windows 100%, 125%, 150% DPI and keyboard accessibility
- [ ] Review package fullTrust restricted capability disclosure/certification notes
- [ ] Complete dedicated non-production Blogger OAuth, preview, live-write and scheduler QA
- [ ] Verify final MSIX identity, package version, install/uninstall, upgrade, data persistence
- [ ] Obtain explicit acceptance before pressing **Submit for certification**

**Packaging reference:** `store/product_identity.json`. Never change Identity Name or
Publisher to make a build pass; both values must match Partner Center exactly.
