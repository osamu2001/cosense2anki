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
     - 対象Scrapboxプロジェクト名（例: `help-jp` は `https://scrapbox.io/help-jp/` の「help-jp」部分）
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

## 備考

- Pythonの追加モジュールや特別なセットアップは不要です
- apkgファイルは `resources/QAonScrapbox.apkg` に同梱されています
- ノートタイプやテンプレートの詳細はapkgを参照してください
