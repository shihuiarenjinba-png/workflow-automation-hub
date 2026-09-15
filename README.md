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
