#!/usr/bin/env python3
"""Build the Seizure Watch weekly newsletter (one self-contained HTML file).

Usage:  python3 scripts/build_newsletter.py [END_DATE YYYY-MM-DD] [OUT.html]

- Reads docs/events.csv, takes the 7 days ending END_DATE (default: latest date in the data).
- Featured stories carry a photo. Where the machine has internet (e.g. GitHub Actions) the photo
  is downloaded and embedded; otherwise the article's photo link is used and the card falls
  back to a plain panel if the image cannot load.
- Charts are plain HTML/CSS, so the file works in a browser and in most mail clients.
"""
import base64, csv, collections, datetime as dt, html, os, re, sys, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(ROOT, "docs", "events.csv")
LOGO = os.path.join(ROOT, "assets", "pccp", "pccp-logo-banner.jpg")
SITE = "https://glretief-ux.github.io/Seizure-watch-/"

# Featured stories: article link -> (photo url, headline, text). Edit each week, or let the
# script pick the top-scoring reports (see auto_pick) when this list is empty.
FEATURED = [
    ("https://jamaica-gleaner.com/article/news/20261020/more-1-billion-worth-cocaine-seized-48-hours",
     "http://jamaica-gleaner.com/sites/default/files/styles/1_1_large/public/media/article_images/2026/10/19/3499548/8541649.jpg?h=10d202d3&itok=AZmtv8ar",
     "Jamaica: about 1.5 tonnes of cocaine seized in 48 hours",
     "Jamaican outlets report a two-day run of cocaine seizures around Kingston. Coverage links the shipment to a Honduras to Belgium route and to concealment in legitimate cargo.",
     "Jamaica Gleaner"),
    ("https://www.vanguardngr.com/2026/10/ndlea-issues-public-alert-after-intercepting-woman-with-drugs-concealed-in-palm-oil-keg/",
     "https://cdn.vanguardngr.com/wp-content/uploads/2026/10/NDLEA.jpeg",
     "Nigeria: Saudi-bound drugs hidden in a palm oil keg",
     "NDLEA officers at Kano airport stopped a passenger carrying drugs concealed in a palm oil keg. The wider operation recovered tramadol worth about N6.9 billion (reported as 8.7 tonnes) at Lagos.",
     "Vanguard"),
    ("https://thethaiger.com/hot-news/crime/thailand-intercepts-heroin-drink-sachets-australia",
     "https://thethaiger.com/wp-content/uploads/2026/10/%E0%B8%AA%E0%B8%B3%E0%B9%80%E0%B8%99%E0%B8%B2%E0%B8%82%E0%B8%AD%E0%B8%87-23-34-23-1.jpg",
     "Thailand: 7 kg of heroin in drink sachets, bound for Australia",
     "Thai authorities intercepted a parcel shipment in which heroin was packed into drink sachets. The consignment was addressed to Australia.",
     "The Thaiger"),
    ("https://thesouthfirst.com/tamilnadu/nagapattinam-crystal-meth-seizure-provides-dmk-fresh-ammo-to-target-tvk/",
     "https://static.thesouthfirst.com/wp-content/uploads/2026/10/Meth.jpg",
     "India: 142 kg of crystal meth seized in Nagapattinam",
     "A large crystal meth seizure on the Tamil Nadu coast. Reports point to a Nepal to Sri Lanka route and an arrest in Sri Lanka of a suspect tied to the case.",
     "The South First"),
]
# Further notable reports, text only (link -> short line)
ALSO = [
    ("https://en.fnnews.com/news/202610201614562079", "South Korea: Customs activates a three-tier response after a 600 kg cocaine seizure"),
    ("https://www.hindustantimes.com/cities/delhi-news/foreigner-among-3-held-as-ncb-raids-drug-making-labs-in-gr-noida", "India: NCB raids drug-making labs in Greater Noida, three held"),
    ("https://diariodelnorte.net/nacion/incautan-mas-de-14-toneladas-de-cocaina-en-el-pacifico-colombiano-con-destin", "Colombia: more than 1.4 t of cocaine seized in the Pacific, bound for Costa Rica"),
    ("https://hoodline.com/2026/10/houston-airport-luggage-hides-100-pounds-of-meth-dea-and-police-say/", "United States: 100 lb of meth found in luggage at Houston airport"),
    ("https://news.mongabay.com/short-article/thailand-seizes-ivory-shipment-from-zambia-to-launch-dna-investigation", "Thailand: 500 kg ivory shipment from Zambia seized at Laem Chabang, DNA tests to follow"),
    ("https://www.ladepeche.fr/2026/10/17/reportage-combien-de-convois-passent-apres-930-kg-de-cocaine-saisis-dans-l", "France / Belgium: 930 kg of cocaine seized, with the Antwerp route in focus"),
    ("https://www.bastillepost.com/global/article/6264781-hong-kong-customs-seizes-suspected-drugs-worth-about-6-8-m", "Hong Kong: customs seize 22.4 kg of suspected drugs at the airport, two arrested"),
]


