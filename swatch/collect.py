# -*- coding: utf-8 -*-
"""
Collectors. All free, no API keys:
  * Google News RSS (many editions / languages)
  * GDELT DOC 2.0 API (global news index)
  * any RSS/Atom feeds you list in config.yaml
Only headlines + links come from the feeds; article text is fetched (politely) to read the facts,
and only the extracted facts + link are stored - never the article body.
"""
import os
import re
import time
import html
import threading
import email.utils
import datetime as dt
import xml.etree.ElementTree as ET
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, wait
from urllib.parse import quote, urlsplit, urlunsplit, parse_qsl, urlencode

import requests

from . import lexicon as L

UA = "Mozilla/5.0 (compatible; SeizureWatch/1.0; open-source news monitor)"
HDRS = {"User-Agent": UA, "Accept-Language": "en,es;q=0.8,fr;q=0.6,pt;q=0.6,nl;q=0.6,de;q=0.5,sv;q=0.4,da;q=0.4,no;q=0.4"}


def log(*a):
    print(*a, flush=True)


def clean_url(u):
    try:
        p = urlsplit(u)
        q = [(k, v) for k, v in parse_qsl(p.query) if not k.lower().startswith(("utm_", "fbclid", "gclid", "ocid"))]
        return urlunsplit((p.scheme, p.netloc, p.path, urlencode(q), ""))
    except Exception:
        return u


