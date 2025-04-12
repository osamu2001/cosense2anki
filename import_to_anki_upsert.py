import csv
import requests
import sys
import json
# import time # 不要になった

ANKI_CONNECT_URL = "http://localhost:8765"

def find_note_ids(field_id):
    payload = {
        "action": "findNotes",
        "version": 6,
        "params": {"query": f"id:{field_id}"}
    }
    try:
        r = requests.post(ANKI_CONNECT_URL, json=payload)
        r.raise_for_status()
        return r.json()["result"]
    except Exception as e:
        print(f"[find_note_ids] Error: {e}", file=sys.stderr)
        return []

def get_notes_info(note_ids):
    if not note_ids:
        return []
    payload = {
        "action": "notesInfo",
        "version": 6,
        "params": {"notes": note_ids}
    }
    try:
        r = requests.post(ANKI_CONNECT_URL, json=payload)
        r.raise_for_status()
        res = r.json()
        # print(f"[get_notes_info] response: {json.dumps(res, ensure_ascii=False)}", file=sys.stderr)
        return res["result"]
    except Exception as e:
        print(f"[get_notes_info] Error: {e}", file=sys.stderr)
        return []

def update_note(note_id, fields):
    fields_for_update = {k: v for k, v in fields.items() if k != "tags"}
    payload = {
        "action": "updateNoteFields",
        "version": 6,
        "params": {"note": {"id": note_id, "fields": fields_for_update}}
    }
    try:
        # print(f"[update_note] payload: {json.dumps(payload, ensure_ascii=False)}", file=sys.stderr)
        r = requests.post(ANKI_CONNECT_URL, json=payload)
        r.raise_for_status()
        res = r.json()
        # print(f"[update_note] response: {json.dumps(res, ensure_ascii=False)}", file=sys.stderr)
        if res.get("error"):
            print(f"[update_note] Error updating note {note_id}: {res['error']}", file=sys.stderr)
        return res
    except Exception as e:
        print(f"[update_note] Exception: {e}", file=sys.stderr)
        return None

def update_note_tags(note_id, tags):
    payload = {
        "action": "updateNoteTags",
        "version": 6,
        "params": {
            "note": note_id,
            "tags": tags
        }
    }
    try:
        # print(f"[update_note_tags] payload: {json.dumps(payload, ensure_ascii=False)}", file=sys.stderr)
        r = requests.post(ANKI_CONNECT_URL, json=payload)
        r.raise_for_status()
        res = r.json()
        # print(f"[update_note_tags] response: {json.dumps(res, ensure_ascii=False)}", file=sys.stderr)
        if res.get("error"):
            print(f"[update_note_tags] Error updating tags for note {note_id}: {res['error']}", file=sys.stderr)
        return res
    except Exception as e:
        print(f"[update_note_tags] Exception: {e}", file=sys.stderr)
        return None

def add_note(fields, tags):
    payload = {
        "action": "addNotes",
        "version": 6,
        "params": {"notes": [{
            "deckName": "QA on scrapbox",
            "modelName": "QA on scrapbox",
            "fields": fields, # addNotesではtagsフィールドもそのまま渡す
            "tags": tags
        }]}
    }
    try:
        r = requests.post(ANKI_CONNECT_URL, json=payload)
        r.raise_for_status()
        res = r.json()
        if res.get("error"):
            print(f"[add_note] Error adding note: {res['error']}", file=sys.stderr)
        return res
    except Exception as e:
        print(f"[add_note] Exception: {e}", file=sys.stderr)
        return None

def main():
    updated_count = 0
    added_count = 0
    skipped_count = 0
    error_count = 0
    no_change_count = 0 # 変更なしでスキップした件数

    try:
        with open("output.tsv", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                if len(row) != 5:
                    print(f"[main] Skipped row (invalid column count): {row}", file=sys.stderr)
                    skipped_count += 1
                    continue
                id_, title, lines, url, tags_str = row

                # TSVからのデータ
                tsv_fields = {
                    "id": id_,
                    "title": title,
                    "lines": lines,
                    "url": url,
                    # "tags" は比較用には不要
                }
                tsv_tags = sorted(tags_str.split()) if tags_str else [] # 比較用にソート

                note_ids = find_note_ids(id_)
                if note_ids:
                    notes_info = get_notes_info(note_ids)
                    if notes_info:
                        note_info = notes_info[0]
                        note_id = note_info["noteId"]

                        # Anki上の既存データ
                        anki_fields = {k: v["value"] for k, v in note_info["fields"].items() if k != "tags"}
                        anki_tags = sorted(note_info["tags"]) # 比較用にソート

                        # フィールド内容の比較 (tagsを除く)
                        fields_changed = False
                        for field_name, tsv_value in tsv_fields.items():
                            if field_name in anki_fields and anki_fields[field_name] != tsv_value:
                                fields_changed = True
                                break
                            elif field_name not in anki_fields: # Anki側にフィールドがない場合も変更とみなす
                                fields_changed = True
                                break

                        # タグ内容の比較 (順序無視)
                        tags_changed = (anki_tags != tsv_tags)

                        # 変更がある場合のみ更新APIを呼び出す
                        if fields_changed or tags_changed:
                            print(f"Updating note: {id_} (Fields changed: {fields_changed}, Tags changed: {tags_changed})")
                            res = None
                            tags_res = None
                            if fields_changed:
                                # update_note には tags を含まない fields を渡す
                                res = update_note(note_id, {"id": id_, "title": title, "lines": lines, "url": url})
                            if tags_changed:
                                tags_res = update_note_tags(note_id, tsv_tags) # tsv_tagsはソート済みリスト

                            # API呼び出し結果を確認
                            update_successful = True
                            if fields_changed and (not res or res.get("error")):
                                update_successful = False
                            if tags_changed and (not tags_res or tags_res.get("error")):
                                update_successful = False

                            if update_successful:
                                updated_count += 1
                            else:
                                error_count += 1
                        else:
                            print(f"Skipped (no change): {id_}")
                            no_change_count += 1
                    else:
                        print(f"[main] No notesInfo found for id={id_}, skipping update.", file=sys.stderr)
                        skipped_count += 1
                else:
                    # 新規追加
                    print(f"Adding new note: {id_}")
                    # add_note には tags フィールドを含む元の fields と tags リストを渡す
                    add_fields = {
                        "id": id_, "title": title, "lines": lines, "url": url, "tags": tags_str
                    }
                    res = add_note(add_fields, tsv_tags) # tsv_tagsはソート済みリスト
                    if res and not res.get("error"):
                        added_count += 1
                    else:
                        error_count += 1

    except Exception as e:
        print(f"[main] Exception: {e}", file=sys.stderr)
        error_count += 1

    print("\n=== Import Summary ===")
    print(f"Updated: {updated_count}件")
    print(f"Added:   {added_count}件")
    print(f"Skipped (no change): {no_change_count}件")
    print(f"Skipped (invalid row): {skipped_count}件")
    print(f"Error:   {error_count}件")

if __name__ == "__main__":
    main()