def fnum(x):
    try:
        return float(x)
    except Exception:
        return 0.0


def img_src(url):
    """Embed the photo when the network allows, else keep the remote link."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data, ctype = r.read(), r.headers.get_content_type()
        if ctype.startswith("image/") and len(data) < 1_500_000:
            return f"data:{ctype};base64,{base64.b64encode(data).decode()}"
    except Exception:
        pass
    return url


def og_image(url):
    """Lead photo of an article (its og:image / twitter:image), or None. Needs internet access."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            page = r.read(400_000).decode("utf-8", "ignore")
        for pat in (r'<meta[^>]+(?:property|name)=["\'](?:og:image|twitter:image)["\'][^>]*content=["\']([^"\']+)',
                    r'<meta[^>]+content=["\']([^"\']+)["\'][^>]*(?:property|name)=["\'](?:og:image|twitter:image)["\']'):
            m = re.search(pat, page, re.I)
            if m:
                return urllib.parse.urljoin(url, html.unescape(m.group(1)))
    except Exception:
        pass
    return None


def auto_pick(wk, n_feat=4, n_also=7, max_fetch=40):
    """Pick the week's stories automatically: highest risk first, real seizures only, one per outlet."""
    cands = sorted((r for r in wk if r["Link"] and r["Headline (English)"] and fnum(r["Total quantity (kg)"]) > 0),
                   key=lambda r: (-fnum(r["Risk score"]), -fnum(r["Total quantity (kg)"])))
    feat, also, outlets, fetched = [], [], set(), 0
    for r in cands:
        outlet = (r["Outlets"].split(",")[0] or "source").strip()
        if outlet in outlets:
            continue
        head = r["Headline (English)"].strip()
        if len(feat) < n_feat and fetched < max_fetch:
            fetched += 1
            photo = og_image(r["Link"])
            if photo:
                bits = [f'{r["Drug type"]}, {fnum(r["Total quantity (kg)"]):,.0f} kg']
                where = ", ".join(x for x in (r["Seizure place"], r["Seizure country"]) if x)
                if where:
                    bits.append("seized in " + where)
                if r["Origin"] and r["Destination"]:
                    bits.append(f'route {r["Origin"]} to {r["Destination"]}')
                if r["Concealment"]:
                    bits.append("hidden in " + r["Concealment"].split(";")[0].lower())
                feat.append((r["Link"], photo, head, "; ".join(bits) + ".", outlet))
                outlets.add(outlet)
                continue
        if len(also) < n_also:
            also.append((r["Link"], head))
            outlets.add(outlet)
        if len(feat) >= n_feat and len(also) >= n_also:
            break
    return feat, also


def bars(items, total=None, color="var(--a)"):
    top = max([v for _, v in items] or [1])
    out = []
    for label, v in items:
        w = max(2, round(100 * v / top))
        out.append(f'<div class="bar"><span class="bl">{html.escape(str(label))}</span>'
                   f'<span class="bt"><i style="width:{w}%;background:{color}"></i></span>'
                   f'<span class="bv">{v:,}</span></div>')
    return "\n".join(out)


