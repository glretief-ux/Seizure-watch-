#!/usr/bin/env python3
"""Writes board/data.js (the data for the open-source seizure board artifact) from the latest dashboard build.
Usage: python scripts/build_board.py   (reads docs/index.html, which run_daily.py rebuilds every hour)."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
h = open(os.path.join(ROOT, "docs", "index.html"), encoding="utf-8").read()
D = json.loads(re.search(r'id="data">(.*?)</script>', h, re.S).group(1))
geo = json.loads(re.search(r"const GEO = (\{.*?\});\n", h, re.S).group(1))
ev = []
for e in D["events"]:
    ev.append({"i": e["id"], "d": e["date"], "it": e.get("drug_label") or e["drug"], "ca": e.get("category") or "Drug",
               "c": e.get("country"), "p": e.get("place"), "o": e.get("origin"), "de": e.get("dest"), "t": e.get("transit"),
               "co": e.get("conceal"), "tr": e.get("transport") if e.get("transport") != "Unknown" else None,
               "kg": e.get("kg"), "u": e.get("units"), "ut": e.get("unit_type"), "n": e.get("n"),
               "ti": (e.get("title_en") or e.get("title") or "")[:170], "ur": e.get("url"), "ou": (e.get("outlets") or "")[:60],
               "ar": e.get("arrests")})
out = {"asof": D["meta"]["asof"], "generated": D["meta"]["generated"], "first": D["meta"]["first_date"],
       "geo": {k: v for k, v in geo["c"].items()}, "events": ev}
path = os.path.join(ROOT, "board", "data.js")
open(path, "w", encoding="utf-8").write("window.OSD=" + json.dumps(out, ensure_ascii=False, separators=(",", ":"), default=lambda x: None) + ";")
print(len(ev), "events,", round(os.path.getsize(path) / 1e6, 2), "MB")

# also publish a copy on the GitHub Pages site (docs/board/), so the board has a normal web link
import shutil
dst = os.path.join(ROOT, "docs", "board"); os.makedirs(dst, exist_ok=True)
for f in ("index.html", "data.js", "world.js", "pccp-logo-banner.jpg"):
    shutil.copy2(os.path.join(ROOT, "board", f), os.path.join(dst, f))
print("copied to docs/board/")
