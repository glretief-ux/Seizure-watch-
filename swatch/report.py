# -*- coding: utf-8 -*-
"""Write the three outputs: docs/index.html (dashboard), docs/events.csv, docs/seizure_watch.xlsx."""
import json
import math
import os
import datetime as dt
import pandas as pd
from . import analyze, coverage, geo, lexicon


def _clean(v):
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    if isinstance(v, (pd.Timestamp, dt.date)):
        return v.strftime("%Y-%m-%d")
    if hasattr(v, "item"):
        v = v.item()
    return v


# languages spoken almost only in one country: a local story in them is very likely from there
LANG_HOME = {"hi": "India", "tr": "Turkey", "vi": "Vietnam"}


def outlet_homes(ev, min_stories=3, share=0.6):
    """Learn each news outlet's home country from its stories that DO name a place:
    an outlet whose placed stories are mostly (>= share) in one country is taken to be based there."""
    seen = {}
    for r in ev.itertuples():
        c = _clean(r.seizure_country)
        if not c:
            continue
        for o in (r.outlets or []):
            seen.setdefault(o, {}).setdefault(c, 0)
            seen[o][c] += 1
    homes = {}
    for o, cnt in seen.items():
        tot = sum(cnt.values()); top = max(cnt, key=cnt.get)
        if tot >= min_stories and cnt[top] / tot >= share:
            homes[o] = top
    return homes


def approx_country(r, homes):
    """Best guess for a story that names no place at all: the outlet's home country, else the language's."""
    if _clean(r.seizure_country) or _clean(r.origin) or _clean(r.destination) or list(r.transit_list or []):
        return None
    for o in (r.outlets or []):
        if o in homes:
            return homes[o]
    return LANG_HOME.get(_clean(r.lang))


def event_records(ev, homes=None):
    homes = homes or {}
    out = []
    for r in ev.itertuples():
        out.append({
            "id": int(r.event_id), "date": r.date.strftime("%Y-%m-%d"), "drug": r.primary_drug,
            "category": _clean(getattr(r, "category", None)) or "Drug",
            "kg": _clean(r.qty_kg), "units": _clean(r.qty_units), "unit_type": _clean(r.unit_type),
            "origin": _clean(r.origin), "transit": "; ".join(r.transit_list) or None, "dest": _clean(r.destination),
            "country": _clean(r.seizure_country), "place": _clean(r.seizure_place), "corridor": _clean(r.corridor),
            "route": _clean(r.route),
            "conceal": "; ".join(r.conceal_list) or None, "transport": _clean(r.transport),
            "infra": [x for x in str(_clean(getattr(r, "infrastructure", None)) or "").split("|") if x],
            "container": bool(r.in_container == 1), "insider": bool(r.insider == 1), "score": int(r.risk_score),
            "band": r.risk_band, "flags": r.risk_flags, "why": r.risk_why,
            "parts": [int(r.risk_method), int(r.risk_network), int(r.risk_route), int(r.risk_scale), int(r.risk_commodity)], "mo": _clean(r.mo_summary), "n": int(r.n_sources),
            "url": r.urls[0] if r.urls else None, "title": r.title, "title_en": _clean(getattr(r, "title_en", None)), "outlets": ", ".join(r.outlets),
            "arrests": _clean(r.arrests), "mode": r.text_mode, "lang": _clean(r.lang),
            "origin_place": _clean(r.origin_place), "dest_place": _clean(r.destination_place),
            "vessel": _clean(r.vessel), "line": _clean(r.shipping_line), "containers": _clean(r.container_numbers),
            "cover": _clean(r.cover_cargo),
            "approx": approx_country(r, homes),      # map only: country of the outlet when no place is named
        })
    return out