def main():
    rows = list(csv.DictReader(open(CSV, encoding="utf-8-sig")))
    latest = max(r["Date"] for r in rows if r["Date"])
    end = dt.date.fromisoformat(sys.argv[1] if len(sys.argv) > 1 else latest)
    start = end - dt.timedelta(days=6)
    pend, pstart = start - dt.timedelta(days=1), start - dt.timedelta(days=7)
    inr = lambda r, a, b: a.isoformat() <= r["Date"] <= b.isoformat()
    wk = [r for r in rows if inr(r, start, end)]
    pv = [r for r in rows if inr(r, pstart, pend)]
    hi = [r for r in wk if r["Risk band"] == "High"]
    phi = [r for r in pv if r["Risk band"] == "High"]
    tons = sum(fnum(r["Total quantity (kg)"]) for r in wk) / 1000
    ptons = sum(fnum(r["Total quantity (kg)"]) for r in pv) / 1000
    cont = sum(1 for r in wk if r["Container"] == "Yes")
    ctry = len({r["Seizure country"] for r in wk if r["Seizure country"]})
    delta = lambda a, b: (f"{'▲' if a >= b else '▼'} {abs(100*(a-b)/b):.0f}% vs prior week" if b else "")

    days = [(start + dt.timedelta(days=i)) for i in range(7)]
    dc = collections.Counter(r["Date"] for r in wk)
    daily = []
    for d in days:
        n = dc[d.isoformat()]
        tag = " (partial)" if d == end and n < 50 else ""
        daily.append((d.strftime("%a %d") + tag, n))
    drugs = collections.Counter(r["Drug type"] for r in wk if r["Drug type"]).most_common(8)
    cats = collections.Counter(r["Category"] for r in wk if r["Category"]).most_common(6)
    where = collections.Counter(r["Seizure country"] for r in wk if r["Seizure country"]).most_common(8)
    routes = collections.Counter(f'{r["Origin"]} → {r["Destination"]}' for r in wk if r["Origin"] and r["Destination"]).most_common(6)
    conc = collections.Counter(r["Concealment"] for r in wk if r["Concealment"]).most_common(5)

    feat, also_l = FEATURED, ALSO
    if not all(any(r["Link"] == f[0] for r in wk) for f in FEATURED):   # hand-picked list is for another week
        feat, also_l = auto_pick(wk)

    logo = ""
    if os.path.exists(LOGO):
        logo = "data:image/jpeg;base64," + base64.b64encode(open(LOGO, "rb").read()).decode()

    cards = []
    for link, photo, head, text, outlet in feat:
        src = img_src(photo)
        cards.append(f'''<article class="card"><a href="{html.escape(link)}"><div class="ph"><span>Photo: open the article</span><img src="{html.escape(src)}" alt="" loading="lazy" referrerpolicy="no-referrer" onerror="this.remove()"></div></a>
<div class="cb"><h3><a href="{html.escape(link)}">{html.escape(head)}</a></h3><p>{html.escape(text)}</p>
<p class="cr">Photo and report: <a href="{html.escape(link)}">{html.escape(outlet)}</a></p></div></article>''')
    also = "\n".join(f'<li><a href="{html.escape(l)}">{html.escape(t)}</a></li>' for l, t in also_l)

    fmt = lambda d: d.strftime("%-d %b")
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Seizure Watch Weekly {fmt(start)} - {fmt(end)} {end.year}</title>
<style>
:root{{--a:#12507a;--ink:#1b2630;--mut:#5b6a76;--line:#d9e0e6;--bg:#f2f5f8;--hi:#b3261e}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:14px/1.55 Verdana,Geneva,sans-serif}}
.wrap{{max-width:760px;margin:0 auto;background:#fff}}
.banner{{display:block;width:100%;height:auto}}
.head{{padding:28px 32px 8px}}
.eyebrow{{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--a);font-weight:bold}}
h1{{font-size:28px;line-height:1.2;margin:6px 0 4px}}
.dates{{color:var(--mut);margin:0}}
.lead{{padding:8px 32px 0;font-size:15px}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--line);border:1px solid var(--line);margin:22px 32px 0}}
.k{{background:#fff;padding:14px 12px}}.k b{{display:block;font-size:24px;line-height:1.1}}.k span{{font-size:11px;color:var(--mut)}}.k em{{display:block;font-style:normal;font-size:11px;color:var(--mut);margin-top:3px}}
h2{{font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:var(--a);margin:0 0 14px;padding-bottom:8px;border-bottom:2px solid var(--a)}}
section{{padding:30px 32px 0}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}
.card{{border:1px solid var(--line);min-width:0}}
.ph{{position:relative;height:190px;background:linear-gradient(135deg,#e3eaf0,#cdd8e1);overflow:hidden}}
.ph span{{position:absolute;left:0;right:0;top:44%;text-align:center;font-size:11px;color:#5b6a76}}
.ph img{{position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover;display:block}}
@page{{size:A4;margin:10mm 0}}@media print{{body{{background:#fff}}.card,.bar,.k,ul.also li{{break-inside:avoid}}section{{break-inside:auto}}h2{{break-after:avoid}}}}
.cb{{padding:14px 16px 16px}}.cb h3{{font-size:15px;line-height:1.3;margin:0 0 8px}}.cb h3 a{{color:var(--ink);text-decoration:none}}
.cb p{{margin:0 0 8px;font-size:13px}}.cr{{color:var(--mut);font-size:11px!important;margin:0!important}}
a{{color:var(--a)}}
ul.also{{margin:0;padding:0;list-style:none}}ul.also li{{padding:9px 0;border-bottom:1px solid var(--line)}}ul.also a{{text-decoration:none;color:var(--ink)}}ul.also a:hover{{text-decoration:underline}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:28px}}
.cols h4{{margin:0 0 10px;font-size:13px}}
.bar{{display:grid;grid-template-columns:minmax(80px,38%) 1fr 44px;gap:8px;align-items:center;margin:5px 0;font-size:12px}}
.bl{{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}.bt{{background:#e8edf1;height:10px}}.bt i{{display:block;height:10px}}.bv{{text-align:right;color:var(--mut)}}
.risk{{display:flex;height:14px;margin:6px 0 8px}}.risk i{{display:block}}
.legend{{font-size:12px;color:var(--mut)}}
.note{{padding:24px 32px 30px;font-size:11px;color:var(--mut)}}
.foot{{background:#12304a;color:#d4e0ea;padding:18px 32px;font-size:11px}}.foot a{{color:#fff}}
@media(max-width:620px){{.kpis{{grid-template-columns:1fr 1fr}}.ph{{height:170px}}.grid,.cols{{grid-template-columns:1fr}}.head,section,.lead,.note,.foot{{padding-left:18px;padding-right:18px}}.kpis{{margin-left:18px;margin-right:18px}}h1{{font-size:23px}}}}
</style></head><body><div class="wrap">
{f'<img class="banner" src="{logo}" alt="AIRCOP and Container Control Programme">' if logo else ''}
<div class="head"><div class="eyebrow">Seizure Watch · Weekly Newsletter</div>
<h1>The week in seizures</h1><p class="dates">{fmt(start)} to {fmt(end)} {end.year}</p></div>
<p class="lead">{len(wk):,} seizure reports from {ctry} countries, {abs(100*(len(wk)-len(pv))/len(pv)):.0f}% {'more' if len(wk)>=len(pv) else 'fewer'} than the week before. {len(hi)} were rated High risk. Cannabis ({drugs[0][1]}) and cocaine ({drugs[1][1] if len(drugs)>1 else 0}) led the reports.</p>
<div class="kpis">
<div class="k"><b>{len(wk):,}</b><span>Seizure reports</span><em>{delta(len(wk),len(pv))}</em></div>
<div class="k"><b>{len(hi)}</b><span>High risk</span><em>{delta(len(hi),len(phi))}</em></div>
<div class="k"><b>{tons:,.0f} t</b><span>Reported weight</span><em>{delta(tons,ptons)}</em></div>
<div class="k"><b>{cont}</b><span>Container cases</span><em></em></div>
</div>

<section><h2>Top stories</h2><div class="grid">
{chr(10).join(cards)}
</div></section>

<section><h2>Also making news</h2><ul class="also">
{also}
</ul></section>

<section><h2>The week in numbers</h2>
<div class="cols"><div><h4>Reports per day</h4>{bars(daily)}</div>
<div><h4>Most reported drugs and goods</h4>{bars(drugs)}</div></div>
<div class="cols" style="margin-top:24px"><div><h4>What was seized</h4>{bars(cats)}</div>
<div><h4>Where seizures were made</h4>{bars(where)}</div></div>
<div class="cols" style="margin-top:24px"><div><h4>Busiest routes (origin → destination)</h4>{bars(routes, color="#1d7a5f")}</div>
<div><h4>How it was hidden</h4>{bars(conc, color="#7a4a12")}</div></div>
</section>

<p class="note">These are leads from open news sources, not confirmed facts. Verify before acting. Report counts reflect what the tool found in the news it searches; a quiet country may mean no news or no coverage. Photos belong to the cited outlets and link back to their articles. Data runs to {latest}{' (the last day is partial)' if latest == end.isoformat() and dc[latest] < 50 else ''}.</p>
<div class="foot">Seizure Watch · AIRCOP / Container Control Programme · <a href="{SITE}">Full dashboard</a> · <a href="{SITE}bulletin.html">Weekly bulletin</a></div>
</div></body></html>'''
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "docs", "newsletter.html")
    open(out, "w", encoding="utf-8").write(page)
    print("wrote", out, len(page) // 1024, "KB;", len(wk), "reports", start, "to", end)
    try:   # PDF with clickable links (needs: pip install weasyprint)
        from weasyprint import HTML
        pdf = os.path.splitext(out)[0] + ".pdf"
        HTML(string=page, base_url=SITE).write_pdf(pdf)
        print("wrote", pdf)
    except ImportError:
        print("weasyprint not installed; PDF skipped")


if __name__ == "__main__":
    main()
