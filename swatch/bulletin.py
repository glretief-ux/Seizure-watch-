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
    return c


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


def render_html(c):
    def li(items):
        return "".join(f"<li>{x}</li>" for x in items) or "<li>none</li>"
    corr = [f"<b>{esc(r['corridor'])}</b> - {esc(r['trend'])} ({r['events_recent']} vs {r['events_prior']} before; {esc(r['top_drug'])})" for r in c["corridors"]]
    if not corr:
        if not c["history_ok"]:
            corr = [f"Trend detection starts after {c['min_history']} days of data (now {c['history_days']}). Busiest so far: " +
                    (", ".join(f"{esc(r['corridor'])} ({r['events_recent']})" for r in c["busiest"]) or "none yet")]
        else:
            corr = ["No new or surging corridors this week."]
    unusual = []
    for u in c["unusual"]:
        bits = [u["date"], f"<b>{esc(u['drug'])}</b> {esc(u['qty'])}", esc(u["where"]), esc(u["route"]), esc(u["how"]),
                ("cargo: " + esc(u["cargo"])) if u["cargo"] else "", ("vessel: " + esc(u["vessel"])) if u["vessel"] else ""]
        link = f" <a href='{esc(u['url'])}'>source</a>" if u["url"] else ""
        col = {"High": "#c0392b", "Medium": "#e08a00"}.get(u["band"], "#2e8b57")
        unusual.append(f"<span style='background:{col};color:#fff;border-radius:9px;padding:0 6px;font-size:10px'>{u['score']}</span> " +
                       " | ".join(b for b in bits if b) + link)
    top = lambda d: ", ".join(f"{esc(k)} ({v})" for k, v in d.items()) or "none"
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Seizure Watch weekly bulletin {esc(c['period'])}</title>
<style>@page{{size:A4;margin:12mm}}body{{font:12px/1.4 -apple-system,Segoe UI,Arial,sans-serif;color:#1c2b3a;max-width:780px;margin:0 auto;padding:14px}}
h1{{font-size:18px;margin:0;background:#12355b;color:#fff;padding:12px 14px;border-radius:8px}}h1 small{{display:block;font-weight:400;font-size:12px;opacity:.85;margin-top:2px}}
h2{{font-size:13px;margin:14px 0 4px;color:#12355b;border-bottom:1px solid #d9e1ea;padding-bottom:2px}}ul{{margin:4px 0;padding-left:18px}}li{{margin:3px 0}}
.k{{display:flex;gap:8px;margin-top:10px;flex-wrap:wrap}}.k div{{flex:1;min-width:110px;background:#f3f6fa;border-radius:8px;padding:8px 10px}}.k b{{display:block;font-size:20px}}
.s{{font-size:11px;color:#5b6b7f}}a{{color:#12355b}}</style></head><body>
<h1>Seizure Watch - weekly bulletin<small>{esc(c['period'])}</small></h1>
<div class="k"><div><b>{c['n']}</b>seizure reports<br><span class="s">{('previous week ' + str(c['n_prev'])) if c['n_prev'] is not None else 'no earlier week yet'}</span></div><div><b>{c['high']}</b>high risk</div>
<div><b>{c['tonnes']} t</b>reported weight</div></div>
<p class="s">Main drugs: {top(c['top_drugs'])}. Main countries: {top(c['top_countries'])}.</p>
<h2>New and surging corridors</h2><ul>{li(corr)}</ul>
<h2>Unusual events (highest risk first)</h2><ul>{li(unusual)}</ul>
<h2>How it was hidden</h2><p>{top(c['hidden']) if c['hidden'] else 'No method reported.'}{('<br>Cover cargo named: ' + top(c['goods'])) if c['goods'] else ''}</p>
<h2>Coverage and blind spots</h2><p class="s">Searching {len(c['languages'])} languages ({esc(', '.join(c['languages']))}). {c['blind']} countries have no main language searched
(for example {esc(', '.join(c['blind_examples']))}); a quiet country may mean no news, or no coverage.</p>
<p class="s">These are leads from open sources, not confirmed facts. Verify before acting. Full dashboard: <a href="{esc(c['url'])}">{esc(c['url'])}</a></p>
</body></html>"""


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
