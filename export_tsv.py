import json
import sys
import urllib.parse

def main():
    input_path = "input.json"
    output_path = "output.tsv"

    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    project = data.get("name", "")
    pages = data.get("pages", [])

    with open(output_path, "w", encoding="utf-8") as out:
        for page in pages:
            orig_title = str(page.get("title", ""))
            if not orig_title.startswith("Q:"):
                continue
            # タグとタイトル部分を分離
            # 例: Q:tag1:tag2:tag3:ほげほげ
            parts = orig_title.split(":")
            tags = []
            title = ""
            if len(parts) >= 3:
                # Q:, tag1, tag2, ..., title
                tags = parts[1:-1]
                title = parts[-1].lstrip()
            elif len(parts) == 2:
                # Q:, title
                title = parts[1].lstrip()
            else:
                title = orig_title[2:].lstrip()
            tags_str = " ".join(tags)
            page_id = str(page.get("id", ""))
            # lines: 先頭がtitleと同じなら除外し、<br>で連結。タブや改行をエスケープ
            lines = page.get("lines", [])
            if lines and lines[0] == orig_title:
                lines = lines[1:]
            lines_joined = "<br>".join(line.replace("\t", " ").replace("\n", " ") for line in lines)
            # url: https://scrapbox.io/{project}/{title}（titleはURLエンコード）
            url = f"https://scrapbox.io/{urllib.parse.quote(project)}/{urllib.parse.quote(orig_title)}"
            # TSV出力
            out.write(f"{page_id}\t{title}\t{lines_joined}\t{url}\t{tags_str}\n")

if __name__ == "__main__":
    main()
