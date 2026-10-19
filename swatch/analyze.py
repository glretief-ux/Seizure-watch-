# -*- coding: utf-8 -*-
"""
Turn stored articles into risk indicators.

Three layers:
  1. EVENT layer    - one row per seizure (duplicate reports merged), with a 0-100 risk score
  2. PATTERN layer  - corridors, concealment x drug, hotspots, trends vs prior period
  3. ALERT layer    - spikes, new/surging corridors, insider signals, top-risk events (plain-English)
"""
import numpy as np
import pandas as pd
from . import cover as _cover
from .lexicon import LEGIT_CATEGORIES, ADVANCED_CATEGORIES

FLAG_LABELS = {
    "container_cargo": "Container cargo",
    "concealed_in_legit_cargo": "Hidden in legitimate cargo",
    "advanced_concealment": "Advanced concealment",
    "quantity_outlier": "Large quantity",
    "multi_country_route": "Multi-country route",
    "emerging_corridor": "Emerging corridor",
    "organized_network": "Organised network",
    "insider_indicator": "Insider indicator",
    "polydrug": "Multiple drugs",
    "false_declaration": "False declaration or no permit",
    "front_company": "Front or new company",
    "repeat_entity": "Repeat vessel or container",
    "intel_tip": "Intelligence-led",
    "transshipment": "Transshipment or free zone",
    "route_change": "Route change or diversion",
}


DIM_LABELS = {"method": "Concealment & method", "network": "Insiders & organised crime", "route": "Route",
              "scale": "Scale", "commodity": "Commodity"}
_CAPS = {}   # set from config.yaml (risk -> caps) by risk_model_description / score_events


def _cap(d, P):
    s = sum(P[d].values())
    return min(s, _CAPS[d]) if d in _CAPS else s


DIM_MAX = {"method": lambda P: _cap("method", P), "network": lambda P: _cap("network", P),
           "route": lambda P: _cap("route", P), "scale": lambda P: sum(P["scale"].values()),
           "commodity": lambda P: max(P["commodity"].values())}


def risk_model_description(cfg):
    """How the score is built, for the dashboard's 'How risk is scored' box (always in sync with config.yaml)."""
    R = cfg["risk"]; P = R["points"]
    _CAPS.update(R.get("caps") or {})
    dims = []
    for d in ("method", "network", "route", "scale"):
        dims.append({"name": DIM_LABELS[d], "max": DIM_MAX[d](P),
                     "items": [{"label": FLAG_LABELS[k], "points": v} for k, v in P[d].items()]})
    dims.append({"name": DIM_LABELS["commodity"], "max": DIM_MAX["commodity"](P),
                 "items": [{"label": "Tier %d goods: %s" % (t, ", ".join(names[:6]) + ("..." if len(names) > 6 else "")), "points": P["commodity"].get(int(t), 0)}
                           for t, names in R["commodity_tiers"]["items"].items()]})
    wl = R.get("watchlist") or {}
    return {"dimensions": dims, "watchlist_on": any(wl.get(k) for k in ("vessels", "containers", "terms")),
            "high": R["bands"]["high"], "medium": R["bands"]["medium"],
            "min_high": R.get("min_dimensions_high", 2), "min_medium": R.get("min_dimensions_medium", 1)}


