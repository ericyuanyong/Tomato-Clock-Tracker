
import os
import json
import sqlite3
import requests
from sseclient import SSEClient
import time 
from urllib.parse import quote



EVENT_NAME = "tomato/pressed"
TOKEN = os.environ.get("PARTICLE_TOKEN")  # export PARTICLE_TOKEN="..."
DB_PATH = os.environ.get("TOMATO_DB")
STREAM_URL = f"https://api.particle.io/v1/events/{quote(EVENT_NAME, safe='')}?access_token={TOKEN}"

def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tomato_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            published_at TEXT NOT NULL,
            coreid TEXT,
            name TEXT,
            data TEXT
        )
    """)
    con.commit()
    con.close()

def insert_event(ev: dict):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        "INSERT INTO tomato_events (published_at, coreid, name, data) VALUES (?, ?, ?, ?)",
        (ev.get("published_at"), ev.get("coreid"), ev.get("name"), ev.get("data")),
    )
    con.commit()
    con.close()


def stream_events(stream_url: str):
    # requests stream, then hand the response to SSEClient
    resp = requests.get(stream_url, stream=True, timeout=60)
    resp.raise_for_status()

    client = SSEClient(resp)
    for event in client.events():   # ✅ this is the key difference
        if not event.data:
            continue
        yield event.data


def main():
    init_db()
    print("Listening:", STREAM_URL)

    while True:
        try:
            for data in stream_events(STREAM_URL):
                ev = json.loads(data)
                insert_event(ev)
                print("Recorded:", ev.get("published_at"), ev.get("coreid"))
        except Exception as e:
            print("Stream error, reconnecting:", repr(e))
            time.sleep(2)

if __name__ == "__main__":
    main()