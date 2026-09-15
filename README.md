# Workflow Automation Hub

AI判断を使わず、**Trigger → Condition → Action** を決められたルールどおりに実行するWindows向け小型ワークフロー基盤です。

## 現在の方針

- 外部LLM / Ollamaなし
- Dry Run対応
- ローカルファイル操作は `base_dir` 配下だけ
- HTTP/API呼び出しは `allow_hosts` に明示したホストだけ
- APIキー等はコードやGitへ保存しない
- Google OAuth refresh tokenはOS資格情報ストアへ保存
- APIごとに **接続 / 接続確認 / 解除** をGUIから実行
- 接続確認は読み取りまたはOAuthスコープ検証だけで、投稿・送信・アップロード等の副作用を起こさない
- 商用利用・OAuth審査・API固有規約をConnector単位で管理する

## GUI

```powershell
python -m pip install -r requirements.txt
python app.py
```

GUIでは開発・検証用にGoogle OAuthの `credentials.json` を選択し、各Connectorを個別に認証できます。

現在のConnector:

- Blogger
- Google Drive (`drive.file` のみ)
- Google Sheets (`drive.file` 優先)
- Gmail（送信のみ / `gmail.send`）
- YouTube（アップロード用 / `youtube.upload`）
- Windows Task Scheduler 2.0 接続確認

詳細な商用利用・規約上のゲートは `COMPLIANCE.md` を参照してください。

> BYOC（ユーザー自身のOAuthクライアント）は開発・検証モードとして扱います。公開商用版でGoogleの本番OAuth確認を回避する目的には使用しません。

## Workflow Core

現在のAction:

- `copy_file`
- `move_file`
- `write_text`
- `http_request`

実行例:

```powershell
python workflow_hub.py workflow.example.json --dry-run
python workflow_hub.py workflow.example.json
```

## 設計上の原則

1. 同じ設定と入力なら同じ動作をする
2. 許可されていないパスやホストには触れない
3. 秘密情報をGitや平文設定へ保存しない
4. 破壊的処理はDry Runで事前確認できる
5. AIによる自律判断はCoreへ入れない
6. APIの接続確認ではユーザーデータを変更しない
7. 規約・商用条件が不明なConnectorは販売版で有効化しない

## 次の実装候補

- Blogger Automation Pack（投稿、更新、内部リンク挿入）
- GUIからのWindows Task Scheduler登録/更新/削除
- Google Pickerを利用したDrive/Sheetsの明示的なファイル選択
- WorkflowとConnectorの統合
- 実行履歴 / Retry / エラー表示UI