# ------------------------------------------------------------------ 1. events
def load_events(conn):
    df = pd.read_sql_query("SELECT * FROM articles WHERE relevant=1 AND event_id IS NOT NULL", conn)
    if df.empty:
        return df
    df["published"] = pd.to_datetime(df["published"], errors="coerce").dt.normalize()
    df = df.dropna(subset=["published"])
    # the stored cover cargo is whatever goods word the extractor matched, in any language and with some noise:
    # keep recognised goods only, named in English (see cover.py)
    df["cover_cargo"] = [_cover.clean(c, t, te) for c, t, te in zip(df["cover_cargo"], df["title"], df["title_en"])]
    df = df.sort_values(["event_id", "completeness", "qty_kg"], ascending=[True, False, False], na_position="last")
    g = df.groupby("event_id", sort=False)
    best = g.head(1).set_index("event_id")
    agg = g.agg(n_sources=("id", "size"), first_seen=("published", "min"),
                urls=("url", lambda s: list(s)[:5]),
                outlets=("source", lambda s: sorted({x for x in s if x})[:6]),
                # indicators found in ANY report of the event count for the event
                in_container_any=("in_container", "max"), insider_any=("insider", "max"),
                organized_any=("organized", "max"), coverload_any=("coverload", "max"),
                controlled_any=("controlled_delivery", "max"), arrests_any=("arrests", "max"),
                indicators_any=("indicators", lambda s: "|".join(sorted({c for x in s.dropna() for c in str(x).split("|") if c}))),
                conceal_any=("concealment", lambda s: "|".join(sorted({c for x in s.dropna() for c in x.split("|") if c}))),
                vessel_any=("vessel", lambda s: next((x for x in s.dropna() if x), None)),
                line_any=("shipping_line", lambda s: "; ".join(sorted({c.strip() for x in s.dropna() for c in x.split(";") if c.strip()})) or None),
                cont_any=("container_numbers", lambda s: "; ".join(sorted({c.strip() for x in s.dropna() for c in x.split(";") if c.strip()})[:5]) or None),
                type_any=("drug_type", lambda s: s.dropna().mode().iat[0] if s.notna().any() else None),
                cover_any=("cover_cargo", lambda s: "; ".join(list(dict.fromkeys(c.strip() for x in s.dropna() for c in x.split(";") if c.strip()))[:4]) or None))
    ev = best.join(agg).reset_index()
    ev["drug_type"] = ev["type_any"]
    for a, b in [("vessel", "vessel_any"), ("shipping_line", "line_any"), ("container_numbers", "cont_any"), ("cover_cargo", "cover_any")]:
        ev[a] = ev[b]
    for a, b in [("in_container", "in_container_any"), ("insider", "insider_any"), ("organized", "organized_any"),
                 ("coverload", "coverload_any"), ("controlled_delivery", "controlled_any"), ("arrests", "arrests_any")]:
        ev[a] = ev[b]
    # entity recognition also stores police forces and stray words as "shipping line" / "vessel": keep only plausible ones
    from . import links as _links
    ev["shipping_line"] = ev["shipping_line"].apply(_links.clean_lines)
    ev["vessel"] = ev["vessel"].apply(_links.clean_vessel)
    ev["concealment"] = ev["conceal_any"].replace("", None)
    ev["indicators"] = ev["indicators_any"].replace("", None)
    ev = ev.drop(columns=[c for c in ev.columns if c.endswith("_any")])
    ev["date"] = ev["first_seen"]
    return ev.sort_values("date").reset_index(drop=True)


def _qty_outlier(ev, R):
    thr, uthr = R["quantity_thresholds_kg"], R["unit_thresholds"]
    p95 = {}
    for d, g in ev.groupby("primary_drug"):
        q = g["qty_kg"].dropna()
        if len(q) >= R.get("percentile_min_events", 30):
            p95[d] = q.quantile(0.95)
    flags = []
    for r in ev.itertuples():
        f = False
        if pd.notna(r.qty_kg):
            f = r.qty_kg >= thr.get(r.primary_drug, thr.get("default", 200)) or \
                (r.primary_drug in p95 and r.qty_kg >= p95[r.primary_drug])
        if not f and pd.notna(r.qty_units) and r.unit_type in uthr:
            f = r.qty_units >= uthr[r.unit_type]
        flags.append(f)
    return pd.Series(flags, index=ev.index)


