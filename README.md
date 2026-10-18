# Workflow Automation Hub

AI判断を使わず、**Trigger → Condition → Action** を決められたルールどおりに実行するための小型ワークフロー基盤です。

## MVP方針

- Python標準ライブラリ中心
- 外部LLM / Ollamaなし
- Dry Run対応
- ローカルファイル操作は `base_dir` 配下だけ
- HTTP/API呼び出しは `allow_hosts` に明示したホストだけ
- APIキー等はJSONへ直書きせず環境変数 `${ENV:NAME}` から参照
- 実行結果をJSON Linesで監査ログへ保存

## 現在のAction

- `copy_file`
- `move_file`
- `write_text`
- `http_request`

Blogger / Google Drive / Sheets等は、認証モジュールを分離したConnectorとして後から追加します。

## 実行

```powershell
python workflow_hub.py workflow.example.json --dry-run
python workflow_hub.py workflow.example.json
```

## 設計上の原則

1. 同じ設定と入力なら同じ動作をする
2. 許可されていないパスやホストには触れない
3. 秘密情報をGitへ保存しない
4. 破壊的処理はDry Runで事前確認できる
5. AIによる自律判断はCoreへ入れない

## 次の実装候補

- Google OAuth Desktop Flow
- Blogger API Connector
- Google Drive / Sheets Connector
- Schedule Trigger
- Folder Trigger
- GUI設定画面

## Trigger → Condition → Action editor (improvement branch)

Run `python workflow_gui.py`. The UI supports manual or local file-exists triggers; optional file-exists, extension and UTF-8 text-match conditions; and explicit copy/move/write-text/HTTPS-GET actions. The workflow evaluates the trigger and every condition before taking actions, logs skipped runs and respects the existing working-folder and allowed-host boundaries. Preview/Dry Run does not execute a real HTTP request or mutate files. This narrow GUI does **not** implement continuous scheduler service, multi-condition visual editing, OAuth or arbitrary shell commands. A separately developed, more extensive `feat/workflow-safe-stale-locks-20261018` Windows desktop implementation exists and must be reconciled before selecting the product release. The new improvement-branch GitHub Actions unittest/compile workflow passed on Linux and Windows, but this is not a real GUI/MSIX acceptance test. Store submission: **HOLD**.
