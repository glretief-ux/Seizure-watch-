#!/usr/bin/env python3
"""Writes motion/data.js: the last 30 days of reports for the animated motion dashboard (reads board/data.js)."""
import json, os, datetime as dt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
raw = open(os.path.join(ROOT, "board", "data.js"), encoding="utf-8").read()
D = json.loads(raw[len("window.OSD="):-1])
end = dt.date.fromisoformat(D["asof"][:10]); start = end - dt.timedelta(days=29)
days = [(start + dt.timedelta(days=i)).isoformat() for i in range(30)]
idx = {d: i for i, d in enumerate(days)}
ev = []
for e in D["events"]:
    i = idx.get((e.get("d") or "")[:10])
    if i is None: continue
    ev.append([i, e["it"], e.get("c"), round(e["kg"], 1) if e.get("kg") else 0, e.get("ca") or "Drug"])
ev.sort(key=lambda r: r[0])
used = {r[2] for r in ev if r[2]}
out = {"asof": D["asof"], "days": days, "geo": {k: v for k, v in D["geo"].items() if k in used}, "ev": ev}
path = os.path.join(ROOT, "motion", "data.js")
open(path, "w", encoding="utf-8").write("window.MOT=" + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";")
print(len(ev), "events", days[0], "->", days[-1], round(os.path.getsize(path) / 1e3), "KB")
