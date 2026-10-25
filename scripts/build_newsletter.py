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
     "Jamaica Gleaner", "Cocaine", "Jamaica"),
    ("https://www.vanguardngr.com/2026/10/ndlea-issues-public-alert-after-intercepting-woman-with-drugs-concealed-in-palm-oil-keg/",
     "https://cdn.vanguardngr.com/wp-content/uploads/2026/10/NDLEA.jpeg",
     "Nigeria: Saudi-bound drugs hidden in a palm oil keg",
     "NDLEA officers at Kano airport stopped a passenger carrying drugs concealed in a palm oil keg. The wider operation recovered tramadol worth about N6.9 billion (reported as 8.7 tonnes) at Lagos.",
     "Vanguard", "Tramadol", "Nigeria"),
    ("https://thethaiger.com/hot-news/crime/thailand-intercepts-heroin-drink-sachets-australia",
     "https://thethaiger.com/wp-content/uploads/2026/10/%E0%B8%AA%E0%B8%B3%E0%B9%80%E0%B8%99%E0%B8%B2%E0%B8%82%E0%B8%AD%E0%B8%87-23-34-23-1.jpg",
     "Thailand: 7 kg of heroin in drink sachets, bound for Australia",
     "Thai authorities intercepted a parcel shipment in which heroin was packed into drink sachets. The consignment was addressed to Australia.",
     "The Thaiger", "Heroin", "Thailand"),
    ("https://thesouthfirst.com/tamilnadu/nagapattinam-crystal-meth-seizure-provides-dmk-fresh-ammo-to-target-tvk/",
     "https://static.thesouthfirst.com/wp-content/uploads/2026/10/Meth.jpg",
     "India: 142 kg of crystal meth seized in Nagapattinam",
     "A large crystal meth seizure on the Tamil Nadu coast. Reports point to a Nepal to Sri Lanka route and an arrest in Sri Lanka of a suspect tied to the case.",
     "The South First", "Methamphetamine", "India"),
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
                feat.append((r["Link"], photo, head, "; ".join(bits) + ".", outlet, r["Drug type"] or "Seizure", r["Seizure country"] or ""))
                outlets.add(outlet)
                continue
        if len(also) < n_also:
            also.append((r["Link"], head))
            outlets.add(outlet)
        if len(feat) >= n_feat and len(also) >= n_also:
            break
    return feat, also


NAVY, BLUE, TEAL, ORANGE, RED, AMBER, PURPLE, GREEN = "#0B2A4A", "#0098DA", "#12A594", "#F28C28", "#D72638", "#F5B700", "#6C4AB6", "#2E9E4F"


def tag_color(tag):
    t = (tag or "").lower()
    for keys, col in ((("cocaine",), BLUE), (("cannabis", "weed", "hash"), GREEN), (("heroin", "opium"), PURPLE),
                      (("meth", "amphet"), ORANGE), (("tramadol", "nsa", "pill", "captagon"), TEAL),
                      (("ivory", "fauna", "timber", "pangolin", "wildlife"), "#8C6A2F"),
                      (("firearm", "ammun", "arms", "weapon"), "#4A5560")):
        if any(k in t for k in keys):
            return col
    return NAVY


def bars(items, color):
    top = max([v for _, v in items] or [1])
    out = []
    for label, v in items:
        w = max(2, round(100 * v / top))
        out.append(f'<div class="bar"><span class="bl">{html.escape(str(label))}</span>'
                   f'<span class="bt"><i style="width:{w}%;background:{color}"></i></span>'
                   f'<span class="bv">{v:,}</span></div>')
    return "\n".join(out)


def qty(kg):
    kg = fnum(kg)
    return "" if kg <= 0 else (f"{kg/1000:,.1f} t" if kg >= 1000 else f"{kg:,.0f} kg")


