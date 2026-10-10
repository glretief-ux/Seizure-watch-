# -*- coding: utf-8 -*-
"""Weekly one-page bulletin: new and surging corridors, unusual events, how drugs were hidden.
Writes docs/bulletin.html (printable, one page) and docs/bulletin.txt, and can e-mail them.
The mail server and recipients come from environment variables (GitHub secrets), never from the repository."""
import html as _h
import os
import smtplib
import ssl
import datetime as dt
from email.message import EmailMessage
import pandas as pd
from . import coverage


def esc(x):
    return _h.escape(str(x if x is not None else ""))


def _qty(r):
    if pd.notna(r.qty_kg) and r.qty_kg:
        return f"{r.qty_kg / 1000:.1f} t" if r.qty_kg >= 1000 else f"{r.qty_kg:.0f} kg"
    if pd.notna(r.qty_units) and r.qty_units:
        return f"{r.qty_units:,.0f} {r.unit_type or 'units'}"
    return ""


def _line(r):
    place = r.seizure_place if isinstance(r.seizure_place, str) and r.seizure_place else (r.seizure_country if isinstance(r.seizure_country, str) else "")
    route = r.route if isinstance(r.route, str) and r.route else ""
    how = "; ".join(r.conceal_list) if len(r.conceal_list) else ""
    return {"date": r.date.strftime("%d %b"), "drug": r.primary_drug, "qty": _qty(r), "where": place, "route": route, "how": how,
            "cargo": r.cover_cargo if isinstance(r.cover_cargo, str) else "", "vessel": r.vessel if isinstance(r.vessel, str) else "",
            "score": int(r.risk_score), "band": r.risk_band, "url": (r.urls[0] if len(r.urls) else ""), "title": r.title}


def content(res, cfg):
    ev, asof = res["events"], res["asof"]
    wk_start = asof - pd.Timedelta(days=6)
    week = ev[ev["date"] >= wk_start].copy()
    prev = ev[(ev["date"] >= wk_start - pd.Timedelta(days=7)) & (ev["date"] < wk_start)]
    kg = float(week["qty_kg"].sum()) if len(week) else 0.0
    c = {"period": f"{wk_start.strftime('%d %b')} - {asof.strftime('%d %b %Y')}", "asof": asof.strftime("%Y-%m-%d"),
         "n": len(week), "n_prev": len(prev), "high": int((week["risk_band"] == "High").sum()) if len(week) else 0,
         "tonnes": round(kg / 1000, 1), "history_ok": bool(res.get("history_ok")), "history_days": res.get("history_days", 0),
         "min_history": cfg["analysis"]["min_history_days"]}
    c["top_drugs"] = week["primary_drug"].value_counts().head(3).to_dict() if len(week) else {}
    c["top_countries"] = week["seizure_country"].value_counts().head(4).to_dict() if len(week) else {}
    cor = res["corridors"]
    rows = []
    if len(cor) and c["history_ok"]:
        rows = cor[cor["trend"].isin(["NEW", "SURGING"])].head(6).to_dict("records")
    # before enough history exists a "new" or "surging" corridor only means "seen recently", so show the busiest instead
    c["busiest"] = cor.sort_values("events_recent", ascending=False).head(4).to_dict("records") if len(cor) and not rows else []
    c["corridors"] = rows
    if c["history_days"] < 14:
        c["n_prev"] = None
    top = week.sort_values(["risk_score", "qty_kg"], ascending=False, na_position="last").head(6)
    c["unusual"] = [_line(r) for r in top.itertuples()]
    conc = week.explode("conceal_list")
    conc = conc[conc["conceal_list"].notna() & (conc["conceal_list"] != "")]
    c["hidden"] = conc["conceal_list"].value_counts().head(3).to_dict() if len(conc) else {}
    goods = {}
    for v in week["cover_cargo"].dropna() if "cover_cargo" in week else []:
        for g in str(v).split(";"):
            g = g.strip()
            if g:
                goods[g] = goods.get(g, 0) + 1
    c["goods"] = dict(sorted(goods.items(), key=lambda kv: -kv[1])[:5])
    cov = coverage.payload(cfg)
    blind = [k for k, v in cov["countries"].items() if not set(v["langs"]) & set(cov["searched"])]
    c["languages"] = [cov["names"].get(x, x) for x in cov["searched"]]
    c["blind"] = len(blind)
    c["blind_examples"] = blind[:6]
    c["url"] = (cfg.get("bulletin", {}) or {}).get("dashboard_url", "")
    _chart_data(c, week, prev, wk_start, res)
    return c