def score_events(ev, cfg, asof):
    R, A = cfg["risk"], cfg["analysis"]
    ev = ev.copy()
    ev["conceal_list"] = ev["concealment"].fillna("").apply(lambda s: [c for c in s.split("|") if c])
    ev["transit_list"] = ev["transit"].fillna("").apply(lambda s: [c for c in s.split("|") if c])
    ev["drug_list"] = ev["drugs"].fillna("").apply(lambda s: [c for c in s.split("|") if c])
    f = pd.DataFrame(index=ev.index)
    f["container_cargo"] = ev["in_container"].fillna(0).astype(int) == 1
    f["concealed_in_legit_cargo"] = ev["conceal_list"].apply(lambda c: any(x in LEGIT_CATEGORIES for x in c)) | \
        (ev["coverload"].fillna(0).astype(int) == 1)
    f["advanced_concealment"] = ev["conceal_list"].apply(lambda c: any(x in ADVANCED_CATEGORIES for x in c))
    f["quantity_outlier"] = _qty_outlier(ev, R)

    def n_countries(r):
        s = {x for x in [r.origin, r.destination, r.seizure_country] + r.transit_list if x}
        return len(s)
    f["multi_country_route"] = ev.apply(lambda r: n_countries(r) >= 3 or len(r.transit_list) > 0, axis=1)

    history = (ev["date"].max() - ev["date"].min()).days if len(ev) else 0
    if history >= A["min_history_days"]:
        first = ev[ev["corridor"].notna()].groupby("corridor")["date"].min()
        cutoff = asof - pd.Timedelta(days=A["emerging_days"])
        f["emerging_corridor"] = ev["corridor"].map(lambda c: bool(c) and c in first.index and first[c] >= cutoff)
    else:
        f["emerging_corridor"] = False
    f["organized_network"] = ev["organized"].fillna(0).astype(int) == 1
    f["insider_indicator"] = ev["insider"].fillna(0).astype(int) == 1
    f["polydrug"] = ev["drug_list"].apply(lambda d: len([x for x in d if x != "Unspecified"]) >= 2)
    # indicators read from article text (see lexicon.py), kept in one column
    ind = ev["indicators"].fillna("").astype(str).apply(lambda x: set(x.split("|")) - {""}) if "indicators" in ev else \
        pd.Series([set()] * len(ev), index=ev.index)
    for k in ("false_declaration", "front_company", "transshipment", "route_change", "intel_tip"):
        f[k] = ind.apply(lambda s_, k=k: k in s_)
    # the same vessel or container in more than one seizure (a repeat is a lead, not proof)
    seen = {}
    for r in ev.itertuples():
        for name in ([str(r.vessel).strip().lower()] if isinstance(r.vessel, str) and r.vessel else []) + \
                    [c.strip() for c in str(r.container_numbers or "").split(";") if c.strip()]:
            seen.setdefault(name, set()).add(r.event_id)
    f["repeat_entity"] = [any(len(seen.get(n, ())) >= 2 for n in
                              ([str(r.vessel).strip().lower()] if isinstance(r.vessel, str) and r.vessel else []) +
                              [c.strip() for c in str(r.container_numbers or "").split(";") if c.strip()])
                          for r in ev.itertuples()]
    f["repeat_entity"] = pd.Series(f["repeat_entity"], index=ev.index)

    # ---- five dimensions, each with its own cap (see config.yaml -> risk -> points) ----
    P = R["points"]
    cat = ev["category"].fillna("Drug") if "category" in ev else pd.Series("Drug", index=ev.index)
    tiers = R["commodity_tiers"]

    def tier(r_item, r_cat):
        for t, names in tiers["items"].items():
            if r_item in names:
                return int(t)
        return int(tiers["categories"].get(r_cat, tiers["default"]))
    ev["commodity_tier"] = [tier(i, c) for i, c in zip(ev["primary_drug"], cat)]
    dims = {}
    caps = R.get("caps") or {}
    _CAPS.update(caps)
    for d in ("method", "network", "route", "scale"):
        dims[d] = sum(f[k].astype(int) * v for k, v in P[d].items())
        if d in caps:
            dims[d] = dims[d].clip(upper=caps[d])
    dims["commodity"] = ev["commodity_tier"].map(lambda t: P["commodity"].get(t, 0))
    for d, v in dims.items():
        ev["risk_" + d] = v.astype(int)
    score = sum(dims.values())
    ev["risk_score"] = score.clip(upper=100).astype(int)
    # Weight (scale) and commodity type can never carry an event into a higher band on their own:
    # High needs at least two of the operational dimensions (method, network, route) to show something,
    # Medium needs at least one. Otherwise the event stays one band lower.
    n_op = sum((dims[d] > 0).astype(int) for d in ("method", "network", "route"))
    b = R["bands"]
    band = np.where(ev["risk_score"] >= b["high"], "High", np.where(ev["risk_score"] >= b["medium"], "Medium", "Low"))
    band = np.where((band == "High") & (n_op < R.get("min_dimensions_high", 2)), "Medium", band)
    band = np.where((band == "Medium") & (n_op < R.get("min_dimensions_medium", 1)), "Low", band)
    # Watchlist hit (vessel, container or term chosen by the user) overrides the score
    wl = R.get("watchlist") or {}
    wv = {str(x).strip().lower() for x in (wl.get("vessels") or []) if str(x).strip()}
    wc = {str(x).strip().upper().replace(" ", "") for x in (wl.get("containers") or []) if str(x).strip()}
    wt = [str(x).strip().lower() for x in (wl.get("terms") or []) if str(x).strip()]

    def _wl(r):
        if isinstance(r.vessel, str) and r.vessel.strip().lower() in wv:
            return True
        if wc and any(c.strip().upper().replace(" ", "") in wc for c in str(r.container_numbers or "").split(";") if c.strip()):
            return True
        hay = " ".join(str(x) for x in (r.title, getattr(r, "title_en", ""), r.cover_cargo) if isinstance(x, str)).lower()
        return bool(wt) and any(t_ in hay for t_ in wt)
    f["watchlist_hit"] = [_wl(r) for r in ev.itertuples()] if (wv or wc or wt) else False
    band = np.where(f["watchlist_hit"], "High", band)
    ev["risk_band"] = band
    ev["risk_flags"] = f.apply(lambda r: ", ".join(([] if not r.get("watchlist_hit") else ["Watchlist hit"]) +
                                                   [FLAG_LABELS[k] for k in FLAG_LABELS if r[k]]), axis=1)
    # data gaps: weak data is shown separately and never scored as risk (list s.10)
    def _gaps(r):
        g = []
        if not r.origin: g.append("origin")
        if not r.destination: g.append("destination")
        if not r.seizure_country: g.append("seizure country")
        if not r.conceal_list: g.append("concealment")
        if pd.isna(r.qty_kg) and pd.isna(r.qty_units): g.append("quantity")
        return ", ".join(g)
    ev["data_gaps"] = ev.apply(_gaps, axis=1)
    ev["risk_why"] = ev.apply(lambda r: " | ".join(
        f"{DIM_LABELS[d]} {int(r['risk_' + d])}/{DIM_MAX[d](P)}" for d in DIM_LABELS if r["risk_" + d] > 0) or "No risk indicators found", axis=1)
    for k in FLAG_LABELS:
        ev["f_" + k] = f[k]
    return ev