def export_table(ev, verifications=None):
    """Columns named to line up with the UNODC-WCO open-source workbook (drug, origin/destination, concealment, MO...)."""
    verifications = verifications or {}
    verif_status = ev["event_id"].map(lambda eid: verifications.get(eid, {}).get("status", "unverified"))
    verif_note = ev["event_id"].map(lambda eid: verifications.get(eid, {}).get("note") or None)
    df = pd.DataFrame({
        "Date": ev["date"].dt.strftime("%Y-%m-%d"),
        "Category": ev["category"].fillna("Drug") if "category" in ev.columns else "Drug",
        "Drug type": ev["primary_drug"],
        "Origin": ev["origin"], "Transit": ev["transit_list"].apply("; ".join), "Destination": ev["destination"],
        "Seizure country": ev["seizure_country"], "Seizure place": ev["seizure_place"],
        "Origin place": ev["origin_place"], "Destination place": ev["destination_place"],
        "Vessel": ev["vessel"], "Shipping line": ev["shipping_line"], "Container no.": ev["container_numbers"],
        "Cover cargo": ev["cover_cargo"],
        "Routing": ev["route"], "Concealment": ev["conceal_list"].apply("; ".join),
        "Infrastructure": ev["infrastructure"].fillna("").astype(str).apply(lambda s: "; ".join(x for x in s.split("|") if x)) if "infrastructure" in ev.columns else None,
        "Modus operandi": ev["mo_summary"], "Total quantity (kg)": ev["qty_kg"],
        "Other quantity": ev["qty_units"], "Other unit": ev["unit_type"], "Case count": 1,
        "Arrests": ev["arrests"], "Transport type": ev["transport"],
        "Container": ev["in_container"].fillna(0).astype(int).map({1: "Yes", 0: "No"}),
        "Risk score": ev["risk_score"], "Risk band": ev["risk_band"], "Risk flags": ev["risk_flags"],
        "Risk: concealment & method (max 30)": ev["risk_method"], "Risk: insiders & organised crime (max 30)": ev["risk_network"],
        "Risk: route (max 20)": ev["risk_route"], "Risk: scale (max 10)": ev["risk_scale"], "Risk: commodity (max 10)": ev["risk_commodity"],
        "Risk explanation": ev["risk_why"],
        "Reports (n)": ev["n_sources"], "Outlets": ev["outlets"].apply(", ".join),
        "Text used": ev["text_mode"], "Language": ev["lang"], "Headline": ev["title"],
        "Headline (English)": ev["title_en"] if "title_en" in ev.columns else ev["title"],
        "Unrecognised places (NER)": ev["ner_places"] if "ner_places" in ev.columns else None,
        "Verification": verif_status, "Verification note": verif_note,
        "Link": ev["urls"].apply(lambda u: u[0] if u else ""),
        "Event ID": ev["event_id"],
    })
    return df.sort_values(["Date", "Risk score"], ascending=[False, False]).reset_index(drop=True)


def write_excel(path, res, ev_export, alerts_df):
    with pd.ExcelWriter(path, engine="openpyxl") as xw:
        sheets = [("Events", ev_export), ("Alerts", alerts_df), ("Corridors", res["corridors"]),
                  ("Hotspots", res["hotspots"]),
                  ("Concealment x Drug", res["conceal"].reset_index() if len(res["conceal"]) else pd.DataFrame()),
                  ("Method", pd.DataFrame({"Notes": METHOD_NOTES}))]
        for name, df in sheets:
            (df if len(df) else pd.DataFrame({"info": ["no data yet"]})).to_excel(xw, sheet_name=name, index=False)
            ws = xw.sheets[name]
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
            for col in ws.columns:
                width = min(60, max(10, max(len(str(c.value or "")) for c in list(col)[:200]) + 2))
                ws.column_dimensions[col[0].column_letter].width = width


METHOD_NOTES = [
    "Source: public news headlines and articles (Google News RSS, GDELT, optional RSS feeds). Open-source only.",
    "Facts are extracted by keyword rules (drug, quantity, concealment, transport, route, arrests). Routing is the weakest part - verify via the link.",
    "Duplicate reports of the same seizure are merged into one event (similar headline, or same drug + quantity + country within 7 days).",
    "Date = first date the seizure was reported, not necessarily the date of seizure.",
    "Risk score (0-100) = weighted flags set in config.yaml. It ranks reports for analyst attention; it is not proof of anything.",
    "Trend/spike/NEW-corridor alerts stay quiet until at least min_history_days of data have been collected.",
    "Only facts and links are stored, not article text.",
]