def _chart_data(c, week, prev, wk_start, res):
    """Numbers behind the charts in the HTML bulletin."""
    def vc(df, col, n):
        return list(df[col].dropna().astype(str).value_counts().head(n).items()) if len(df) and col in df else []
    days = []
    for i in range(7):
        d = wk_start + pd.Timedelta(days=i)
        sub = week[week["date"] == d]
        days.append({"label": d.strftime("%a"), "date": d.strftime("%d %b"), "High": int((sub["risk_band"] == "High").sum()),
                     "Medium": int((sub["risk_band"] == "Medium").sum()), "Low": int((sub["risk_band"] == "Low").sum())})
    c["daily"] = days
    c["bands"] = {b: int((week["risk_band"] == b).sum()) if len(week) else 0 for b in ("High", "Medium", "Low")}
    c["drug_bars"] = vc(week, "primary_drug", 8)
    c["country_bars"] = vc(week, "seizure_country", 8)
    conc = week.explode("conceal_list") if len(week) else week
    conc = conc[conc["conceal_list"].notna() & (conc["conceal_list"] != "")] if len(conc) else conc
    c["hidden_bars"] = vc(conc, "conceal_list", 6)
    cats = week["category"].fillna("Drug") if len(week) and "category" in week else pd.Series(dtype=str)
    c["cat_bars"] = list(cats.value_counts().items()) if len(cats) else []
    trend = {}
    if len(res["corridors"]) and c["history_ok"]:
        trend = dict(zip(res["corridors"]["corridor"], res["corridors"]["trend"]))
    corr = week[week["corridor"].notna()] if len(week) else week
    c["corr_bars"] = [(k, int(v), trend.get(k, "")) for k, v in corr["corridor"].value_counts().head(7).items()] if len(corr) else []

    def cnt(df, col):
        return int((df[col].fillna(0).astype(int) == 1).sum()) if len(df) and col in df else 0
    ok = c["n_prev"] is not None
    c["kpi"] = {"n": c["n"], "n_prev": c["n_prev"],
                "high": c["high"], "high_prev": int((prev["risk_band"] == "High").sum()) if ok and len(prev) else None,
                "tonnes": c["tonnes"], "tonnes_prev": round(float(prev["qty_kg"].sum()) / 1000, 1) if ok and len(prev) else None,
                "container": cnt(week, "in_container"), "container_prev": cnt(prev, "in_container") if ok else None,
                "insider": cnt(week, "insider"), "insider_prev": cnt(prev, "insider") if ok else None,
                "avg": round(float(week["risk_score"].mean()), 1) if len(week) else 0}
    c["countries_n"] = int(week["seizure_country"].nunique()) if len(week) else 0
    hi = week[week["risk_band"].isin(["High", "Medium"])] if len(week) else week
    c["dim_n"] = len(hi)
    c["dim_bars"] = [(lab, round(float(hi[col].mean()), 1)) for lab, col in
                     (("Method (max 30)", "risk_method"), ("Insiders & network (max 30)", "risk_network"),
                      ("Route (max 20)", "risk_route"), ("Scale (max 10)", "risk_scale"), ("Commodity (max 10)", "risk_commodity"))
                     if col in hi] if len(hi) else []


