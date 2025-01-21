#!/usr/bin/env python3

"""
pull all available wobs from the coppermind and store in db and json file
"""

import requests
import sqlite3
import time
import json

BASE_WOB_URL = "https://wob.coppermind.net/api/"
BASE_WOB_ENTRIES_URL = BASE_WOB_URL + "entry/?format=json"
WOB_ENTRY_URL = BASE_WOB_URL + "entry/?page={}&format=json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0"
}
COLS = [
    "id",
    "event",
    "event_name",
    "event_date",
    "event_state",
    "date",
    "paraphrased",
    "modified_date",
    "tags",
    "lines",
    "note",
]


def convert_rows(l: list[dict], entries_page: str = "0") -> list[tuple]:
    return [tuple([str(d.get(k, "")) for k in COLS] + [entries_page]) for d in l]


# setup sqlite stuff and create new db/table if needed
# both json and sqlite output are used because json is easier to use
# in the near term, but ultimately i'd like to build an embedding index
# over the wobs for better search -- and that can be done with sqlite extensions
con = sqlite3.connect("references/wobs/wobs.db")
cur = con.cursor()
if (
    cur.execute(
        "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='wobs'"
    ).fetchone()[0]
    == 0
):
    create_resp = cur.execute("""CREATE TABLE wobs(
        id INTEGER DEFAULT 0,
        event INTEGER DEFAULT 0,
        event_name TEXT DEFAULT "",
        event_date TEXT DEFAULT "",
        event_state TEXT DEFAULT "",
        date TEXT DEFAULT "",
        paraphrased TEXT DEFAULT "",
        modified_date TEXT DEFAULT "",
        tags JSON DEFAULT('[]'),
        lines JSON DEFAULT('[]'),
        note TEXT DEFAULT "",
        entries_page INTEGER DEFAULT "0"
    )""")


# below chunk iterates over all entries until end is found, each entry will get pushed
# into a list for jsonification as well as inserted into sqlite db
r = requests.get(BASE_WOB_ENTRIES_URL, headers=HEADERS)
json_entries = []
current_page = "0"
record_cnt = 0
while r.json().get("results", []):
    entries = r.json()["results"]
    next = r.json().get("next")
    record_cnt = record_cnt + len(entries)
    json_entries = json_entries + entries
    rows = convert_rows(entries, current_page)
    try:
        current_page = next.split("page=")[-1].split("=")[0]
    except:
        break
    else:
        print(f"on page {current_page}, processed {record_cnt} records...")
        res = cur.executemany(
            "INSERT INTO wobs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", rows
        )
        con.commit()
        r = requests.get(next, headers=HEADERS)
        time.sleep(2)  # hopefully avoid api limits lmao

# dump into json file as well
with open("references/wobs/wobs.json", "w") as f:
    json.dump(json_entries, f, indent=4)