def monthly_counts(ev):
    """Event counts per month x category x item x risk band over the FULL history.
    Lets the dashboard show whole months and years even after they drop out of the
    report_days window that is loaded event by event. Rows: [month, category, item, band, n]."""
    if not len(ev):
        return []
    g = pd.DataFrame({
        "m": ev["date"].dt.strftime("%Y-%m"),
        "c": ev["category"].fillna("Drug") if "category" in ev else "Drug",
        "d": ev["primary_drug"].fillna(""),
        "b": ev["risk_band"].fillna(""),
    }).groupby(["m", "c", "d", "b"]).size().reset_index(name="n")
    return [[r.m, r.c, r.d, r.b, int(r.n)] for r in g.itertuples()]


def build_dashboard(path, payload):
    data = json.dumps(payload, ensure_ascii=False, default=_clean).replace("</", "<\\/")
    geo_json = json.dumps(geo.payload(lexicon.PLACE_ALIAS), ensure_ascii=False, separators=(",", ":"))
    with open(os.path.join(os.path.dirname(__file__), "dashboard.html"), encoding="utf-8") as f:
        html = f.read()
    logo = os.path.join(os.path.dirname(__file__), "..", "assets", "pccp", "aircop-ccp-logo.png")
    try:
        import base64
        with open(logo, "rb") as lf:
            logo_uri = "data:image/png;base64," + base64.b64encode(lf.read()).decode()
    except OSError:
        logo_uri = ""          # logo file missing: the page still builds, just without it
    with open(path, "w", encoding="utf-8") as f:
        f.write(html.replace("__DATA__", data).replace("__GEO__", geo_json).replace("__LOGO__", logo_uri))


def write_all(res, out_dir, cfg, demo=False, verifications=None):
    os.makedirs(out_dir, exist_ok=True)
    ev = res["events"]
    days = cfg["run"]["report_days"]
    ev_r = ev[ev["date"] >= res["asof"] - pd.Timedelta(days=days - 1)]
    ev_export = export_table(ev_r, verifications)
    alerts_df = pd.DataFrame([{"Severity": a["severity"], "Type": a["type"], "Title": a["title"],
                               "Detail": a["detail"], "Links": "\n".join(a.get("urls", []))} for a in res["alerts"]])
    ev_export.to_csv(os.path.join(out_dir, "events.csv"), index=False, encoding="utf-8-sig")
    write_excel(os.path.join(out_dir, "seizure_watch.xlsx"), res, ev_export, alerts_df)
    payload = {
        "meta": {"asof": res["asof"].strftime("%Y-%m-%d"), "generated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                 "demo": demo, "history_days": res["history_days"], "history_ok": res["history_ok"],
                 "min_history": cfg["analysis"]["min_history_days"], "total_events": res["kpis"]["events_total"],
                 "first_date": ev["date"].min().strftime("%Y-%m-%d") if len(ev) else None,
                 "window_start": (res["asof"] - pd.Timedelta(days=days - 1)).strftime("%Y-%m-%d")},
        "coverage": coverage.payload(cfg), "risk_model": analyze.risk_model_description(cfg),
        "kpis": res["kpis"], "events": event_records(ev_r, outlet_homes(ev)), "alerts": res["alerts"],
        "monthly": monthly_counts(ev),
        "corridors": res["corridors"].head(40).to_dict("records") if len(res["corridors"]) else [],
        "hotspots": res["hotspots"].head(25).to_dict("records") if len(res["hotspots"]) else [],
    }
    build_dashboard(os.path.join(out_dir, "index.html"), payload)
    return {"events": len(ev_r), "alerts": len(res["alerts"])}