def render_text(c):
    L = [f"SEIZURE WATCH - weekly bulletin, {c['period']}", "",
         f"{c['n']} seizure reports this week" + (f" (previous week {c['n_prev']})" if c["n_prev"] is not None else "") + f"; {c['high']} high risk; {c['tonnes']} t reported.",
         "Main drugs: " + (", ".join(f"{k} ({v})" for k, v in c["top_drugs"].items()) or "none"),
         "Main countries: " + (", ".join(f"{k} ({v})" for k, v in c["top_countries"].items()) or "none"), ""]
    L.append("NEW AND SURGING CORRIDORS")
    if c["corridors"]:
        for r in c["corridors"]:
            L.append(f"- {r['corridor']}: {r['trend']} ({r['events_recent']} this period, {r['events_prior']} before; mainly {r['top_drug']})")
    elif not c["history_ok"]:
        L.append(f"- Trend detection starts after {c['min_history']} days of data (now {c['history_days']}). Busiest corridors instead:")
        L += [f"  {r['corridor']}: {r['events_recent']} reports" for r in c["busiest"]] or ["  none yet"]
    else:
        L.append("- No new or surging corridors this week.")
    L += ["", "UNUSUAL EVENTS (highest risk first)"]
    for u in c["unusual"] or []:
        bits = [u["date"], u["drug"], u["qty"], u["where"], u["route"], u["how"], ("cargo: " + u["cargo"]) if u["cargo"] else "",
                ("vessel: " + u["vessel"]) if u["vessel"] else ""]
        L.append(f"- [{u['band']} {u['score']}] " + " | ".join(b for b in bits if b))
        if u["url"]:
            L.append("  " + u["url"])
    if not c["unusual"]:
        L.append("- none")
    L += ["", "HOW IT WAS HIDDEN: " + (", ".join(f"{k} ({v})" for k, v in c["hidden"].items()) or "no method reported")]
    if c["goods"]:
        L.append("Cover cargo named: " + ", ".join(f"{k} ({v})" for k, v in c["goods"].items()))
    L += ["", f"Coverage: searching {len(c['languages'])} languages ({', '.join(c['languages'])}). {c['blind']} countries have no main language searched "
              f"(e.g. {', '.join(c['blind_examples'])}).",
          "Leads from open sources, not confirmed facts. Verify before acting.", c["url"]]
    return "\n".join(L)


