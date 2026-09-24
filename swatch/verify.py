# -*- coding: utf-8 -*-
"""
Officer verification feedback loop.

data/verifications.csv is a file YOU edit (via the GitHub website, same
as anything else in this repo) - not something the pipeline writes to.
Add a row for any event you've checked against a confirmed case:

    event_id,status,note
    482,verified,matches CEN/nCEN case #2026-1187
    501,false_positive,headline was about a training exercise, not a real seizure

`event_id` is the number shown in the "Event ID" column of
seizure_watch.xlsx / events.csv - it's stable once assigned (an event
keeps the same id for as long as it exists), so rows here stay valid
across future runs. `status` should be exactly "verified" or
"false_positive" (anything else is ignored rather than guessed at).
`note` is optional free text, e.g. a reference to the matching case in
your CEN/nCEN records.

If the file doesn't exist yet, or a row is malformed, this degrades to
"nothing verified" rather than breaking the run - same fail-safe pattern
as translate.py and ner.py.
"""
import csv
import os


def load(path):
    """Returns {event_id: {"status": ..., "note": ...}}. Empty dict if the
    file is missing or unreadable."""
    if not os.path.exists(path):
        return {}
    out = {}
    try:
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                try:
                    eid = int(row.get("event_id", "").strip())
                except (ValueError, AttributeError):
                    continue
                status = (row.get("status") or "").strip().lower()
                if status not in ("verified", "false_positive"):
                    continue
                out[eid] = {"status": status, "note": (row.get("note") or "").strip()}
    except Exception:
        return {}
    return out
