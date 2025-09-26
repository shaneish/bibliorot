#!/usr/bin/env python3

"""
take wobs.json file extracted from coppermind and turn into human readable format, for easy
searching as well as future indexing
"""

import re
import json


def process_record(r: dict) -> str:
    event_id = r.get('event', '')
    question_id = r.get('id', '<ID>')
    records = ["---", "\n", f"# Event ID - {event_id}, Question ID - {question_id}"]
    records.append(
            f'- EVENT: {r.get("event_name", "UNKNOWN-EVENT")} - {r.get("date", "UNKNOWN-DATE")}'
    )
    records.append(
            f"- TAGS: {', '.join(r.get('tags', []))}"
    )
    records.append(
        f"- URL: https://wob.coppermind.net/events/{event_id}/#e{question_id}"
    )
    records.append(
            f"- CONVERSATION {'(PARAPHRASED)' if r.get('paraphrased', True) else ''}:"
    )
    for blurb in r.get("lines", []):
        speaker = re.sub("<.*?>", "", blurb.get("speaker", "QUESTIONER")).replace("\n", "").upper()
        text = re.sub("<.*?>", "", blurb.get("text", "")).replace("\n", "").replace("&nbsp;", "")
        records.append(f"> **{speaker}**: {text}")
        records.append(">")
    note = (
        r.get("note", "")
        .replace("../../../", "https://wob.coppermind.net/")
        .replace("<i>", "*")
        .replace("<\\i>", "*")
        .replace("<b>", "**")
        .replace("<\\b>", "**")
    )
    if note:
        records.append(f"- NOTES: {note}")
    return "\n".join(records) + "\n"


# load extracted wobs json file
with open("wobs/wobs.json", "r") as f:
    wobs = json.load(f)

# iterate over all wobs and turn into human readable format
with open("wobs/wobs.md", "w") as f:
    for block in wobs:
        f.write(process_record(block))
