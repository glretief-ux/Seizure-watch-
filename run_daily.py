#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seizure Watch - daily run.

  python run_daily.py            # real run: search the web, extract, analyse, write docs/
  python run_daily.py --demo     # offline demo with invented sample articles (separate database)
  python run_daily.py --reanalyse   # skip searching; just rebuild the analysis/report from stored data
"""
import argparse
import datetime as dt
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from swatch import db, collect, extract, analyze, report  # noqa: E402


def log(*a):
    print(*a, flush=True)


def ingest(conn, items, is_demo=False):
    """Extract facts from each item and store. Returns (stored, relevant)."""
    stored = relevant = 0
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    for it in items:
        rec = extract.extract(it["title"], it.get("text", ""), it.get("source_country"))
        rec.update({
            "url": it["url"], "title": it["title"], "title_key": db.title_key(it["title"], it.get("source")),
            "source": it.get("source"), "published": it.get("published"), "fetched": now,
            "lang": it.get("lang"), "source_country": it.get("source_country"),
            "text_mode": it.get("text_mode", "snippet"), "is_demo": int(is_demo),
        })
        art_id = db.insert_article(conn, rec)
        if art_id is None:
            continue
        stored += 1
        if rec["relevant"]:
            db.assign_event(conn, art_id)
            relevant += 1
    conn.commit()
    return stored, relevant


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.path.join(HERE, "config.yaml"))
    ap.add_argument("--demo", action="store_true", help="use invented sample articles (offline)")
    ap.add_argument("--reanalyse", action="store_true", help="skip collection, rebuild analysis from the database")
    ap.add_argument("--days", type=int, help="override lookback days (e.g. 30 for a first back-fill)")
    ap.add_argument("--out", default=os.path.join(HERE, "docs"))
    ap.add_argument("--send-bulletin", action="store_true", help="e-mail the weekly bulletin now (needs the mail secrets)")
    args = ap.parse_args()

    cfg = yaml.safe_load(open(args.config, encoding="utf-8"))
    db_path = os.path.join(HERE, "data", "demo.db" if args.demo else "seizure_watch.db")
    if args.demo and os.path.exists(db_path):
        os.remove(db_path)
    conn = db.connect(db_path)
    today = dt.date.today()

    if args.demo:
        items = __import__("swatch.demo", fromlist=["demo_articles"]).demo_articles(today)
        log(f"Demo mode: {len(items)} invented articles")
        stored, rel = ingest(conn, items, is_demo=True)
        log(f"Stored {stored}; {rel} look like seizure reports")
    elif not args.reanalyse:
        days = args.days or cfg["run"]["lookback_days"]
        log(f"[1/4] Searching the web (last {days} day(s))...")
        items = collect.collect(cfg, days)
        cutoff = (today - dt.timedelta(days=days + 1)).isoformat()
        items = collect.prefilter(items, cutoff)
        seen_urls, seen_titles = db.known_urls(conn), db.known_title_keys(conn, 30)
        new = [i for i in items if i["url"] not in seen_urls and db.title_key(i["title"], i.get("source")) not in seen_titles]
        new = new[: cfg["run"]["max_articles_per_run"]]
        log(f"      {len(items)} candidate headlines, {len(new)} new")
        log("[2/4] Reading articles...")
        if cfg["run"]["fetch_full_text"]:
            new = collect.fetch_all(new, cfg["run"]["resolve_google_links"])
        else:
            for i in new:
                i["text"], i["text_mode"] = i.get("snippet", ""), "snippet"
        log("[3/4] Extracting facts and storing...")
        stored, rel = ingest(conn, new)
        log(f"      stored {stored}, of which {rel} are seizure reports")

    log("[4/4] Analysing and building report...")
    res = analyze.run(conn, cfg)
    if res is None:
        log("No seizure events stored yet - nothing to analyse. Try again after the first successful collection.")
        return 0
    db.save_alerts(conn, res["asof"].strftime("%Y-%m-%d"), res["alerts"])
    out = report.write_all(res, args.out, cfg, demo=args.demo)
    log(f"Done. {out['events']} events in report, {out['alerts']} alerts.")
    bcfg = cfg.get("bulletin", {}) or {}
    if bcfg.get("enabled", True):
        from swatch import bulletin
        b = bulletin.build(res, cfg, args.out)
        log(f"Weekly bulletin written ({os.path.join(args.out, 'bulletin.html')}).")
        if not args.demo:
            last = db.get_meta(conn, "bulletin_sent")
            if args.send_bulletin or bulletin.is_due(last, today, bcfg.get("weekday", 0)):
                ok, msg = bulletin.send_email(b)
                log(f"Bulletin e-mail: {msg}")
                if ok:
                    db.set_meta(conn, "bulletin_sent", today.isoformat())
    log(f"Open: {os.path.join(args.out, 'index.html')}")
    for a in res["alerts"][:8]:
        log(f"  [{a['severity']:6}] {a['type']}: {a['title']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
