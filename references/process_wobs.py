#!/usr/bin/env python3

"""
take wobs.json file extracted from coppermind and turn into human readable format, for easy
searching as well as future indexing
"""

import re
import json


def process_record(r: dict) -> str:
    records = [
        r.get("event_name", "UNKNOWN-EVENT") + " - " + r.get("date", "UNKNOWN-DATE")
    ]
    records.append(
        "TAGS: " + (", ".join(r.get("tags", [])) if r.get("tags", []) else "NO-TAGS")
    )
    records.append(
        "CONVERSATION" + (" (PARAPHRASED):" if r.get("paraphrased", True) else ":")
    )
    for blurb in r.get("lines", []):
        speaker = blurb.get("speaker", "QUESTIONER").upper()
        text = re.sub("<.*?>", "", blurb.get("text", "")).replace("\n", "")
        records.append(f"- {speaker}: {text}")
    records.append(
        "NOTES: " + (r.get("notes", "NO-NOTES") if r.get("notes") else "NO-NOTES")
    )
    return "\n".join(records) + "\n\n"


# load extracted wobs json file
with open("references/wobs/wobs.json", "r") as f:
    wobs = json.load(f)

# iterate over all wobs and turn into human readable format
with open("references/wobs/wobs-human_readable.txt", "w") as f:
    for block in wobs:
        f.write(process_record(block))