# ---------------------------------------------------------------- 2. patterns
def _trend(n_recent, n_prior, is_new):
    if is_new:
        return "NEW"
    if n_recent >= 3 and n_recent >= 2 * max(n_prior, 1):
        return "SURGING"
    if n_recent < n_prior:
        return "DECLINING"
    return "STABLE"


def corridor_table(ev, asof, cfg, history_ok):
    days = cfg["analysis"]["trend_window_days"]
    rs = asof - pd.Timedelta(days=days - 1)
    ps = rs - pd.Timedelta(days=days)
    e = ev[ev["corridor"].notna()]
    rows = []
    for c, g in e.groupby("corridor"):
        r, p = g[g["date"] >= rs], g[(g["date"] >= ps) & (g["date"] < rs)]
        is_new = history_ok and g["date"].min() >= rs and len(r) > 0
        rows.append({
            "corridor": c, "events_recent": len(r), "events_prior": len(p), "events_total": len(g),
            "kg_recent": round(float(r["qty_kg"].sum()), 1), "top_drug": g["primary_drug"].mode().iat[0],
            "container_share": round(float(g["in_container"].fillna(0).mean()), 2),
            "avg_risk": round(float(g["risk_score"].mean()), 1),
            "first_seen": g["date"].min().date().isoformat(), "last_seen": g["date"].max().date().isoformat(),
            "trend": _trend(len(r), len(p), is_new) if len(r) or len(p) else "INACTIVE",
        })
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    return df.sort_values(["events_recent", "avg_risk", "events_total"], ascending=False).reset_index(drop=True)


def concealment_matrix(ev, asof, days=90):
    e = ev[ev["date"] >= asof - pd.Timedelta(days=days - 1)].explode("conceal_list")
    e = e[e["conceal_list"].notna() & (e["conceal_list"] != "")]
    if e.empty:
        return pd.DataFrame()
    return e.groupby(["conceal_list", "primary_drug"]).size().unstack(fill_value=0)


