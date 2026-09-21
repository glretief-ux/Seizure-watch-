"""Offline tests of the collectors using canned Google News / GDELT / RSS payloads (no internet needed)."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from swatch import collect

GNEWS = b"""<?xml version="1.0"?><rss version="2.0"><channel>
<item><title>Customs seize 2 tonnes of cocaine at Rotterdam - Example News</title>
<link>https://news.google.com/rss/articles/CBMiX123</link><pubDate>Sat, 19 Sep 2026 08:00:00 GMT</pubDate>
<description>&lt;a href="x"&gt;Customs seize 2 tonnes of cocaine at Rotterdam&lt;/a&gt;&amp;nbsp;&lt;font&gt;Example News&lt;/font&gt;</description>
<source url="https://example.com">Example News</source></item>
<item><title>Cannabis stocks rally on legalization news - Biz</title><link>https://news.google.com/rss/articles/CBMiY</link>
<pubDate>Sat, 19 Sep 2026 09:00:00 GMT</pubDate><description>stocks</description><source url="https://b.com">Biz</source></item>
</channel></rss>"""
GDELT = json.dumps({"articles": [{"url": "https://example.org/a?utm_source=x", "title": "Saisie de 500 kg de cocaine",
                                   "seendate": "20260919T101500Z", "domain": "example.org", "sourcecountry": "France"}]}).encode()

class FakeResp:
    def __init__(self, content): self.content = content; self.text = content.decode(); self.headers = {"Content-Type": "text/html"}
    def json(self): return json.loads(self.content)

def test_google_parse(monkeypatch=None):
    orig = collect._get
    collect._get = lambda url, **kw: FakeResp(GNEWS)
    try:
        items = collect.google_news("cocaine seized", {"hl": "en-US", "gl": "US", "ceid": "US:en", "lang": "en"}, 2)
    finally:
        collect._get = orig
    assert len(items) == 2
    assert items[0]["title"] == "Customs seize 2 tonnes of cocaine at Rotterdam"
    assert items[0]["source"] == "Example News" and items[0]["published"] == "2026-09-19"
    kept = collect.prefilter(items, "2026-09-18")
    assert len(kept) == 1          # the 'cannabis stocks' story is filtered out

def test_gdelt_parse():
    orig, sl = collect._get, collect.time.sleep
    collect._get = lambda url, **kw: FakeResp(GDELT); collect.time.sleep = lambda s: None
    try:
        items = collect.gdelt("cocaine", "fr", 2)
    finally:
        collect._get, collect.time.sleep = orig, sl
    assert items[0]["published"] == "2026-09-19" and items[0]["source_country"] == "France"
    assert collect.clean_url(items[0]["url"]) == "https://example.org/a"

def test_fetch_fallback():
    orig = collect._get
    collect._get = lambda url, **kw: None       # simulate blocked site
    try:
        txt, mode = collect.fetch_text({"url": "https://example.org/x", "snippet": "headline snippet"}, resolve=False)
    finally:
        collect._get = orig
    assert (txt, mode) == ("headline snippet", "snippet")

def _with_decoder(fake, fn):
    import googlenewsdecoder
    orig = googlenewsdecoder.gnewsdecoder
    googlenewsdecoder.gnewsdecoder = fake
    try:
        return fn()
    finally:
        googlenewsdecoder.gnewsdecoder = orig

def test_resolve_new_decoder_format():
    items = [{"url": "https://news.google.com/rss/articles/AAA"}, {"url": "https://news.google.com/rss/articles/BBB"},
             {"url": "https://example.org/direct"}]
    fake = lambda src, interval=None, **kw: [{"success": True, "decoded_url": "https://pub.example/a?utm_source=x"},
                                             {"success": False, "message": "blocked"}]
    done, failed = _with_decoder(fake, lambda: collect.resolve_google_links(items))
    assert (done, failed) == (1, 1)
    assert items[0]["url"] == "https://pub.example/a" and "news.google.com" in items[1]["url"]

def test_resolve_old_decoder_format():
    def fake(src, interval=None, **kw):
        if isinstance(src, list):
            raise TypeError("old version takes one link")
        return {"status": True, "decoded_url": "https://pub.example/old"}
    items = [{"url": "https://news.google.com/rss/articles/AAA"}]
    done, failed = _with_decoder(fake, lambda: collect.resolve_google_links(items))
    assert (done, failed) == (1, 0) and items[0]["url"] == "https://pub.example/old"

def test_fetch_all_reads_full_text():
    class R:
        headers = {"Content-Type": "text/html"}
        text = "<html><body><article><p>" + ("Customs officers seized 120 kg of cocaine at the port. " * 20) + "</p></article></body></html>"
    orig = collect._get
    collect._get = lambda url, **kw: R()
    try:
        fake = lambda src, interval=None, **kw: [{"success": True, "decoded_url": "https://pub.example/a"}]
        items = [{"url": "https://news.google.com/rss/articles/AAA", "snippet": "s"}]
        out = _with_decoder(fake, lambda: collect.fetch_all(items, resolve=True))
    finally:
        collect._get = orig
    assert out[0]["text_mode"] == "full" and out[0]["url"] == "https://pub.example/a" and "120 kg" in out[0]["text"]

ATOM_XML = b"""<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"><title>x</title>
<entry><title>Border Force seizes 50kg of cocaine at Felixstowe</title><link rel="alternate" href="https://www.gov.uk/government/news/a"/>
<updated>2026-09-20T10:00:00+00:00</updated><summary>&lt;p&gt;Officers found cocaine.&lt;/p&gt;</summary></entry></feed>"""
RSS_XML = b"""<?xml version="1.0"?><rss version="2.0"><channel><item><title>Customs seizes suspected ketamine at airport</title>
<link>https://www.info.gov.hk/gia/general/202609/20/P1.htm</link><pubDate>Sun, 20 Sep 2026 10:00:00 +0800</pubDate><description>Ketamine seized.</description></item></channel></rss>"""