def _strip_html(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


_FAIL_STATS = Counter()   # why article downloads failed this run (summarised once, instead of one log line per URL)


def _get(url, timeout=20, quiet=False, max_seconds=None, max_bytes=None, **kw):
    """GET with a connect/read timeout. max_seconds / max_bytes put a hard cap on one download, because a
    read timeout alone only limits the gap between two chunks: a server that trickles bytes can hold a
    worker for many minutes. quiet=True counts failures in _FAIL_STATS instead of logging every one."""
    try:
        if max_seconds is None and max_bytes is None:
            r = requests.get(url, headers=HDRS, timeout=timeout, **kw)
            r.raise_for_status()
            return r
        r = requests.get(url, headers=HDRS, timeout=timeout, stream=True, **kw)
        r.raise_for_status()
        t0, buf = time.monotonic(), bytearray()
        for chunk in r.iter_content(65536):
            buf += chunk
            if (max_bytes and len(buf) > max_bytes) or (max_seconds and time.monotonic() - t0 > max_seconds):
                break
        r._content, r._content_consumed = bytes(buf), True   # so r.content / r.text work as usual
        r.close()
        return r
    except Exception as e:
        if quiet:
            _FAIL_STATS[type(e).__name__] += 1
        else:
            log(f"   ! {url[:90]}... {type(e).__name__}")
        return None


# ---------------------------------------------------------------- Google News
# The Google News edition a headline came from is a weak hint of where it happened. It is used only when the
# text names no place, country, agency or currency at all (see extract._route), and is stored as low confidence.
_ED_COUNTRY = {"US": "United States", "GB": "United Kingdom", "AU": "Australia", "IN": "India", "ZA": "South Africa",
               "NG": "Nigeria", "MX": "Mexico", "ES": "Spain", "CO": "Colombia", "FR": "France", "BR": "Brazil", "PT": "Portugal",
               "NL": "Netherlands", "BE": "Belgium", "AT": "Austria", "DK": "Denmark", "EE": "Estonia", "ET": "Ethiopia",
               "IS": "Iceland", "MN": "Mongolia", "NO": "Norway", "SK": "Slovakia", "SE": "Sweden"}


def google_news(query, ed, days):
    q = quote(f"{query} when:{days}d")
    url = (f"https://news.google.com/rss/search?q={q}&hl={ed['hl']}&gl={ed['gl']}&ceid={quote(ed['ceid'], safe=':')}")
    r = _get(url)
    if r is None:
        return []
    out = []
    try:
        root = ET.fromstring(r.content)
    except ET.ParseError:
        return []
    for it in root.iter("item"):
        title = html.unescape(it.findtext("title") or "")
        src_el = it.find("source")
        source = (src_el.text if src_el is not None else "") or ""
        if source and title.endswith(" - " + source):
            title = title[: -len(source) - 3]
        pub = it.findtext("pubDate")
        try:
            published = email.utils.parsedate_to_datetime(pub).astimezone(dt.timezone.utc).date().isoformat()
        except Exception:
            published = None
        out.append({"url": it.findtext("link"), "title": title, "source": source, "published": published,
                    "snippet": _strip_html(it.findtext("description")), "lang": ed.get("lang"),
                    "source_country": _ED_COUNTRY.get(ed.get("gl")), "via": "google"})
    return out


def _decoded(res):
    """The publisher address from a googlenewsdecoder result. Old versions answer {"status": True, ...},
    version 0.2 and later answer {"success": True, ...}; accept both."""
    if isinstance(res, dict) and (res.get("success") or res.get("status")) and res.get("decoded_url"):
        return res["decoded_url"]
    return None


def resolve_google_link(url):
    """Google News links are redirects; googlenewsdecoder (optional) turns them into the publisher URL."""
    if "news.google.com" not in url:
        return url
    try:
        from googlenewsdecoder import gnewsdecoder
        return _decoded(gnewsdecoder(url, interval=0.5)) or url
    except Exception:
        return url


def resolve_google_links(items, interval=0.3, chunk=25, deadline=None):
    """Turn the Google News redirect links of many items into real article addresses (in place).
    One polite pass, one small batch at a time. Returns (resolved, failed) and logs why links failed."""
    todo = [it for it in items if "news.google.com" in it.get("url", "")]
    if not todo:
        return 0, 0
    try:
        from googlenewsdecoder import gnewsdecoder
    except Exception as e:
        log(f"   ! googlenewsdecoder is not available ({type(e).__name__}: {e}); reading headlines and snippets only")
        return 0, len(todo)
    done, why = 0, {}
    for i in range(0, len(todo), chunk):
        if deadline and time.monotonic() > deadline:
            log(f"      link resolving stopped at its time limit after {done} of {len(todo)}; the rest are read from headline + snippet")
            break
        batch = todo[i:i + chunk]
        urls = [b["url"] for b in batch]
        try:
            res = gnewsdecoder(urls, interval=interval)      # newer versions take a whole list in one go
            if not isinstance(res, list) or len(res) != len(urls):
                raise TypeError("list answer expected")
        except Exception:
            res = []
            for u in urls:                                    # older versions: one link at a time
                try:
                    res.append(gnewsdecoder(u, interval=interval))
                except Exception as e:
                    res.append({"success": False, "message": f"{type(e).__name__}: {e}"})
        for it, r in zip(batch, res):
            real = _decoded(r)
            if real:
                it["url"] = clean_url(real)
                done += 1
            else:
                msg = str((r or {}).get("message", r))[:110] if isinstance(r, dict) else str(r)[:110]
                why[msg] = why.get(msg, 0) + 1
    failed = len(todo) - done
    log(f"      links resolved: {done} of {len(todo)}")
    for msg, n in sorted(why.items(), key=lambda kv: -kv[1])[:3]:
        log(f"   ! {n} links failed: {msg}")
    return done, failed


# ---------------------------------------------------------------------- GDELT
GDELT_LANGS = {"en": "english", "es": "spanish", "fr": "french", "pt": "portuguese", "ar": "arabic", "tr": "turkish",
               "ru": "russian", "zh": "chinese", "hi": "hindi", "vi": "vietnamese", "nl": "dutch", "de": "german", "da": "danish", "et": "estonian",
               "am": "amharic", "is": "icelandic", "mn": "mongolian", "no": "norwegian", "sk": "slovak", "sv": "swedish"}


_GDELT_FAILS = 0
GDELT_MAX_FAILS = 4   # after this many failures in a row, skip GDELT for the rest of the run (it is down or blocking us)


def gdelt(query, lang, days, maxrec=100):
    global _GDELT_FAILS
    if _GDELT_FAILS >= GDELT_MAX_FAILS:
        return []
    q = f"({query}) sourcelang:{GDELT_LANGS.get(lang, 'english')}"
    url = ("https://api.gdeltproject.org/api/v2/doc/doc?query=" + quote(q) +
           f"&mode=artlist&maxrecords={maxrec}&format=json&sort=datedesc&timespan={days}d")
    r = _get(url, timeout=(5, 15))
    time.sleep(6)  # GDELT asks for <= 1 request / 5 s
    if r is None:
        _GDELT_FAILS += 1
        if _GDELT_FAILS == GDELT_MAX_FAILS:
            print(f"   ! GDELT failed {GDELT_MAX_FAILS} times in a row; skipping GDELT for the rest of this run", flush=True)
        return []
    _GDELT_FAILS = 0
    try:
        arts = r.json().get("articles", [])
    except Exception:
        return []
    out = []
    for a in arts:
        sd = a.get("seendate", "")
        published = f"{sd[:4]}-{sd[4:6]}-{sd[6:8]}" if len(sd) >= 8 else None
        out.append({"url": a.get("url"), "title": a.get("title", ""), "source": a.get("domain", ""),
                    "published": published, "snippet": "", "lang": lang,
                    "source_country": L.COUNTRY_ALIAS.get(L.norm(a.get("sourcecountry", ""))),
                    "via": "gdelt"})
    return out


# ------------------------------------------------------------------ RSS feeds
ATOM = "{http://www.w3.org/2005/Atom}"
RDF = "{http://purl.org/rss/1.0/}"


def _first(it, *tags):
    for t in tags:
        v = it.findtext(t)
        if v and v.strip():
            return v.strip()
    return ""


def rss_feed(feed):
    """RSS 2.0, RSS 1.0 and Atom feeds."""
    r = _get(feed["url"])
    if r is None:
        return []
    try:
        root = ET.fromstring(r.content)
    except ET.ParseError:
        return []
    out = []
    for it in list(root.iter("item")) + list(root.iter(RDF + "item")) + list(root.iter(ATOM + "entry")):
        link = _first(it, "link", RDF + "link")
        if not link:
            for le in it.findall(ATOM + "link"):
                if le.get("rel", "alternate") == "alternate" and le.get("href"):
                    link = le.get("href")
                    break
        pub = _first(it, "pubDate", ATOM + "published", ATOM + "updated", "{http://purl.org/dc/elements/1.1/}date")
        try:
            published = email.utils.parsedate_to_datetime(pub).date().isoformat()
        except Exception:
            published = pub[:10] or None
        out.append({"url": link, "title": html.unescape(_first(it, "title", ATOM + "title", RDF + "title")),
                    "source": feed.get("name", ""), "published": published,
                    "snippet": _strip_html(_first(it, "description", ATOM + "summary", ATOM + "content", RDF + "description")),
                    "lang": feed.get("lang", "en"), "source_country": feed.get("country"), "via": "rss", "official": True})
    return out


# ------------------------------------------------------------------ orchestration
def collect(cfg, days):
    items, official = [], []
    s = cfg["sources"]
    # 1. official newsrooms: your RSS feeds, and Google News searches limited to official websites
    for feed in s.get("rss_feeds", []) or []:
        got = rss_feed(feed)
        official += got
        log(f"   RSS {feed.get('name')}: {len(got)} items")
    o = s.get("official_sites", {}) or {}
    if o.get("enabled", False) and o.get("sites"):
        # The search itself always runs through the English Google News edition (that's just
        # the query locale) - but each site publishes in its own language, which is what decides
        # whether the headline gets auto-translated later, so that's tagged per site below.
        ed = (s.get("google_news", {}).get("editions") or [{"lang": "en", "hl": "en-US", "gl": "US", "ceid": "US:en"}])[0]
        n0 = len(official)
        for entry in o["sites"]:
            site, site_lang = (entry["site"], entry.get("lang", "en")) if isinstance(entry, dict) else (entry, "en")
            got = google_news(o.get("query", "site:{site} (seized OR seizure)").format(site=site), ed, days)
            for g_ in got:
                g_["official"] = True
                g_["lang"] = site_lang
            official += got
            time.sleep(s.get("google_news", {}).get("delay_seconds", 1.0))
        log(f"   Official websites ({len(o['sites'])} searched): {len(official) - n0} headlines")
    # 2. general news
    if s.get("google_news", {}).get("enabled", True):
        g = s["google_news"]
        for ed in g["editions"]:
            n_ed = 0
            for q in g["queries"].get(ed["lang"], []):
                got = google_news(q, ed, days)
                items += got
                n_ed += len(got)
                time.sleep(g.get("delay_seconds", 1.0))
            # one line per non-English edition, so an edition Google does not serve (0 headlines) is easy to spot
            if ed["lang"] != "en":
                log(f"      edition {ed['gl']}/{ed['lang']}: {n_ed} headlines")
        log(f"   Google News: {len(items)} headlines")
    if s.get("gdelt", {}).get("enabled", True):
        n0 = len(items)
        for lang, queries in s["gdelt"]["queries"].items():
            n_l = len(items)
            for q in queries:
                items += gdelt(q, lang, days)
            if lang != "en":
                log(f"      GDELT {lang}: {len(items) - n_l} headlines")
        log(f"   GDELT: {len(items) - n0} headlines")
    return official + items


def prefilter(items, cutoff_date):
    """Cheap headline check so we only download articles that look like
    seizure stories - drugs, precursor chemicals, CITES-protected timber,
    or (vehicle noun + theft/recovery cue together, since a vehicle word
    alone is far too common a false-positive trigger on its own)."""
    seen, out = set(), []
    for it in items:
        if not it.get("url") or not it.get("title"):
            continue
        if it["published"] and it["published"] < cutoff_date:
            continue
        blob = L.norm(it["title"] + " " + (it.get("snippet") or ""))
        is_contraband = L.ANY_CONTRABAND.search(blob)
        is_vehicle = L.VEHICLE_THEFT_CUE.search(blob) and (
            L.ANY_STOLEN_VEHICLE.search(blob) or L.VEHICLE_WORDS.search(blob))
        if not (is_contraband or is_vehicle):
            continue
        if L.EXCLUDE.search(blob):
            continue
        it["url"] = clean_url(it["url"])
        key = L.slug(it["title"])[:90]
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


# Sites that keep refusing us (bot walls, paywalls, dead hosts) are skipped after a few failures in a row instead
# of being tried again for every one of their articles. Reset at the start of every fetch_all().
DOMAIN_MAX_FAILS = 3
_dom_fails, _dom_lock = {}, threading.Lock()


def _domain(url):
    try:
        return urlsplit(url).netloc.lower()
    except Exception:
        return ""


def _domain_blocked(url):
    with _dom_lock:
        return _dom_fails.get(_domain(url), 0) >= DOMAIN_MAX_FAILS


def _domain_result(url, ok):
    d = _domain(url)
    with _dom_lock:
        _dom_fails[d] = 0 if ok else _dom_fails.get(d, 0) + 1


def fetch_text(item, resolve=True, max_chars=9000):
    """Fetch and extract article text. Returns (text, mode). Falls back to headline + snippet."""
    url = item["url"]
    try:
        if resolve:
            url = resolve_google_link(url)
            item["url"] = clean_url(url)
        if "news.google.com" in url:
            return item.get("snippet", ""), "snippet"
        if _domain_blocked(url):
            _FAIL_STATS["skipped (site kept failing)"] += 1
            return item.get("snippet", ""), "snippet"
        r = _get(url, timeout=(5, 10), quiet=True, max_seconds=20, max_bytes=2_000_000)
        _domain_result(url, r is not None)
        if r is not None and "text" in r.headers.get("Content-Type", "text"):
            try:
                import trafilatura
                txt = trafilatura.extract(r.text, include_comments=False, include_tables=False) or ""
            except ImportError:
                txt = _strip_html(r.text)
            if len(txt) > 200:
                return txt[:max_chars], "full"
    except Exception as e:
        _FAIL_STATS[type(e).__name__] += 1
    return item.get("snippet", ""), "snippet"


def fetch_all(items, resolve=True, workers=None, budget_min=None):
    """Read the articles in parallel. Everything is bounded: each download has a hard cap (see fetch_text) and the
    whole step stops after budget_min minutes (env FETCH_BUDGET_MIN, default 14). Articles not reached keep their
    headline + snippet, so the run still goes on to analysis, the dashboard and 'Save results'."""
    workers = workers or int(os.environ.get("FETCH_WORKERS", "16"))
    budget_min = budget_min if budget_min is not None else float(os.environ.get("FETCH_BUDGET_MIN", "14"))
    t_end = time.monotonic() + budget_min * 60
    with _dom_lock:
        _dom_fails.clear()
    _FAIL_STATS.clear()
    if resolve:
        # link resolving may use at most half of the budget; the rest is for reading the articles
        resolve_google_links(items, deadline=time.monotonic() + budget_min * 30)

    def one(it):
        if time.monotonic() > t_end:
            return it
        txt, mode = fetch_text(it, resolve=False)
        it["text"], it["text_mode"] = txt, mode
        return it
    ex = ThreadPoolExecutor(max_workers=workers)
    futs = [ex.submit(one, it) for it in items]
    _, not_done = wait(futs, timeout=max(1, t_end - time.monotonic()))
    for f in not_done:
        f.cancel()
    ex.shutdown(wait=False, cancel_futures=True)   # downloads still running are capped at ~20 s by fetch_text
    for it in items:                                # anything not reached: headline + snippet only
        if "text" not in it:
            it["text"], it["text_mode"] = it.get("snippet", ""), "snippet"
    full = sum(1 for i in items if i.get("text_mode") == "full")
    log(f"      read in full: {full}; headline + snippet only: {len(items) - full}"
        + (f" (time limit of {budget_min:g} min reached)" if not_done else ""))
    if _FAIL_STATS:
        log("      download problems: " + ", ".join(f"{k} x{v}" for k, v in _FAIL_STATS.most_common(6)))
    return items