CSS = """
*{box-sizing:border-box}
body{margin:0;background:#e9eef3;color:#1b2630;font:13px/1.55 Verdana,Geneva,'DejaVu Sans',sans-serif}
a{color:#0077b6}
.wrap{max-width:780px;margin:0 auto;background:#fff}
.banner{display:block;width:100%;height:auto}
.mast{background:#0B2A4A;color:#fff;padding:26px 32px 22px;display:flex;justify-content:space-between;align-items:flex-end}
.mast .l{flex:1}
.mast .kick{font-size:11px;letter-spacing:.28em;text-transform:uppercase;color:#F28C28;font-weight:bold}
.mast h1{margin:6px 0 0;font-size:38px;line-height:1.05;letter-spacing:.04em;text-transform:uppercase;color:#fff}
.mast .r{text-align:right;border-left:3px solid #F28C28;padding-left:18px}
.mast .wk{font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:#9fd6f2}
.mast .no{font-size:34px;font-weight:bold;line-height:1.1}
.mast .dt{font-size:12px;color:#cfe3f1}
.stripe{display:flex;height:8px}.stripe i{flex:1;display:block}
.intro{background:#eaf6fd;padding:20px 32px;font-size:15px;line-height:1.6;color:#0B2A4A}
.tiles{display:flex;gap:10px;padding:18px 32px 4px}
.tile{flex:1;color:#fff;padding:14px 14px 12px;border-radius:6px}
.tile b{display:block;font-size:30px;line-height:1.1}
.tile span{display:block;font-size:11px;letter-spacing:.06em;text-transform:uppercase;margin-top:2px}
.tile em{display:block;font-style:normal;font-size:11px;margin-top:6px;opacity:.9}
section{padding:26px 32px 0}
.sh{display:flex;align-items:center;gap:10px;margin:0 0 16px}
.sh i{display:block;width:14px;height:14px;flex:none}
.sh h2{margin:0;font-size:15px;letter-spacing:.14em;text-transform:uppercase;color:#0B2A4A}
.sh u{display:block;flex:1;height:2px;background:#d9e0e6;text-decoration:none}
.tag{display:inline-block;color:#fff;font-size:10px;font-weight:bold;letter-spacing:.1em;text-transform:uppercase;padding:3px 9px;border-radius:3px;margin-right:6px}
.ph{position:relative;background:linear-gradient(135deg,#dbe7f0,#bfd0dd);overflow:hidden}
.ph span{position:absolute;left:0;right:0;top:44%;text-align:center;font-size:11px;color:#5b6a76}
.ph img{position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover;display:block}
.lead{display:flex;gap:0;border:1px solid #d9e0e6;border-top:5px solid #D72638;margin-bottom:18px}
.lead>a{display:block;width:52%;flex:none}.lead .ph{width:100%;height:270px}
.lead .tx{padding:18px 20px;flex:1;min-width:0}
.lead .kicker{font-size:10px;font-weight:bold;letter-spacing:.2em;color:#D72638;text-transform:uppercase;margin-bottom:8px}
.lead h3{margin:8px 0 10px;font-size:21px;line-height:1.25}.lead h3 a{color:#0B2A4A;text-decoration:none}
.lead p{margin:0 0 12px}
.btn{display:inline-block;background:#0B2A4A;color:#fff!important;text-decoration:none;font-size:11px;letter-spacing:.08em;text-transform:uppercase;padding:7px 12px;border-radius:3px}
.cards{display:flex;gap:14px}
.card{flex:1;min-width:0;border:1px solid #d9e0e6}
.card .ph{height:130px}
.card .cb{padding:12px 13px 14px}
.card h3{margin:8px 0 6px;font-size:13.5px;line-height:1.3}.card h3 a{color:#0B2A4A;text-decoration:none}
.card p{margin:0 0 8px;font-size:12px}
.src{font-size:10.5px;color:#5b6a76}
table.risk{width:100%;border-collapse:collapse;font-size:12px}
table.risk td{padding:9px 8px;border-bottom:1px solid #e1e7ec;vertical-align:middle}
table.risk .sc{width:48px}
.badge{display:block;width:40px;text-align:center;color:#fff;font-weight:bold;font-size:15px;padding:6px 0;border-radius:4px}
table.risk .d{width:64px;color:#5b6a76;font-size:11px}
table.risk .it b{display:block}.risk small{color:#5b6a76}
.also{background:#fff4e6;padding:6px 18px;margin:0;list-style:none}
.also li{padding:10px 0 10px 22px;border-bottom:1px solid #f6dcb8;position:relative}
.also li:last-child{border-bottom:0}
.also li:before{content:"";position:absolute;left:0;top:15px;width:9px;height:9px;background:#F28C28}
.also a{color:#1b2630;text-decoration:none}
.band{display:flex;height:22px;margin:4px 0 8px}.band i{display:block}
.legend{font-size:11px;color:#5b6a76;margin-bottom:6px}.legend b{display:inline-block;width:10px;height:10px;margin:0 5px 0 12px}
.cols{display:flex;gap:16px;margin-top:16px}
.panel{flex:1;min-width:0;padding:14px 14px 10px;border-radius:6px}
.panel h4{margin:0 0 10px;font-size:11px;letter-spacing:.12em;text-transform:uppercase}
.bar{display:flex;align-items:center;gap:8px;margin:6px 0;font-size:11.5px}
.bl{width:34%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:none}
.bt{flex:1;background:rgba(255,255,255,.75);height:10px}.bt i{display:block;height:10px}
.bv{width:40px;text-align:right;flex:none;color:#3c4b57}
.note{padding:24px 32px 26px;font-size:10.5px;color:#5b6a76}
.foot{background:#0B2A4A;color:#cfe3f1;padding:20px 32px;font-size:11px}.foot a{color:#fff}
.foot b{color:#F28C28;letter-spacing:.14em;text-transform:uppercase}
@page{size:A4;margin:8mm 0}
@media print{body{background:#fff}.card,.lead,.tile,.panel,table.risk tr,.also li{break-inside:avoid}.sh{break-after:avoid}}
@media(max-width:640px){.mast{display:block}.mast .r{margin-top:14px;text-align:left}.mast h1{font-size:28px}.tiles,.cards,.cols,.lead{display:block}.tile{margin-bottom:8px}.card,.panel{margin-bottom:12px}.lead>a{width:100%}.lead .ph{height:210px}section,.intro,.tiles,.note,.foot,.mast{padding-left:18px;padding-right:18px}table.risk .d{display:none}}
"""


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
    bands = collections.Counter(r["Risk band"] for r in wk)
    tons = sum(fnum(r["Total quantity (kg)"]) for r in wk) / 1000
    ptons = sum(fnum(r["Total quantity (kg)"]) for r in pv) / 1000
    cont = sum(1 for r in wk if r["Container"] == "Yes")
    ctry = len({r["Seizure country"] for r in wk if r["Seizure country"]})
    delta = lambda a, b: (f"{'▲' if a >= b else '▼'} {abs(100*(a-b)/b):.0f}% vs prior week" if b else "&nbsp;")

    days = [(start + dt.timedelta(days=i)) for i in range(7)]
    dc = collections.Counter(r["Date"] for r in wk)
    daily = [(d.strftime("%a %d") + (" (partial)" if d == end and dc[d.isoformat()] < 50 else ""), dc[d.isoformat()]) for d in days]
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

    esc = html.escape

    def story_parts(f):
        link, photo, head, text, outlet, tag, country = f
        src = img_src(photo)
        img = (f'<a href="{esc(link)}"><div class="ph"><span>Photo: open the article</span>'
               f'<img src="{esc(src)}" alt="" referrerpolicy="no-referrer" onerror="this.remove()"></div></a>')
        pills = f'<span class="tag" style="background:{tag_color(tag)}">{esc(tag)}</span>' + (
            f'<span class="tag" style="background:{NAVY}">{esc(country)}</span>' if country else "")
        return link, head, text, outlet, img, pills

    lead_html, cards = "", []
    for i, f in enumerate(feat):
        link, head, text, outlet, img, pills = story_parts(f)
        if i == 0:
            lead_html = (f'<article class="lead">{img}<div class="tx"><div class="kicker">Top story</div>{pills}'
                         f'<h3><a href="{esc(link)}">{esc(head)}</a></h3><p>{esc(text)}</p>'
                         f'<p class="src">Photo and report: {esc(outlet)}</p><a class="btn" href="{esc(link)}">Read the report &rarr;</a></div></article>')
        else:
            cards.append(f'<article class="card">{img}<div class="cb">{pills}<h3><a href="{esc(link)}">{esc(head)}</a></h3>'
                         f'<p>{esc(text)}</p><p class="src">Photo and report: <a href="{esc(link)}">{esc(outlet)}</a></p></div></article>')

    seen, risk_rows = set(), []
    for r in sorted(hi, key=lambda r: -fnum(r["Risk score"])):
        key = (r["Seizure place"], r["Drug type"], r["Date"])
        if key in seen or not r["Link"]:
            continue
        seen.add(key)
        sc = int(fnum(r["Risk score"]))
        col = RED if sc >= 90 else ORANGE if sc >= 75 else AMBER
        place = ", ".join(x for x in (r["Seizure place"], r["Seizure country"]) if x) or "Place not named"
        route = f'{r["Origin"]} → {r["Destination"]}' if r["Origin"] and r["Destination"] else ""
        d = dt.date.fromisoformat(r["Date"]).strftime("%-d %b")
        risk_rows.append(f'<tr><td class="sc"><span class="badge" style="background:{col}">{sc}</span></td><td class="d">{d}</td>'
                         f'<td class="it"><b><a href="{esc(r["Link"])}">{esc(r["Drug type"])} {esc(qty(r["Total quantity (kg)"]))}</a></b>'
                         f'<small>{esc(place)}{" · " + esc(route) if route else ""}</small></td></tr>')
        if len(risk_rows) == 6:
            break

    also = "\n".join(f'<li><a href="{esc(l)}">{esc(t)}</a></li>' for l, t in also_l)

    def sect(title, color, body):
        return f'<section><div class="sh"><i style="background:{color}"></i><h2>{title}</h2><u></u></div>{body}</section>'

    fmt = lambda d: d.strftime("%-d %b")
    n_all = max(1, len(wk))
    band_html = "".join(f'<i style="width:{100*bands[b]/n_all:.1f}%;background:{c}"></i>' for b, c in (("High", RED), ("Medium", AMBER), ("Low", GREEN)))
    legend = "".join(f'<b style="background:{c}"></b>{b} {bands[b]:,}' for b, c in (("High", RED), ("Medium", AMBER), ("Low", GREEN)))
    pan = lambda title, items, col, bg: f'<div class="panel" style="background:{bg}"><h4 style="color:{col}">{title}</h4>{bars(items, col)}</div>'
    chg = (len(wk) - len(pv)) / len(pv) * 100 if pv else 0
    body = f"""<div class="wrap">
{f'<img class="banner" src="{logo}" alt="AIRCOP and Container Control Programme">' if logo else ''}
<div class="mast"><div class="l"><div class="kick">The weekly newsletter</div><h1>Seizure Watch</h1></div>
<div class="r"><div class="wk">Week</div><div class="no">{end.isocalendar()[1]}</div><div class="dt">{fmt(start)} &ndash; {fmt(end)} {end.year}</div></div></div>
<div class="stripe"><i style="background:{BLUE}"></i><i style="background:{TEAL}"></i><i style="background:{ORANGE}"></i><i style="background:{RED}"></i></div>
<div class="intro">{len(wk):,} seizure reports from {ctry} countries, {abs(chg):.0f}% {'more' if chg >= 0 else 'fewer'} than the week before. {len(hi)} were rated high risk. Cannabis ({drugs[0][1]}) and cocaine ({drugs[1][1] if len(drugs) > 1 else 0}) led the reports.</div>
<div class="tiles">
<div class="tile" style="background:{BLUE}"><b>{len(wk):,}</b><span>Seizure reports</span><em>{delta(len(wk), len(pv))}</em></div>
<div class="tile" style="background:{RED}"><b>{len(hi)}</b><span>High risk</span><em>{delta(len(hi), len(phi))}</em></div>
<div class="tile" style="background:{ORANGE}"><b>{tons:,.0f} t</b><span>Reported weight</span><em>{delta(tons, ptons)}</em></div>
<div class="tile" style="background:{TEAL}"><b>{cont}</b><span>Container cases</span><em>&nbsp;</em></div></div>
{sect("Top stories", RED, lead_html + '<div class="cards">' + "".join(cards) + '</div>')}
{sect("Risk watch: highest-risk events", ORANGE, '<table class="risk">' + "".join(risk_rows) + '</table>')}
{sect("Also making news", AMBER, '<ul class="also">' + also + '</ul>')}
{sect("The week in numbers", BLUE, f'<div class="legend">Reports by risk band {legend}</div><div class="band">{band_html}</div>'
      + '<div class="cols">' + pan("Reports per day", daily, BLUE, "#e6f4fb") + pan("Most reported drugs and goods", drugs, ORANGE, "#fff1e1") + '</div>'
      + '<div class="cols">' + pan("What was seized", cats, PURPLE, "#f0ebfa") + pan("Where seizures were made", where, TEAL, "#e2f5f2") + '</div>'
      + '<div class="cols">' + pan("Busiest routes", routes, RED, "#fde9eb") + pan("How it was hidden", conc, "#B07A00", "#fdf4d6") + '</div>')}
<p class="note">These are leads from open news sources, not confirmed facts. Verify before acting. Counts reflect what the tool found in the news it searches; a quiet country may mean no news or no coverage. Photos belong to the cited outlets and link back to their articles. Data runs to {latest}{' (the last day is partial)' if latest == end.isoformat() and dc[latest] < 50 else ''}.</p>
<div class="foot"><b>Seizure Watch</b> &middot; AIRCOP / Container Control Programme &middot; <a href="{SITE}">Full dashboard</a> &middot; <a href="{SITE}bulletin.html">Weekly bulletin</a></div>
</div>"""
    page = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Seizure Watch Weekly {fmt(start)} - {fmt(end)} {end.year}</title><style>{CSS}</style></head><body>{body}</body></html>')
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
