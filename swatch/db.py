# -*- coding: utf-8 -*-
"""SQLite store. One row per article; articles about the same seizure share an event_id."""
import os
import re
import sqlite3
from .lexicon import norm, slug

SCHEMA = """
CREATE TABLE IF NOT EXISTS articles(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  url TEXT UNIQUE, title TEXT, title_key TEXT, source TEXT, published TEXT, fetched TEXT,
  lang TEXT, source_country TEXT, text_mode TEXT, is_demo INTEGER DEFAULT 0,
  relevant INTEGER DEFAULT 0,
  primary_drug TEXT, drugs TEXT, qty_kg REAL, qty_units REAL, unit_type TEXT,
  concealment TEXT, concealment_detail TEXT, transport TEXT, in_container INTEGER,
  origin TEXT, origin_place TEXT, destination TEXT, destination_place TEXT, transit TEXT,
  seizure_country TEXT, seizure_place TEXT, location_conf TEXT,
  arrests INTEGER, organized INTEGER, insider INTEGER, controlled_delivery INTEGER, coverload INTEGER,
  route TEXT, corridor TEXT, mo_summary TEXT, completeness INTEGER, event_id INTEGER,
  vessel TEXT, shipping_line TEXT, container_numbers TEXT, cover_cargo TEXT, title_en TEXT, ner_places TEXT,
  infrastructure TEXT, category TEXT, drug_type TEXT, indicators TEXT
);
CREATE INDEX IF NOT EXISTS ix_pub ON articles(published);
CREATE INDEX IF NOT EXISTS ix_event ON articles(event_id);
CREATE TABLE IF NOT EXISTS alerts(
  run_date TEXT, severity TEXT, type TEXT, title TEXT, detail TEXT, urls TEXT
);
"""
COLS = None


