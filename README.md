# Scrapbox Q&A to Anki Importer

## 概要

ScrapboxのQ&Aページ（タイトルが`Q:`で始まるページ）をAnkiにインポートするツールです。  
**Q&Aページの書き方:**
- タイトルは `Q:` で始める（例: `Q:Pythonでリスト内包表記の使い方`）
- 本文が答えとしてAnkiカードに取り込まれます
- タイトルに `Q:tag1:tag2:質問内容` のようにタグを含めると、Ankiのタグとしてインポートされます

## 必要なもの

- Anki本体（最新版推奨）
- AnkiConnectアドオン（AnkiのAPI連携用、[公式ページ](https://ankiweb.net/shared/info/2055492159)）

## セットアップ

1. **ノートタイプ・テンプレートのインポート**
   - `resources/QAonScrapbox.apkg` をAnkiでインポート
   - （ダミーノートは不要なら削除してOK）

2. **環境変数を設定**
   - `SCRAPBOX_PROJECT`  
     - 対象Scrapboxプロジェクト名（例: `https://scrapbox.io/help-jp/` の「help-jp」の部分を指定）
   - `SCRAPBOX_SESSION_ID`  
     - Scrapboxの全ページデータをダウンロードするために必要
     - **取得方法:**
       1. ChromeでScrapboxにログイン
       2. F12でデベロッパーツールを開く
       3. [Application]タブ → [Cookies] → `connect.sid` の値をコピー
       4. これを `SCRAPBOX_SESSION_ID` に設定
   - `SCRAPBOX_DECK`（任意）  
     - インポート先のAnkiデッキ名（未設定時は `"QA on scrapbox"`）

3. **Ankiを起動し、AnkiConnectが動作している状態で `make` を実行**

## 使い方

- 必要な環境変数を設定し、Ankiを起動した状態で
- ターミナルで `make` を実行するだけでOK
- デフォルトのデッキ名は `"QA on scrapbox"`  
  変更したい場合は `SCRAPBOX_DECK` を設定


## トラブルシューティング

- **input.jsonがダウンロードできない場合**
  - エラー例: `Error: SCRAPBOX_PROJECTとSCRAPBOX_SESSION_IDの環境変数を設定してください。` など
  - 主な原因: `SCRAPBOX_SESSION_ID` が正しく設定されていない、または期限切れ・誤った値になっている可能性が高い
  - 対策:
    - Chromeのデベロッパーツールで `connect.sid` を再取得し、正しい値を環境変数に設定し直す
    - Scrapboxに再ログインしてから取得し直すと確実

- **AnkiConnectの接続確認**
  - `make check-anki` でAnkiConnectへの接続確認ができます
  - または `python3 src/check_anki_connect.py` でも確認できます
  - 正常時の出力例:  
    `{"result": 6, "error": null}`
  - エラーや応答がない場合はAnki本体やAnkiConnectの起動・インストール状況を確認してください

## 備考

- Pythonの追加モジュールとして `requests` が必要です（`pip install requests` でインストール）
- apkgファイルは `resources/QAonScrapbox.apkg` に同梱されています
- ノートタイプやテンプレートの詳細はapkgを参照してください
- 本来の使い方ではありませんが、AnkiConnectを使わずにAnkiアプリから手作業で「ファイルをインポート」（build/output.tsvを指定）することも可能です

### 中間生成ファイルについて

- `build/` ディレクトリ配下には一時的な中間生成ファイルが作成されます。
    - `build/input.json` … Scrapboxからダウンロードした全ページデータ（make時に自動生成され、再利用・削除可）
    - `build/output.tsv` … Ankiインポート用に整形されたTSVファイル（make時に自動生成され、再利用・削除可）
    - `build/.imported` … インポート済みの印ファイル（makeの冪等性管理用、不要なら削除可）
- これらのファイルは何度でも再生成できるため、不要になった場合は削除して問題ありません。
