import os

import dotenv
import requests


dotenv.load_dotenv()

DIFY_URL = os.getenv("DIFY_URL")
DIFY_APP_ID = os.getenv("DIFY_APP_ID")

BASE_URL = f"{DIFY_URL}/console/api/apps/{DIFY_APP_ID}"
CONVERSATION_URL = f"{BASE_URL}/chat-conversations"


DIFY_CONSOLE_API_KEY = os.getenv("DIFY_CONSOLE_API_KEY")
HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "authorization": f"Bearer {DIFY_CONSOLE_API_KEY}",
    "content-type": "application/json",
    "referer": f"{BASE_URL}/logs",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
}

print(CONVERSATION_URL)
print(HEADERS)


def fetch_all_session_ids(dify_console_url: str, limit: int = 50):
    session_ids = []
    page = 1
    while True:
        print(f"Feching page {page}", flush=True)
        url = f"{dify_console_url}?page={page}&limit={limit}&sort_by=-created_at&annotation_status=all"
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        session_ids.extend(
            [
                item["from_end_user_session_id"]
                for item in data.get("data", [])
                if "from_end_user_session_id" in item
            ]
        )
        if not data.get("has_more"):
            break
        page += 1
    print(f"Num converstaion before set: {len(session_ids)}")
    session_ids = set(session_ids)
    print(f"Num converstaion after set: {len(session_ids)}")
    return session_ids


if __name__ == "__main__":
    session_ids = fetch_all_session_ids(dify_console_url=CONVERSATION_URL)
    for sid in session_ids:
        print(sid)