def connect(path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    global COLS
    COLS = {r["name"] for r in conn.execute("PRAGMA table_info(articles)")}
    for col in ("vessel", "shipping_line", "container_numbers", "cover_cargo", "title_en", "ner_places",
                "infrastructure", "category", "drug_type", "indicators"):      # databases made by older versions
        if col not in COLS:
            conn.execute(f"ALTER TABLE articles ADD COLUMN {col} TEXT")
    COLS = {r["name"] for r in conn.execute("PRAGMA table_info(articles)")}
    # renamed labels (old name -> new name)
    for old, new in (("Unspecified protected timber", "Other CITES-protected wood"),):
        conn.execute("UPDATE articles SET primary_drug=? WHERE primary_drug=?", (new, old))
    conn.commit()
    conn.execute("CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT)")
    return conn


def title_key(title, source=None):
    t = norm(title)
    if source:
        t = re.sub(r"\s+-\s+" + re.escape(norm(source)) + r"\s*$", "", t)
    t = re.sub(r"\s+-\s+[^-]{2,40}$", "", t)          # strip trailing " - Outlet"
    return slug(t)[:90]


def known_urls(conn):
    return {r[0] for r in conn.execute("SELECT url FROM articles")}


def known_title_keys(conn, days=14):
    return {r[0] for r in conn.execute(
        "SELECT title_key FROM articles WHERE date(published) >= date('now', ?)", (f"-{days} day",))}


def insert_article(conn, rec):
    keys = [k for k in rec if k in COLS]
    cur = conn.execute(f"INSERT OR IGNORE INTO articles ({','.join(keys)}) VALUES ({','.join('?' * len(keys))})",
                       [rec[k] for k in keys])
    return cur.lastrowid if cur.rowcount else None


def fix_official_site_langs(conn, site_langs):
    """One-time correction for articles from an official-site search (config.yaml's
    official_sites) that were stored with lang='en' before each site's real
    language was tracked - so their headline never got translated. Resets lang
    to the site's real language and clears title_en so backfill_title_en()
    translates them properly on this run."""
    n = 0
    for site, lang in (site_langs or {}).items():
        if lang == "en":
            continue
        cur = conn.execute(
            "UPDATE articles SET lang=?, title_en=NULL WHERE url LIKE ? "
            "AND lang='en' AND (title_en IS NULL OR title_en=title)",
            (lang, f"%{site}%"))
        n += cur.rowcount
    if n:
        conn.commit()
    return n


def backfill_title_en(conn, translate_fn, limit=150):
    """One-time catch-up for articles stored before English titles existed,
    or where a translation call failed at the time. A failed/skipped call
    falls back to storing the original text as title_en unchanged (see
    translate.py), so "title_en still equals title" is included here as a
    sign the translation never actually happened, not just an empty value -
    otherwise those rows would stay untranslated forever with no retry.
    Translates up to `limit` per call, oldest first, so a large backlog
    clears itself over many runs instead of one slow run. Kept deliberately
    small: translate.py's per-call timeout still adds up across `limit` rows,
    and the whole GitHub Actions job only gets 45 minutes (see
    .github/workflows/daily.yaml) - a run of this ran long and got killed by
    that timeout once already with limit=2000 and no per-call cap."""
    rows = conn.execute(
        "SELECT id, title, lang FROM articles WHERE relevant=1 AND lang IS NOT NULL "
        "AND lang != 'en' AND (title_en IS NULL OR title_en = '' OR title_en = title) "
        "ORDER BY id LIMIT ?", (limit,)
    ).fetchall()
    n = 0
    for r in rows:
        en = translate_fn(r["title"], r["lang"])
        conn.execute("UPDATE articles SET title_en=? WHERE id=?", (en, r["id"]))
        n += 1
    if n:
        conn.commit()
    return n


_STOP = set("with from that this into after over their they were have been will which said says about "
            "more than also during near amid under police customs officers officials seized seizure seizes "
            "drugs drug worth million found".split())


from .lexicon import LANG_COUNTRY  # noqa: E402

LOCATION_COLS = ["seizure_country", "seizure_place", "location_conf", "origin", "origin_place", "destination",
                 "destination_place", "transit", "route", "corridor"]


def backfill_locations(conn, locate_fn, days=7):
    """Re-read the headline of every seizure report that has no country yet, now that the place list, agency and
    currency cues have grown. Only fills what is empty; never changes a country that was found before.
    Returns how many reports gained a country."""
    rows = conn.execute("SELECT id, title, COALESCE(source_country, ''), lang FROM articles WHERE relevant=1 AND seizure_country IS NULL "
                        "AND COALESCE(published, fetched) >= date('now', ?)", (f"-{int(days)} day",)).fetchall()
    gained = 0
    for r in rows:
        try:
            rec = locate_fn(r[1], r[2] or LANG_COUNTRY.get(r[3]))
        except Exception:
            continue
        if not rec.get("seizure_country"):
            continue
        sets = {c: rec.get(c) for c in LOCATION_COLS if rec.get(c) is not None}
        conn.execute("UPDATE articles SET " + ", ".join(f"{c}=?" for c in sets) + " WHERE id=?", [*sets.values(), r[0]])
        gained += 1
    conn.commit()
    return gained


def _tokens(title):
    """Words of 4+ letters (3+ in Arabic, Cyrillic, Devanagari); Chinese text is compared by pairs of characters."""
    t = slug(title)
    words = {w for w in t.split() if (len(w) >= 4 or (len(w) >= 3 and not w.isascii())) and w not in _STOP}
    for run in re.findall(r"[\u4e00-\u9fff]+", t):
        words |= {run[i:i + 2] for i in range(len(run) - 1)}
    return words


def _jaccard(a, b):
    return len(a & b) / len(a | b) if a and b else 0.0


def _days_apart(d1, d2):
    import datetime as dt
    try:
        return abs((dt.date.fromisoformat(d1[:10]) - dt.date.fromisoformat(d2[:10])).days)
    except Exception:
        return 99


def _same_amount(a, b):
    """True/False when both quantities are known and comparable; None when we cannot tell."""
    for k in ("qty_kg", "qty_units"):
        x, y = a[k], b[k]
        if x and y:
            return abs(x - y) / max(x, y) <= 0.08
    return None


def assign_event(conn, art_id):
    """Give a new relevant article an event_id: join an existing event if it looks like the same seizure.
    Rules: quantities must agree (within 8%) when both are known; then same country or a similar headline.
    With no quantity to compare, we need a very similar headline, the same country and <= 2 days apart."""
    a = conn.execute("SELECT * FROM articles WHERE id=?", (art_id,)).fetchone()
    cands = conn.execute(
        "SELECT * FROM articles WHERE relevant=1 AND event_id IS NOT NULL AND primary_drug=? AND id<>? "
        "AND date(published) BETWEEN date(?, '-7 day') AND date(?, '+7 day')",
        (a["primary_drug"], art_id, a["published"], a["published"])).fetchall()
    ta = _tokens(a["title"])
    for c in cands:
        sim = _jaccard(ta, _tokens(c["title"]))
        same_ctry = bool(a["seizure_country"] and c["seizure_country"] and a["seizure_country"] == c["seizure_country"])
        amount = _same_amount(a, c)
        if amount is False:
            continue
        both_ctry = bool(a["seizure_country"] and c["seizure_country"])
        if amount is True:
            if same_ctry:
                match = True
            elif both_ctry:                     # same amount but different countries: only near-identical headlines
                match = sim >= 0.8
            else:
                match = sim >= 0.3
        elif amount is None:
            match = sim >= 0.6 and same_ctry and _days_apart(a["published"], c["published"]) <= 2
        else:
            match = False
        if match:
            conn.execute("UPDATE articles SET event_id=? WHERE id=?", (c["event_id"], art_id))
            return c["event_id"]
    conn.execute("UPDATE articles SET event_id=? WHERE id=?", (art_id, art_id))
    return art_id


def save_alerts(conn, run_date, alerts):
    conn.execute("DELETE FROM alerts WHERE run_date=?", (run_date,))
    conn.executemany("INSERT INTO alerts VALUES (?,?,?,?,?,?)",
                     [(run_date, a["severity"], a["type"], a["title"], a["detail"], "\n".join(a.get("urls", [])))
                      for a in alerts])
    conn.commit()


def get_meta(conn, key, default=None):
    row = conn.execute("SELECT v FROM meta WHERE k=?", (key,)).fetchone()
    return row["v"] if row is not None else default


def set_meta(conn, key, value):
    conn.execute("INSERT OR REPLACE INTO meta(k, v) VALUES(?, ?)", (key, str(value)))
    conn.commit()


def backfill_drug_types(conn, type_fn, days=7):
    """Name the kind of NSA (Captagon, Fentanyl, mephedrone...) for recent NSA reports stored without one."""
    rows = conn.execute("SELECT id, title FROM articles WHERE relevant=1 AND primary_drug='NSA' AND drug_type IS NULL "
                        "AND COALESCE(published, fetched) >= date('now', ?)", (f"-{int(days)} day",)).fetchall()
    n = 0
    for r in rows:
        t = type_fn(norm(r[1]), "")
        if t:
            conn.execute("UPDATE articles SET drug_type=? WHERE id=?", (t, r[0]))
            n += 1
    conn.commit()
    return n
