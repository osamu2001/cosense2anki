import csv
import requests
import sys
import json
import time # デバッグ用に追記したが不要になった

ANKI_CONNECT_URL = "http://localhost:8765"
# TARGET_ID = "67f9f89cdffb412a3f635c0e" # デバッグ対象のID指定を解除

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
        # デバッグ用にnotesInfoのレスポンスも表示していたがコメントアウト
        # print(f"[get_notes_info] response: {json.dumps(res, ensure_ascii=False)}", file=sys.stderr)
        return res["result"]
    except Exception as e:
        print(f"[get_notes_info] Error: {e}", file=sys.stderr)
        return []

def update_note(note_id, fields):
    # tagsはupdateNoteFieldsでは更新できないので除外
    fields_for_update = {k: v for k, v in fields.items() if k != "tags"}

    # --- デバッグ用: linesフィールドに強制的に追記していた処理を削除 ---
    # if "lines" in fields_for_update:
    #     fields_for_update["lines"] += f"_updated_{int(time.time())}"
    # --- デバッグ用ここまで ---

    payload = {
        "action": "updateNoteFields",
        "version": 6,
        "params": {"note": {"id": note_id, "fields": fields_for_update}}
    }
    try:
        # デバッグ用のpayload表示もコメントアウト
        # print(f"[update_note] payload: {json.dumps(payload, ensure_ascii=False)}", file=sys.stderr)
        r = requests.post(ANKI_CONNECT_URL, json=payload)
        r.raise_for_status()
        res = r.json()
        # デバッグ用のresponse表示もコメントアウト
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
        # デバッグ用のpayload表示もコメントアウト
        # print(f"[update_note_tags] payload: {json.dumps(payload, ensure_ascii=False)}", file=sys.stderr)
        r = requests.post(ANKI_CONNECT_URL, json=payload)
        r.raise_for_status()
        res = r.json()
        # デバッグ用のresponse表示もコメントアウト
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
            "fields": fields,
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
    # found_target = False # 対象IDが見つかったかどうかのフラグも不要に

    try:
        with open("output.tsv", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                if len(row) != 5:
                    print(f"[main] Skipped row (invalid column count): {row}", file=sys.stderr)
                    skipped_count += 1
                    continue
                id_, title, lines, url, tags_str = row

                # --- デバッグ用: 特定IDのみ処理していた箇所を削除 ---
                # if TARGET_ID and id_ != TARGET_ID:
                #     continue
                # found_target = True # 対象IDが見つかった
                # --- デバッグ用ここまで ---

                fields = {
                    "id": id_,
                    "title": title,
                    "lines": lines,
                    "url": url,
                    "tags": tags_str # tagsフィールドも一旦保持
                }
                tags = tags_str.split() if tags_str else []
                note_ids = find_note_ids(id_)
                if note_ids:
                    notes_info = get_notes_info(note_ids)
                    if notes_info:
                        note_id = notes_info[0]["noteId"]
                        # update_note には tags を含まない fields を渡す
                        res = update_note(note_id, fields)
                        tags_res = update_note_tags(note_id, tags)
                        if (res and not res.get("error")) and (tags_res and not tags_res.get("error")):
                            updated_count += 1
                        else:
                            # どちらかでエラーがあればエラーカウント
                            error_count += 1
                        # print(f"Updated: {id_}") # 逐次表示もコメントアウト（サマリーで表示するため）
                    else:
                        print(f"[main] No notesInfo found for id={id_}, skipping update.", file=sys.stderr)
                        skipped_count += 1
                else:
                    # add_note には tags を含む fields を渡す
                    res = add_note(fields, tags)
                    if res and not res.get("error"):
                        added_count += 1
                    else:
                        error_count += 1
                    # print(f"Added: {id_}") # 逐次表示もコメントアウト

                # 対象IDが見つかったらループを抜ける処理も削除
                # if found_target:
                #     break

    except Exception as e:
        print(f"[main] Exception: {e}", file=sys.stderr)
        error_count += 1

    # 対象IDが見つからなかった場合のメッセージも削除
    # if TARGET_ID and not found_target:
    #     print(f"[main] Target ID {TARGET_ID} not found in output.tsv", file=sys.stderr)

    print("\n=== Import Summary ===")
    print(f"Updated: {updated_count}件")
    print(f"Added:   {added_count}件")
    print(f"Skipped: {skipped_count}件")
    print(f"Error:   {error_count}件")

if __name__ == "__main__":
    main()