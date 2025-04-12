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
            title = str(page.get("title", ""))
            if not title.startswith("Q:"):
                continue
            page_id = str(page.get("id", ""))
            # lines: 先頭がtitleと同じなら除外し、<br>で連結。タブや改行をエスケープ
            lines = page.get("lines", [])
            if lines and lines[0] == title:
                lines = lines[1:]
            lines_joined = "<br>".join(line.replace("\t", " ").replace("\n", " ") for line in lines)
            # url: https://scrapbox.io/{project}/{title}（titleはURLエンコード）
            url = f"https://scrapbox.io/{urllib.parse.quote(project)}/{urllib.parse.quote(title)}"
            # TSV出力
            out.write(f"{page_id}\t{title}\t{lines_joined}\t{url}\n")

if __name__ == "__main__":
    main()
