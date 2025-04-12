import requests

ANKI_CONNECT_URL = "http://localhost:8765"

def check_anki_connect():
    payload = {
        "action": "version",
        "version": 6
    }
    try:
        r = requests.post(ANKI_CONNECT_URL, json=payload, timeout=3)
        r.raise_for_status()
        res = r.json()
        if "result" in res and isinstance(res["result"], int):
            print(f"AnkiConnect OK (version: {res['result']})")
            return True
        else:
            print("AnkiConnect応答異常:", res)
            return False
    except Exception as e:
        print("AnkiConnectに接続できません:", e)
        return False

if __name__ == "__main__":
    check_anki_connect()
