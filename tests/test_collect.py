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

if __name__ == "__main__":
    for k, v in list(globals().items()):
        if k.startswith("test_"):
            v(); print("ok  ", k)
