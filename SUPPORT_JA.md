# Workflow Automation Hub — サポート手順

対象: Windows 10 / Windows 11 64-bit (x64) の販売候補版。ARM64、Windows Server、企業管理PCは未検証または制限される場合があります。

## 「開かない」とき

1. ZIPを完全に展開してから WorkflowAutomationHub.exe を起動してください。ZIP内から直接実行しません。
2. 配布元が提示したZIPのSHA-256と、手元のZIPのSHA-256を比較してください。
   PowerShell例: Get-FileHash -Algorithm SHA256 .\WorkflowAutomationHub-....zip
3. Windows Security / Defender が警告・隔離した場合は、Defenderを無効化せず、画面の内容またはProtection Historyを確認してください。
4. 展開フォルダー内の 02_SUPPORT_DIAGNOSTICS.bat を実行してください。
5. 生成された support_report.txt のみをサポートへ送ってください。

## 送らないもの

Google OAuth JSON、client secret、access token、refresh token、パスワード、個人ブログの記事データは送らないでください。診断レポートはこれらの内容、Windowsユーザー名、ホスト名、フルパスを意図的に含めません。

## 診断レポートで確認できるもの

Windowsのバージョン/CPUアーキテクチャ、アプリのバージョン、EXE SHA-256、EXE版かソース版か、アプリ保存領域への書き込み可否、設定/ジョブ/暗号化Google設定の「存在有無」、自己診断のPASS/FAILです。

## 切り分け

- EXE自体がWindowsに止められる: SmartScreen / Defender / 企業ポリシー側を確認。
- EXEが起動してすぐ終了する: support_report.txt とEXE SHA-256を確認。
- 画面は開くがGoogle接続だけ失敗: OAuth設定、Google Cloud設定、Blogger API、アカウント権限を確認。
- 表示が崩れる: Windowsの表示倍率(100/125/150%)とスクリーンショットを記録。

販売者はセキュリティ機能を無効化する案内を標準対応にしません。原因を診断してから対応します。
