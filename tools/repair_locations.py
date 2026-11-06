#!/usr/bin/env python3
"""One-off repair of stored locations after the outlet-country / Algerian-places fix (2026-11-06).
Re-reads each relevant report's headline only (article bodies are not stored) and changes a row ONLY when:
  a) it has no town and low/medium confidence, and the headline now names a town (high confidence);
  b) a national outlet's own country is the origin but a bare mention of another country became the seizure country (home case);
  c) the country is a low-confidence guess from the Google News edition and the outlet's domain says otherwise;
  e) the headline names a different country than a town met later in the body (headline wins);
  f) statistics headlines ("rise in cocaine seizures") are not events and are switched off;
  d) it had no country and the headline now gives one from the text itself (a town, agency or currency), not from the outlet guess.
Rows with a high-confidence town are never touched. Usage: python tools/repair_locations.py [--dry-run]"""
import os, sys, sqlite3
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from swatch import extract, lexicon as L, db  # noqa: E402

dry = "--dry-run" in sys.argv
sample = "--sample" in sys.argv
import random; random.seed(1)
conn = sqlite3.connect(os.path.join(ROOT, "data", "seizure_watch.db")); conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT * FROM articles WHERE relevant=1").fetchall()
stats = [r["id"] for r in rows if L.EXCLUDE.search(L.norm((r["title"] or "") + " " + (r["title_en"] or "")))]
if stats and not dry:
    conn.execute("UPDATE articles SET relevant=0 WHERE id IN (%s)" % ",".join("?" * len(stats)), stats)
print(len(stats), "statistics headlines set to not-an-event:", stats)
rows = [r for r in rows if r["id"] not in set(stats)]
changed = {"a": 0, "b": 0, "c": 0, "d": 0, "e": 0, "x": 0}; examples = []
for r in rows:
    outlet = L.outlet_country(r["url"])
    new = extract.locate(r["title"], outlet or r["source_country"] or L.LANG_COUNTRY.get(r["lang"]), outlet)
    old_conf, old_place, old_c = r["location_conf"], r["seizure_place"], r["seizure_country"]
    upd, why = None, None
    if old_conf != "high" and not old_place and new["seizure_place"] and new["location_conf"] == "high" and new["seizure_country"] != old_c:
        upd, why = {k: new[k] for k in db.LOCATION_COLS}, "a"
    elif outlet and r["origin"] == outlet and old_c and old_c != outlet and old_conf != "high" and not old_place:
        upd = {"seizure_country": outlet, "seizure_place": None, "location_conf": "medium", "origin": None, "origin_place": None}
        why = "b"
    elif outlet and old_conf == "low" and not old_place and old_c and old_c != outlet and new["seizure_country"] == outlet:
        upd, why = {"seizure_country": outlet}, "c"      # still a low-confidence guess
    elif not old_c and new["seizure_country"] and new["location_conf"] in ("medium", "high"):
        upd, why = {k: new[k] for k in db.LOCATION_COLS if new[k] is not None}, "d"
    if not upd and new["location_conf"] in ("high", "medium") and new["seizure_country"] and old_c and new["seizure_country"] != old_c \
            and (old_place or old_conf == "high") and len(extract.title_countries(L.norm(r["title"]))) == 1:
        # e) the headline names a country or town and the stored one came from a different town met later in the body
        upd, why = {k: new[k] for k in ("seizure_country", "seizure_place", "location_conf")}, "e"
        keep = {k: r[k] for k in ("origin", "origin_place", "destination", "destination_place", "transit")}
        for k, pk in (("origin", "origin_place"), ("destination", "destination_place")):
            if keep[k] == new["seizure_country"]:
                keep[k] = keep[pk] = None
        tr = [x for x in (keep["transit"] or "").split("|") if x and x != new["seizure_country"]]
        upd.update(origin=keep["origin"], origin_place=keep["origin_place"], destination=keep["destination"],
                   destination_place=keep["destination_place"], transit="|".join(tr) or None)
        upd["corridor"], upd["route"] = extract.compose_route(keep["origin"], keep["destination"], tr, new["seizure_country"])
    if not upd:
        continue
    merged = {**dict(r), **upd}
    transit = [x for x in (merged["transit"] or "").split("|") if x and x != merged["seizure_country"] and x != merged["origin"]]
    if why in ("b", "c"):
        upd["transit"] = "|".join(transit) or None
        upd["corridor"], upd["route"] = extract.compose_route(merged["origin"], merged["destination"], transit, merged["seizure_country"])
    changed[why] += 1
    if (why in ("a", "b", "e") and not sample) or (sample and why in ("c", "d") and random.random() < 0.07):
        examples.append((r["id"], why, old_c, "->", upd.get("seizure_country", old_c), upd.get("seizure_place"), (r["title_en"] or r["title"])[:60]))
    if not dry:
        conn.execute("UPDATE articles SET " + ", ".join(f"{k}=?" for k in upd) + " WHERE id=?", [*upd.values(), r["id"]])
if not dry:
    conn.commit()
print(changed, "dry-run" if dry else "written")
for e in examples: print(e)