def test_rss_feed_reads_atom_and_rss():
    class R:  # noqa
        def __init__(self, c): self.content = c
    orig = collect._get
    try:
        collect._get = lambda url, **kw: R(ATOM_XML)
        a = collect.rss_feed({"name": "NCA", "url": "u", "country": "United Kingdom"})
        collect._get = lambda url, **kw: R(RSS_XML)
        b = collect.rss_feed({"name": "HK", "url": "u", "country": "Hong Kong"})
    finally:
        collect._get = orig
    assert a[0]["title"].startswith("Border Force seizes 50kg") and a[0]["url"].endswith("/a") and a[0]["published"] == "2026-09-20"
    assert a[0]["snippet"] == "Officers found cocaine." and a[0]["official"] is True
    assert b[0]["published"] == "2026-09-20" and b[0]["source_country"] == "Hong Kong"

def test_official_sources_come_first():
    calls = []
    def fake_gn(q, ed, days):
        calls.append(q)
        return [{"url": "https://x/" + str(len(calls)), "title": ("OFFICIAL " if q.startswith("site:") else "NEWS ") + q[:20], "source": "s", "published": "2026-09-20"}]
    o_gn, o_gd, o_rss, o_sleep = collect.google_news, collect.gdelt, collect.rss_feed, collect.time.sleep
    collect.google_news, collect.gdelt = fake_gn, lambda *a, **k: []
    collect.rss_feed = lambda f: [{"url": "https://feed/1", "title": "FEED item", "source": "f", "published": "2026-09-20", "official": True}]
    collect.time.sleep = lambda s: None
    try:
        cfg = {"sources": {"google_news": {"enabled": True, "delay_seconds": 0, "editions": [{"lang": "en", "hl": "en-US", "gl": "US", "ceid": "US:en"}],
                                            "queries": {"en": ["cocaine seized"]}},
                           "gdelt": {"enabled": False, "queries": {}},
                           "official_sites": {"enabled": True, "query": "site:{site} seized", "sites": ["cbp.gov", "dea.gov"]},
                           "rss_feeds": [{"name": "f", "url": "u"}]}}
        out = collect.collect(cfg, 2)
    finally:
        collect.google_news, collect.gdelt, collect.rss_feed, collect.time.sleep = o_gn, o_gd, o_rss, o_sleep
    titles = [i["title"] for i in out]
    assert titles[0].startswith("FEED") and titles[1].startswith("OFFICIAL") and titles[2].startswith("OFFICIAL") and titles[3].startswith("NEWS")
    assert calls[:2] == ["site:cbp.gov seized", "site:dea.gov seized"]

if __name__ == "__main__":
    for k, v in list(globals().items()):
        if k.startswith("test_"):
            v(); print("ok  ", k)