def hotspot_table(ev, asof, cfg):
    days = cfg["analysis"]["trend_window_days"]
    rs = asof - pd.Timedelta(days=days - 1)
    ps = rs - pd.Timedelta(days=days)
    e = ev[ev["seizure_country"].notna()]
    rows = []
    for c, g in e.groupby("seizure_country"):
        r, p = g[g["date"] >= rs], g[(g["date"] >= ps) & (g["date"] < rs)]
        rows.append({"country": c, "events_total": len(g), "events_recent": len(r), "events_prior": len(p),
                     "high_risk": int((g["risk_band"] == "High").sum()),
                     "kg_total": round(float(g["qty_kg"].sum()), 1),
                     "container_share": round(float(g["in_container"].fillna(0).mean()), 2),
                     "top_drug": g["primary_drug"].mode().iat[0],
                     "top_place": (g["seizure_place"].dropna().mode().iat[0] if g["seizure_place"].notna().any() else "")})
    df = pd.DataFrame(rows)
    return df.sort_values(["events_recent", "events_total"], ascending=False).reset_index(drop=True) if len(df) else df


# ------------------------------------------------------------------ 3. alerts
def _urls(g, n=3):
    out = []
    for u in g["urls"]:
        out += u[:1]
    return out[:n]


def _spikes(ev, keys, asof, A, label):
    """Compare the last 7 days with the average of the 8 weeks before."""
    out = []
    rs = asof - pd.Timedelta(days=6)
    for key, g in ev.groupby(keys):
        rec = g[g["date"] >= rs]
        if len(rec) < A["spike_min_events"]:
            continue
        base = g[(g["date"] < rs) & (g["date"] >= rs - pd.Timedelta(days=56))]
        idx = ((rs - base["date"]).dt.days - 1) // 7
        weekly = np.bincount(idx.astype(int), minlength=8)[:8] if len(base) else np.zeros(8)
        mean, sd = weekly.mean(), weekly.std()
        z = (len(rec) - mean) / max(sd, 1.0)
        if z >= A["spike_z"]:
            key = key if isinstance(key, tuple) else (key,)
            out.append({"severity": "High" if z >= 3 or len(rec) >= 6 else "Medium", "type": "SPIKE",
                        "title": f"{label(key)}: {len(rec)} seizures in 7 days",
                        "detail": f"Usual level is about {mean:.1f} per week over the previous 8 weeks (z={z:.1f}).",
                        "urls": _urls(rec)})
    return out


def _txt(x):
    return x if isinstance(x, str) and x else None


def _new_combo(ev, field, asof, cfg, label_fn):
    """Flag a (drug, `field`) combination appearing for the first time in
    the recent trend window - a genuinely new modus operandi, as opposed
    to a corridor or a volume spike. `ev` must already be limited to rows
    where `field` is set."""
    A = cfg["analysis"]
    window_start = asof - pd.Timedelta(days=A["trend_window_days"] - 1)
    recent = ev[ev["date"] >= window_start]
    older = ev[ev["date"] < window_start]
    seen_before = set(zip(older["primary_drug"], older[field]))
    out = []
    for (drug, val), g in recent.groupby(["primary_drug", field]):
        if (drug, val) in seen_before:
            continue
        out.append({"severity": "Medium", "type": "NEW MO",
                    "title": label_fn(drug, val),
                    "detail": f"First seen {g['date'].min().date()}; {len(g)} report(s) since. "
                              f"Not previously recorded for {drug}.",
                    "urls": _urls(g)})
    return out


