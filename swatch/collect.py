# -*- coding: utf-8 -*-
"""
Collectors. All free, no API keys:
  * Google News RSS (many editions / languages)
  * GDELT DOC 2.0 API (global news index)
  * any RSS/Atom feeds you list in config.yaml
Only headlines + links come from the feeds; article text is fetched (politely) to read the facts,
and only the extracted facts + link are stored - never the article body.
"""
import re
import time
import html
import email.utils
import datetime as dt
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote, urlsplit, urlunsplit, parse_qsl, urlencode

import requests

from . import lexicon as L

UA = "Mozilla/5.0 (compatible; SeizureWatch/1.0; open-source news monitor)"
HDRS = {"User-Agent": UA, "Accept-Language": "en,es;q=0.8,fr;q=0.6,pt;q=0.6"}


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


def _get(url, timeout=20, **kw):
    try:
        r = requests.get(url, headers=HDRS, timeout=timeout, **kw)
        r.raise_for_status()
        return r
    except Exception as e:
        log(f"   ! {url[:90]}... {type(e).__name__}")
        return None


# ---------------------------------------------------------------- Google News
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
                    "source_country": None, "via": "google"})
    return out


def resolve_google_link(url):
    """Google News links are redirects; googlenewsdecoder (optional) turns them into the publisher URL."""
    if "news.google.com" not in url:
        return url
    try:
        from googlenewsdecoder import gnewsdecoder
        res = gnewsdecoder(url, interval=0.5)
        if res.get("status") and res.get("decoded_url"):
            return res["decoded_url"]
    except Exception:
        pass
    return url


# ---------------------------------------------------------------------- GDELT
GDELT_LANGS = {"en": "english", "es": "spanish", "fr": "french", "pt": "portuguese"}


def gdelt(query, lang, days, maxrec=100):
    q = f"({query}) sourcelang:{GDELT_LANGS.get(lang, 'english')}"
    url = ("https://api.gdeltproject.org/api/v2/doc/doc?query=" + quote(q) +
           f"&mode=artlist&maxrecords={maxrec}&format=json&sort=datedesc&timespan={days}d")
    r = _get(url, timeout=40)
    time.sleep(6)  # GDELT asks for <= 1 request / 5 s
    if r is None:
        return []
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
def rss_feed(feed):
    r = _get(feed["url"])
    if r is None:
        return []
    try:
        root = ET.fromstring(r.content)
    except ET.ParseError:
        return []
    out = []
    for it in list(root.iter("item")) + list(root.iter("{http://www.w3.org/2005/Atom}entry")):
        link = it.findtext("link") or ""
        if not link:
            le = it.find("{http://www.w3.org/2005/Atom}link")
            link = le.get("href") if le is not None else ""
        pub = it.findtext("pubDate") or it.findtext("{http://www.w3.org/2005/Atom}updated") or ""
        try:
            published = email.utils.parsedate_to_datetime(pub).date().isoformat()
        except Exception:
            published = pub[:10] or None
        out.append({"url": link, "title": html.unescape(it.findtext("title") or ""), "source": feed.get("name", ""),
                    "published": published,
                    "snippet": _strip_html(it.findtext("description") or it.findtext(
                        "{http://www.w3.org/2005/Atom}summary")),
                    "lang": feed.get("lang", "en"), "source_country": feed.get("country"), "via": "rss"})
    return out


# ------------------------------------------------------------------ orchestration
def collect(cfg, days):
    items = []
    s = cfg["sources"]
    if s.get("google_news", {}).get("enabled", True):
        g = s["google_news"]
        for ed in g["editions"]:
            for q in g["queries"].get(ed["lang"], []):
                got = google_news(q, ed, days)
                items += got
                time.sleep(g.get("delay_seconds", 1.0))
        log(f"   Google News: {len(items)} headlines")
    if s.get("gdelt", {}).get("enabled", True):
        n0 = len(items)
        for lang, queries in s["gdelt"]["queries"].items():
            for q in queries:
                items += gdelt(q, lang, days)
        log(f"   GDELT: {len(items) - n0} headlines")
    for feed in s.get("rss_feeds", []) or []:
        got = rss_feed(feed)
        items += got
        log(f"   RSS {feed.get('name')}: {len(got)} items")
    return items


def prefilter(items, cutoff_date):
    """Cheap headline check so we only download articles that look like drug-seizure stories."""
    seen, out = set(), []
    for it in items:
        if not it.get("url") or not it.get("title"):
            continue
        if it["published"] and it["published"] < cutoff_date:
            continue
        blob = L.norm(it["title"] + " " + (it.get("snippet") or ""))
        if not L.ANY_DRUG.search(blob):
            continue
        if L.EXCLUDE.search(blob):
            continue
        it["url"] = clean_url(it["url"])
        key = re.sub(r"[^a-z0-9]+", " ", L.norm(it["title"]))[:90]
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


def fetch_text(item, resolve=True, max_chars=9000):
    """Fetch and extract article text. Returns (text, mode). Falls back to headline + snippet."""
    url = item["url"]
    try:
        if resolve:
            url = resolve_google_link(url)
            item["url"] = clean_url(url)
        if "news.google.com" in url:
            return item.get("snippet", ""), "snippet"
        r = _get(url, timeout=15)
        if r is not None and "text" in r.headers.get("Content-Type", "text"):
            try:
                import trafilatura
                txt = trafilatura.extract(r.text, include_comments=False, include_tables=False) or ""
            except ImportError:
                txt = _strip_html(r.text)
            if len(txt) > 200:
                return txt[:max_chars], "full"
    except Exception as e:
        log(f"   ! fetch failed {type(e).__name__}")
    return item.get("snippet", ""), "snippet"


def fetch_all(items, resolve=True, workers=6):
    def one(it):
        txt, mode = fetch_text(it, resolve)
        it["text"], it["text_mode"] = txt, mode
        return it
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(one, items))