def _logo_uri():
    """The AIRCOP / Container Control Programme logo as an inline image (empty if the file is missing)."""
    import base64
    try:
        with open(os.path.join(os.path.dirname(__file__), "..", "assets", "pccp", "aircop-ccp-logo.png"), "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode()
    except OSError:
        return ""


NAVY, BLUE, TEAL, AMBER, RED, GREEN, PURPLE, GREY = "#12355b", "#2f6db5", "#1a9aa0", "#e08a00", "#c0392b", "#2e8b57", "#6a3fb5", "#8894a5"
BAND_COL = {"High": RED, "Medium": AMBER, "Low": GREEN}
SERIES = [BLUE, TEAL, AMBER, PURPLE, GREEN, RED, "#8c6d31", GREY]
TREND_COL = {"NEW": PURPLE, "SURGING": RED, "STABLE": BLUE, "DECLINING": TEAL}
FONT = "Verdana,'DejaVu Sans',Arial,sans-serif"


def _short(t, n):
    t = str(t)
    return t if len(t) <= n else t[:n - 1].rstrip() + "..."


def _hbar(items, colors=None, w=380, label_w=150, row=24, empty="No data this week"):
    """Horizontal bar chart as inline SVG. items = [(label, value), ...]"""
    if not items:
        return f'<div class="empty">{empty}</div>'
    mx = max(v for _, v in items) or 1
    bar_w = w - label_w - 36
    h = row * len(items) + 4
    out = [f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" style="display:block;font-family:{FONT}">']
    for i, (lab, v) in enumerate(items):
        y = i * row + 2
        col = (colors[i] if colors else SERIES[i % len(SERIES)])
        bw = max(3, bar_w * v / mx)
        out.append(f'<text x="{label_w - 8}" y="{y + row / 2 + 4}" text-anchor="end" font-size="10.5" fill="#33445a">{esc(_short(lab, 26))}</text>')
        out.append(f'<rect x="{label_w}" y="{y + 3}" width="{bw:.1f}" height="{row - 8}" rx="3" fill="{col}"/>')
        out.append(f'<text x="{label_w + bw + 6:.1f}" y="{y + row / 2 + 4}" font-size="10.5" font-weight="700" fill="#1c2b3a">{v}</text>')
    out.append("</svg>")
    return "".join(out)


def _columns(days, w=380, h=190):
    """Reports per day, stacked by risk band."""
    mx = max([d["High"] + d["Medium"] + d["Low"] for d in days] + [1])
    top, bottom, left = 18, 34, 28
    ph = h - top - bottom
    bw = (w - left - 8) / len(days)
    out = [f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" style="display:block;font-family:{FONT}">']
    for frac in (0, .5, 1):
        y = top + ph - ph * frac
        out.append(f'<line x1="{left}" y1="{y:.1f}" x2="{w - 6}" y2="{y:.1f}" stroke="#e3e8ef"/>'
                   f'<text x="{left - 5}" y="{y + 3:.1f}" text-anchor="end" font-size="9" fill="#66758a">{round(mx * frac)}</text>')
    for i, d in enumerate(days):
        x = left + i * bw + bw * .18
        y = top + ph
        for band in ("Low", "Medium", "High"):
            v = d[band]
            if not v:
                continue
            hh = ph * v / mx
            y -= hh
            out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw * .64:.1f}" height="{hh:.1f}" fill="{BAND_COL[band]}"/>')
        tot = d["High"] + d["Medium"] + d["Low"]
        out.append(f'<text x="{x + bw * .32:.1f}" y="{y - 4:.1f}" text-anchor="middle" font-size="10" font-weight="700" fill="#1c2b3a">{tot}</text>')
        out.append(f'<text x="{x + bw * .32:.1f}" y="{h - 18}" text-anchor="middle" font-size="10" fill="#33445a">{d["label"]}</text>'
                   f'<text x="{x + bw * .32:.1f}" y="{h - 7}" text-anchor="middle" font-size="8.5" fill="#66758a">{d["date"][:2]}</text>')
    out.append("</svg>")
    return "".join(out)


def _donut(parts, size=150, centre=""):
    tot = sum(v for _, v, _ in parts) or 1
    r, circ, off = 52, 2 * 3.14159265 * 52, 0.0
    out = [f'<svg viewBox="0 0 130 130" width="{size}" height="{size}" role="img" style="font-family:{FONT}">',
           '<circle cx="65" cy="65" r="52" fill="none" stroke="#eef2f7" stroke-width="20"/>']
    for lab, v, col in parts:
        if not v:
            continue
        ln = circ * v / tot
        out.append(f'<circle cx="65" cy="65" r="{r}" fill="none" stroke="{col}" stroke-width="20" stroke-dasharray="{ln:.2f} {circ - ln:.2f}" '
                   f'stroke-dashoffset="{-off:.2f}" transform="rotate(-90 65 65)"/>')
        off += ln
    out.append(f'<text x="65" y="63" text-anchor="middle" font-size="22" font-weight="700" fill="#12355b">{tot}</text>'
               f'<text x="65" y="78" text-anchor="middle" font-size="9" fill="#66758a">{esc(centre)}</text></svg>')
    return "".join(out)


def _delta(now, before, unit="", good_down=False):
    if before is None:
        return '<span class="dl nd">no earlier week yet</span>'
    d = round(now - before, 1)
    if d == 0:
        return '<span class="dl nd">same as last week</span>'
    up = d > 0
    bad = up if good_down else not up
    cls = "dn" if (up and not good_down) or (not up and good_down) else "up"
    cls = "bad" if (up and good_down) else cls
    arrow = "&#9650;" if up else "&#9660;"
    pct = f" ({abs(d) / before * 100:.0f}%)" if before else ""
    return f'<span class="dl {"hi" if up else "lo"}">{arrow} {abs(d):g}{unit}{pct} vs last week</span>'


def _panel(title, body, cls=""):
    return f'<section class="panel {cls}"><h2>{title}</h2><div class="pb">{body}</div></section>'


def render_html(c):
    k = c["kpi"]
    cards = [("Seizure reports", k["n"], "", k["n_prev"], NAVY), ("High risk", k["high"], "", k["high_prev"], RED),
             ("Reported weight", f"{k['tonnes']} t", "", None, TEAL), ("Container cases", k["container"], "", k["container_prev"], BLUE),
             ("Insider signals", k["insider"], "", k["insider_prev"], PURPLE)]
    prev_by = {"Seizure reports": k["n_prev"], "High risk": k["high_prev"], "Container cases": k["container_prev"], "Insider signals": k["insider_prev"]}
    kp = []
    for lab, val, _, prv, col in cards:
        if lab == "Reported weight":
            dl = _delta(k["tonnes"], k["tonnes_prev"], " t") if k["tonnes_prev"] is not None else '<span class="dl nd">&nbsp;</span>'
        else:
            dl = _delta(val, prv)
        kp.append(f'<div class="kc" style="border-top-color:{col}"><span class="kl">{lab}</span><b style="color:{col}">{val}</b>{dl}</div>')

    # headline sentence
    lead = f"{c['n']} seizure reports from {c['countries_n']} countries"
    if c["n_prev"]:
        ch = (c["n"] - c["n_prev"]) / c["n_prev"] * 100
        lead += f", {abs(ch):.0f}% {'more' if ch >= 0 else 'fewer'} than the week before"
    lead += f". {c['high']} rated High risk; average risk score {k['avg']}."
    if c["drug_bars"]:
        lead += f" Most reported: {esc(c['drug_bars'][0][0])} ({c['drug_bars'][0][1]})."

    daily = _columns(c["daily"]) + ('<div class="lg"><i style="background:%s"></i>High <i style="background:%s"></i>Medium <i style="background:%s"></i>Low &nbsp;&middot;&nbsp; the latest day may be incomplete</div>' % (RED, AMBER, GREEN))
    bands = [(b, c["bands"][b], BAND_COL[b]) for b in ("High", "Medium", "Low")]
    donut = '<div class="dn">' + _donut(bands, 130, "reports") + '<div class="lgv">' + "".join(
        f'<div><i style="background:{col}"></i><b>{v}</b> {lab}</div>' for lab, v, col in bands) + "</div></div>"
    drug_cols = [SERIES[i % len(SERIES)] for i in range(len(c["drug_bars"]))]
    if c["corr_bars"]:
        corr_html = _hbar([(a, b) for a, b, _ in c["corr_bars"]], [TREND_COL.get(t, BLUE) for _, _, t in c["corr_bars"]], label_w=170) + \
            '<div class="lg"><i style="background:%s"></i>New <i style="background:%s"></i>Surging <i style="background:%s"></i>Other</div>' % (PURPLE, RED, BLUE)
        if not c["history_ok"]:
            corr_html += f'<div class="note">New / surging labels start after {c["min_history"]} days of data (now {c["history_days"]}).</div>'
    else:
        corr_html = '<div class="empty">No routes with a known origin and destination this week</div>'
    hidden = _hbar(c["hidden_bars"], [TEAL] * len(c["hidden_bars"]), label_w=190)
    countries = _hbar(c["country_bars"], [BLUE] * len(c["country_bars"]), label_w=120)
    cats = ""
    if len(c["cat_bars"]) > 1:
        cats = _panel("What was seized", _hbar(c["cat_bars"], [NAVY, PURPLE, TEAL, AMBER, GREEN, RED, GREY][:len(c["cat_bars"])], label_w=150))
    drivers = _panel("What drives the higher-risk reports",
                     _hbar(c["dim_bars"], [BLUE, PURPLE, TEAL, AMBER, GREY], label_w=200) +
                     f'<div class="note">Average points per report, {c["dim_n"]} Medium and High reports. Size alone never makes a report High.</div>') if c["dim_bars"] else ""

    rows = []
    for u in c["unusual"]:
        bits = [x for x in (esc(u["where"]), esc(u["route"]), esc(u["how"]), ("cargo: " + esc(u["cargo"])) if u["cargo"] else "",
                            ("vessel: " + esc(u["vessel"])) if u["vessel"] else "") if x]
        link = f' <a href="{esc(u["url"])}">source</a>' if u["url"] else ""
        rows.append(f'<tr><td class="c"><span class="chip" style="background:{BAND_COL.get(u["band"], GREEN)}">{u["score"]}</span></td>'
                    f'<td class="nw">{esc(u["date"])}</td><td><b>{esc(u["drug"])}</b><br><span class="s">{esc(u["qty"])}</span></td>'
                    f'<td class="s2">{" | ".join(bits)}{link}</td></tr>')
    table = ('<table class="tb"><tr><th>Risk</th><th>Date</th><th>Item</th><th>Where, route and method</th></tr>' + "".join(rows) + "</table>") if rows else '<div class="empty">No events this week</div>'

    web = ""
    if c.get("url"):
        web = f'<div class="web">Charts show best in a browser: <a href="{esc(c["url"])}bulletin.html">open the online version</a>.</div>'
    logo = _logo_uri()
    logo_html = f'<div class="lg0"><img src="{logo}" alt="AIRCOP - Container Control Programme"></div>' if logo else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Seizure Watch weekly bulletin {esc(c['period'])}</title>
<style>
@page{{size:A4;margin:9mm}}
*{{box-sizing:border-box}}
body{{margin:0;background:#eef2f7;color:#1c2b3a;font:12px/1.45 {FONT};-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.wrap{{max-width:860px;margin:0 auto;padding:12px}}
.lg0{{text-align:center;margin:0 0 10px}}.lg0 img{{height:60px;max-width:90%}}
.hero{{background:linear-gradient(135deg,#0d2a4a,#1d4f86);color:#fff;border-radius:12px;padding:18px 20px}}
.hero h1{{margin:0;font-size:21px;letter-spacing:.3px}}.hero .sub{{opacity:.85;margin-top:3px;font-size:12px}}
.hero .lead{{margin-top:12px;padding-top:10px;border-top:1px solid rgba(255,255,255,.25);font-size:12.5px;line-height:1.5}}
.kpis{{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin:10px 0}}
.kc{{background:#fff;border-radius:10px;border-top:4px solid #12355b;padding:9px 10px;box-shadow:0 1px 2px rgba(0,0,0,.07)}}
.kc .kl{{display:block;font-size:9.5px;text-transform:uppercase;letter-spacing:.5px;color:#66758a}}.kc b{{display:block;font-size:24px;line-height:1.15;margin:2px 0}}
.dl{{font-size:9.5px;color:#66758a}}.dl.hi{{color:#b03a2e}}.dl.lo{{color:#1e7d4f}}.dl.nd{{color:#99a5b5}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}.full{{grid-column:1/-1}}
.panel{{background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 1px 2px rgba(0,0,0,.07);break-inside:avoid;page-break-inside:avoid}}
.panel h2{{margin:0;padding:8px 12px;background:#12355b;color:#fff;font-size:12px;letter-spacing:.2px}}.pb{{padding:10px 12px 12px}}
.dn{{display:flex;align-items:center;gap:14px;justify-content:center}}.lgv div{{margin:5px 0;font-size:12px}}
i{{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px;vertical-align:-1px}}.lg{{font-size:10px;color:#44546a;margin-top:4px}}.lg i{{margin-left:8px}}.lg i:first-child{{margin-left:0}}
.empty,.note{{color:#66758a;font-size:11px;padding:8px 0}}.note{{padding:4px 0 0}}
table.tb{{width:100%;border-collapse:collapse}}.tb th{{background:#f0f3f7;text-align:left;font-size:10px;text-transform:uppercase;letter-spacing:.4px;color:#66758a;padding:6px 8px}}
.tb td{{padding:7px 8px;vertical-align:top;border-top:1px solid #e6ebf2}}.tb tr:nth-child(even) td{{background:#eaf1fa}}.tb td.c{{width:44px}}.nw{{white-space:nowrap}}
.chip{{display:inline-block;min-width:26px;text-align:center;color:#fff;font-weight:700;font-size:11px;border-radius:99px;padding:1px 7px}}
.s,.s2{{color:#5b6b7f;font-size:11px}}a{{color:#12355b}}
.how{{font-size:10.5px;color:#44546a;line-height:1.5}}.how b{{color:#12355b}}
.foot{{margin:10px 2px 0;font-size:10px;color:#66758a;line-height:1.5}}.web{{text-align:center;font-size:11px;margin:6px 0}}
@media(max-width:640px){{.kpis{{grid-template-columns:repeat(2,1fr)}}.grid{{grid-template-columns:1fr}}}}
@media print{{body{{background:#fff}}.wrap{{padding:0;max-width:none}}.web{{display:none}}}}
</style></head><body><div class="wrap">
{web}{logo_html}
<div class="hero"><h1>SEIZURE WATCH &mdash; Weekly Bulletin</h1><div class="sub">{esc(c['period'])}</div><div class="lead">{lead}</div></div>
<div class="kpis">{''.join(kp)}</div>
<div class="grid">
{_panel('Reports per day, by risk band', daily)}
{_panel('Risk bands', donut)}
{_panel('Most reported drugs and goods', _hbar(c['drug_bars'], drug_cols, label_w=130))}
{cats}
{_panel('Busiest routes (origin &rarr; destination)', corr_html)}
{_panel('Where seizures were made', countries)}
{_panel('How it was hidden', hidden)}
{drivers}
{_panel('Highest-risk events this week', table, 'full')}
</div>
<div class="foot"><b>How the risk score works.</b> Each report scores up to 100 from five separate areas: how it was smuggled (30), who was behind it (30), the route (20), the size (10) and the harm of the goods (10). Size alone can never make an event High.<br>
<b>Coverage.</b> Searching {len(c['languages'])} languages ({esc(', '.join(c['languages']))}). {c['blind']} countries have no main language searched (for example {esc(', '.join(c['blind_examples']))}); a quiet country may mean no news, or no coverage.<br>
These are leads from open sources, not confirmed facts. Verify before acting.{(' Full dashboard: <a href="' + esc(c['url']) + '">' + esc(c['url']) + '</a>') if c.get('url') else ''}</div>
</div></body></html>"""


def build(res, cfg, out_dir):
    c = content(res, cfg)
    html, text = render_html(c), render_text(c)
    with open(os.path.join(out_dir, "bulletin.html"), "w", encoding="utf-8") as f:
        f.write(html)
    with open(os.path.join(out_dir, "bulletin.txt"), "w", encoding="utf-8") as f:
        f.write(text)
    return {"content": c, "html": html, "text": text}


def is_due(last_sent, today, weekday=0):
    """Once a week: the first run on the chosen weekday, or the next run if a week has gone by."""
    if not last_sent:
        return today.weekday() == weekday
    try:
        return (today - dt.date.fromisoformat(last_sent)).days >= 7
    except ValueError:
        return True


def send_email(b, subject=None, env=os.environ):
    """Send the bulletin. Returns (sent, message). Needs SMTP_HOST, SMTP_USER, SMTP_PASS and BULLETIN_TO."""
    host, user, pw, to = (env.get(k, "").strip() for k in ("SMTP_HOST", "SMTP_USER", "SMTP_PASS", "BULLETIN_TO"))
    if not (host and user and pw and to):
        return False, "e-mail is not set up (add the SMTP_HOST, SMTP_USER, SMTP_PASS and BULLETIN_TO secrets)"
    port = int(env.get("SMTP_PORT", "").strip() or 587)
    msg = EmailMessage()
    msg["Subject"] = subject or f"Seizure Watch weekly bulletin - {b['content']['period']}"
    msg["From"] = env.get("BULLETIN_FROM", "").strip() or user
    msg["To"] = ", ".join(x.strip() for x in to.replace(";", ",").split(",") if x.strip())
    msg.set_content(b["text"])
    msg.add_alternative(b["html"], subtype="html")
    ctx = ssl.create_default_context()
    try:
        if port == 465:
            with smtplib.SMTP_SSL(host, port, context=ctx, timeout=30) as s:
                s.login(user, pw)
                s.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=30) as s:
                s.starttls(context=ctx)
                s.login(user, pw)
                s.send_message(msg)
    except Exception as e:                      # never stop the daily run because of mail trouble
        return False, f"could not send: {type(e).__name__}: {e}"[:200]
    return True, f"sent to {msg['To']}"