def build_alerts(ev, corridors, asof, cfg, history_ok):
    A = cfg["analysis"]
    alerts = []
    recent = ev[ev["date"] >= asof - pd.Timedelta(days=2)]
    for r in recent[recent["risk_band"] == "High"].sort_values("risk_score", ascending=False).head(10).itertuples():
        alerts.append({"severity": "High", "type": "HIGH-RISK EVENT",
                       "title": f"{r.primary_drug} - {_txt(r.seizure_place) or _txt(r.seizure_country) or 'location unclear'} "
                                f"(score {r.risk_score})",
                       "detail": r.mo_summary + (f" | Flags: {r.risk_flags}" if r.risk_flags else ""),
                       "urls": r.urls[:2]})
    week = ev[ev["date"] >= asof - pd.Timedelta(days=6)]
    for r in week[week["insider"].fillna(0) == 1].head(5).itertuples():
        alerts.append({"severity": "High", "type": "INSIDER SIGNAL",
                       "title": f"Possible insider involvement - {_txt(r.seizure_place) or _txt(r.seizure_country) or 'location unclear'}",
                       "detail": r.mo_summary, "urls": r.urls[:2]})
    if history_ok:
        for r in corridors.itertuples() if len(corridors) else []:
            g = ev[ev["corridor"] == r.corridor]
            g = g[g["date"] >= asof - pd.Timedelta(days=A["trend_window_days"] - 1)]
            if r.trend == "NEW":
                alerts.append({"severity": "Medium", "type": "NEW CORRIDOR",
                               "title": f"New corridor: {r.corridor}",
                               "detail": f"First seen {r.first_seen}; {r.events_recent} event(s) since. "
                                         f"Main drug: {r.top_drug}.", "urls": _urls(g)})
            elif r.trend == "SURGING":
                alerts.append({"severity": "Medium", "type": "SURGING CORRIDOR",
                               "title": f"Corridor surging: {r.corridor}",
                               "detail": f"{r.events_recent} events in the last {A['trend_window_days']} days vs "
                                         f"{r.events_prior} in the 30 days before.", "urls": _urls(g)})
        alerts += _spikes(ev[ev["seizure_country"].notna()], ["primary_drug", "seizure_country"], asof, A,
                          lambda k: f"{k[0]} seizures in {k[1]}")
        alerts += _spikes(ev[ev["origin"].notna()], ["primary_drug", "origin"], asof, A,
                          lambda k: f"{k[0]} shipments originating in {k[1]}")
        ex = ev.explode("conceal_list")
        ex = ex[ex["conceal_list"].notna() & (ex["conceal_list"] != "")]
        alerts += _spikes(ex, ["primary_drug", "conceal_list"], asof, A,
                          lambda k: f"{k[0]} concealed as/in: {k[1]}")

        alerts += _new_combo(ex, "conceal_list", asof, cfg,
                             lambda drug, val: f"New concealment method for {drug}: {val}")
        et = ev[ev["transport"].notna() & (ev["transport"] != "")]
        alerts += _new_combo(et, "transport", asof, cfg,
                             lambda drug, val: f"New transport mode for {drug}: {val}")
    order = {"High": 0, "Medium": 1, "Low": 2}
    seen, out = set(), []
    for a in sorted(alerts, key=lambda a: order[a["severity"]]):
        if a["title"] not in seen:
            seen.add(a["title"])
            out.append(a)
    return out


# ------------------------------------------------------------------- driver
def run(conn, cfg, asof=None):
    ev = load_events(conn)
    if ev.empty:
        return None
    asof = pd.Timestamp(asof).normalize() if asof is not None else ev["date"].max()
    ev = ev[ev["date"] <= asof]
    ev = score_events(ev, cfg, asof)
    history_days = int((ev["date"].max() - ev["date"].min()).days)
    history_ok = history_days >= cfg["analysis"]["min_history_days"]
    corr = corridor_table(ev, asof, cfg, history_ok)
    alerts = build_alerts(ev, corr, asof, cfg, history_ok)
    from . import links as _links
    try:
        repeat = _links.repeat_links(ev, asof, cfg)
        chain = _links.production_chain(ev, asof, cfg)
        extra = _links.link_alerts(repeat) + _links.chain_alerts(chain, asof)
    except Exception as exc:  # the link views are extras: never let them stop the daily run
        print(f"      link analysis skipped ({type(exc).__name__}: {exc})", flush=True)
        repeat, chain, extra = [], [], []
    have = {a["title"] for a in alerts}
    alerts = sorted(alerts + [a for a in extra if a["title"] not in have],
                    key=lambda a: {"High": 0, "Medium": 1, "Low": 2}[a["severity"]])
    w = asof - pd.Timedelta(days=6)
    pw = w - pd.Timedelta(days=7)
    cur, prev = ev[ev["date"] >= w], ev[(ev["date"] >= pw) & (ev["date"] < w)]
    kpis = {
        "events_7d": int(len(cur)), "events_prev_7d": int(len(prev)),
        "high_7d": int((cur["risk_band"] == "High").sum()),
        "container_share_7d": round(float(cur["in_container"].fillna(0).mean()) * 100, 1) if len(cur) else 0.0,
        "insider_7d": int((cur["insider"].fillna(0) == 1).sum()),
        "events_total": int(len(ev)),
    }
    return {"events": ev, "corridors": corr, "conceal": concealment_matrix(ev, asof),
            "hotspots": hotspot_table(ev, asof, cfg), "alerts": alerts, "kpis": kpis,
            "asof": asof, "history_days": history_days, "history_ok": history_ok,
            "links": repeat, "chain": chain}
