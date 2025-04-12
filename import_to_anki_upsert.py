import csv
import requests
import sys

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
        return r.json()["result"]
    except Exception as e:
        print(f"[get_notes_info] Error: {e}", file=sys.stderr)
        return []

def update_note(note_id, fields):
    payload = {
        "action": "updateNoteFields",
        "version": 6,
        "params": {"note": {"id": note_id, "fields": fields}}
    }
    try:
        r = requests.post(ANKI_CONNECT_URL, json=payload)
        r.raise_for_status()
        res = r.json()
        if res.get("error"):
            print(f"[update_note] Error updating note {note_id}: {res['error']}", file=sys.stderr)
        return res
    except Exception as e:
        print(f"[update_note] Exception: {e}", file=sys.stderr)
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
    try:
        with open("output.tsv", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                if len(row) != 5:
                    print(f"[main] Skipped row (invalid column count): {row}", file=sys.stderr)
                    skipped_count += 1
                    continue
                id_, title, lines, url, tags_str = row
                fields = {
                    "id": id_,
                    "title": title,
                    "lines": lines,
                    "url": url,
                    "tags": tags_str
                }
                tags = tags_str.split() if tags_str else []
                note_ids = find_note_ids(id_)
                if note_ids:
                    notes_info = get_notes_info(note_ids)
                    if notes_info:
                        note_id = notes_info[0]["noteId"]
                        res = update_note(note_id, fields)
                        if res and not res.get("error"):
                            updated_count += 1
                        else:
                            error_count += 1
                        print(f"Updated: {id_}")
                    else:
                        print(f"[main] No notesInfo found for id={id_}, skipping update.", file=sys.stderr)
                        skipped_count += 1
                else:
                    res = add_note(fields, tags)
                    if res and not res.get("error"):
                        added_count += 1
                    else:
                        error_count += 1
                    print(f"Added: {id_}")
    except Exception as e:
        print(f"[main] Exception: {e}", file=sys.stderr)
        error_count += 1

    print("\n=== Import Summary ===")
    print(f"Updated: {updated_count}件")
    print(f"Added:   {added_count}件")
    print(f"Skipped: {skipped_count}件")
    print(f"Error:   {error_count}件")

if __name__ == "__main__":
    main()