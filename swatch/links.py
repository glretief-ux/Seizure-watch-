# -*- coding: utf-8 -*-
"""Leads that connect separate seizure reports.

Two analyses, both working on the one-row-per-event table that analyze.py builds:

  1. REPEAT LINKS - the same vessel, shipping line, container number, origin port, or the same
     cover cargo on the same corridor turning up in more than one separate seizure.
  2. PRODUCTION CHAIN - precursor chemical seizures and clandestine-laboratory reports followed
     by synthetic-drug seizures in the same country (a possible link, never proof).

Everything here is a lead for an analyst to check, built from news text that can be wrong. Names are
cleaned first, because automatic entity recognition also picks up police forces, agencies and
ordinary words, and linking on those would create false leads.
"""
import re
import pandas as pd

from . import extract

KNOWN_LINES = set(extract.SHIPPING_LINES)

# Words that look like a name to the extractor but are not a vessel.
_NOT_VESSELS = {"show", "shed", "system", "matthew", "spanish", "usa", "uk", "us", "eu", "customs", "police", "navy",
                "coast", "guard", "ship", "vessel", "boat", "cargo", "container", "port", "sea", "ocean", "bulk"}
_LATIN_WORD = re.compile(r"[A-Za-z][A-Za-z \-/&']{2,38}")
# Cover goods too common to say anything on their own (they are matched together with the corridor).
_GENERIC_GOODS = {"goods", "cargo", "food", "products", "items", "merchandise", "luggage", "parcels", "packages"}
SYNTHETIC = {"Methamphetamine", "NSA"}
LAB_RX = re.compile(r"laborator|laboratoire|лаборатор|مختبر|معمل|实验室|實驗室|\blab\b|\blabs\b|narcolab|cocina\s+clandestina|"
                    r"clandestine\s+(?:drug\s+)?(?:lab|factory|kitchen)|drug\s+factory|synthetic\s+drug\s+(?:plant|factory)", re.I)


def split_list(v):
    return [x.strip() for x in str(v).split(";") if x.strip()] if isinstance(v, str) else []


def clean_lines(v):
    """Keep only recognised shipping lines (drops police forces, agencies and stray words)."""
    keep = [x for x in split_list(v) if x in KNOWN_LINES]
    return "; ".join(dict.fromkeys(keep)) or None


def clean_vessel(v):
    if not isinstance(v, str):
        return None
    name = v.strip(" .,'\"")
    if len(name) < 3 or len(name) > 30:
        return None
    toks = name.split()
    if toks[0].lower() in _NOT_VESSELS or name.lower() in _NOT_VESSELS:
        return None
    if len(toks) == 1 and name.isupper() and len(name) <= 6:      # ZIMRA, RCMP, ... are agencies
        return None
    return name


def _is_synthetic(row):
    return row.get("primary_drug") in SYNTHETIC or any(d in SYNTHETIC for d in row.get("drug_list", []) or [])


def _entity_rows(ev):
    """One (type, name, event_id) row per entity mention."""
    rows = []
    for r in ev.itertuples():
        v = clean_vessel(r.vessel)
        if v:
            rows.append(("Vessel", v, r.event_id))
        for x in split_list(r.shipping_line):
            if x in KNOWN_LINES:
                rows.append(("Shipping line", x, r.event_id))
        for x in split_list(r.container_numbers):
            rows.append(("Container number", x, r.event_id))
        if isinstance(r.origin_place, str) and r.origin_place and isinstance(r.primary_drug, str):
            rows.append(("Loading place", r.origin_place, r.event_id))
        if isinstance(r.corridor, str) and r.corridor:
            for g in split_list(r.cover_cargo):
                g = g.lower()
                if _LATIN_WORD.fullmatch(g) and g not in _GENERIC_GOODS:
                    rows.append(("Cover cargo on corridor", f"{g} | {r.corridor}", r.event_id))
    return rows


# how much weight a repeat deserves: an individual vessel or box recurring is a strong lead, a big carrier is not
STRENGTH = {"Vessel": "High", "Container number": "High", "Cover cargo on corridor": "Medium", "Loading place": "Low", "Shipping line": "Low"}


def repeat_links(ev, asof, cfg):
    L = (cfg.get("links") or {})
    mins = {"Vessel": 2, "Container number": 2, "Shipping line": 4, "Loading place": 4, "Cover cargo on corridor": 3}
    mins.update(L.get("min_events") or {})
    recent_days = int(L.get("recent_days", 30))
    if ev is None or not len(ev):
        return []
    rows = pd.DataFrame(_entity_rows(ev), columns=["type", "name", "event_id"]).drop_duplicates()
    if rows.empty:
        return []
    idx = ev.set_index("event_id")
    cut = asof - pd.Timedelta(days=recent_days - 1)
    out = []
    for (t, name), g in rows.groupby(["type", "name"]):
        if len(g) < mins.get(t, 2):
            continue
        sub = idx.loc[g["event_id"].tolist()]
        recent = int((sub["date"] >= cut).sum())
        if recent == 0:
            continue                      # only leads that are still live
        urls = []
        for u in sub.sort_values("date", ascending=False)["urls"]:
            if len(u):
                urls.append(u[0])
        out.append({"type": t, "name": name, "n": int(len(g)), "recent": recent,
                    "first": sub["date"].min().strftime("%Y-%m-%d"), "last": sub["date"].max().strftime("%Y-%m-%d"),
                    "countries": sorted({c for c in sub["seizure_country"].dropna()})[:5],
                    "items": sorted({c for c in sub["primary_drug"].dropna()})[:4],
                    "band": "High" if (sub["risk_band"] == "High").any() else ("Medium" if (sub["risk_band"] == "Medium").any() else "Low"),
                    "strength": STRENGTH.get(t, "Low"), "ids": [int(i) for i in g["event_id"]][:25], "urls": urls[:3]})
    out = _merge_same_case(out)
    order = {"High": 0, "Medium": 1, "Low": 2}
    out.sort(key=lambda r: (order[r["strength"]], -r["recent"], -r["n"]))
    return out


def _merge_same_case(out):
    """Several containers that all turn up in the very same reports are one case reported more than once
    (the reports were not merged into one event), not several separate links."""
    groups, rest = {}, []
    for r in out:
        if r["type"] == "Container number":
            groups.setdefault(tuple(sorted(r["ids"])), []).append(r)
        else:
            rest.append(r)
    for ids, rs in groups.items():
        if len(rs) == 1:
            rest.append(rs[0])
            continue
        r = dict(rs[0])
        r["name"] = f"{len(rs)} containers ({', '.join(x['name'] for x in rs[:3])}{', ...' if len(rs) > 3 else ''})"
        r["note"] = "The same containers appear together in each of these reports: probably one case reported more than once."
        r["strength"] = "Low"
        rest.append(r)
    return rest


def link_alerts(links):
    """Alerts for the strong and medium leads only (carriers are too big a net to alert on)."""
    alerts = []
    for r in links:
        if r["strength"] != "High":       # only an individual vessel or container is specific enough to alert on
            continue
        where = f" in {', '.join(r['countries'])}" if r["countries"] else ""
        alerts.append({"severity": "High" if r["strength"] == "High" else "Medium", "type": "RECURRING LINK",
                       "title": f"{r['type']} linked to {r['n']} separate seizures: {r['name']}",
                       "detail": f"First seen {r['first']}, most recent {r['last']}{where}. Items: {', '.join(r['items']) or 'n/a'}. "
                                 "A lead to check, not proof of a link.",
                       "urls": r["urls"]})
    return alerts


# ------------------------------------------------------------------ production chain
def is_lab(row):
    txt = " ".join(str(row.get(k) or "") for k in ("title", "title_en", "mo_summary"))
    return bool(LAB_RX.search(txt))


def production_chain(ev, asof, cfg):
    """Precursor seizures and clandestine labs, followed by synthetic-drug seizures in the same country."""
    L = (cfg.get("links") or {})
    back = int(L.get("chain_days", 90))        # how far back to look for precursors and labs
    gap = int(L.get("chain_gap_days", 60))     # how close the synthetic-drug seizure has to be
    empty = {"countries": [], "n_precursor": 0, "n_lab": 0, "days": back}
    if ev is None or not len(ev):
        return empty
    cat = ev["category"].fillna("Drug") if "category" in ev else pd.Series("Drug", index=ev.index)
    start = asof - pd.Timedelta(days=back - 1)
    win = ev[ev["date"] >= start].copy()
    win["_cat"] = cat.loc[win.index]
    win["_lab"] = win.apply(lambda r: is_lab(r), axis=1)
    pre = win[win["_cat"] == "Precursor chemical"]
    lab = win[win["_lab"] & (win["_cat"] != "Precursor chemical")]
    empty["n_precursor"], empty["n_lab"] = int(len(pre)), int(len(lab))
    synth = win[win.apply(_is_synthetic, axis=1) & ~win["_lab"] & (win["_cat"] == "Drug")]

    def country(r, prefer_dest):
        for k in (("destination", "seizure_country") if prefer_dest else ("seizure_country",)):
            v = r.get(k)
            if isinstance(v, str) and v:
                return v
        return None

    rows = {}
    for kind, df in (("precursor", pre), ("lab", lab)):
        for _, r in df.iterrows():
            c = country(r, kind == "precursor")
            if not c:
                continue
            d = rows.setdefault(c, {"country": c, "precursor": [], "lab": []})
            d[kind].append(r)
    out = []
    for c, d in rows.items():
        anchors = d["precursor"] + d["lab"]
        first_anchor = min(a["date"] for a in anchors)
        places = {a["seizure_place"] for a in anchors if isinstance(a.get("seizure_place"), str) and a["seizure_place"]}
        s = synth[(synth["seizure_country"] == c) & (synth["date"] >= first_anchor - pd.Timedelta(days=gap)) &
                  (synth["date"] <= asof)]
        # synthetic seizures close in time to any precursor or lab report
        def near(row):
            return any(abs((row["date"] - a["date"]).days) <= gap for a in anchors)
        s = s[s.apply(near, axis=1)] if len(s) else s
        urls = []
        for a in sorted(anchors, key=lambda x: x["date"], reverse=True):
            if len(a["urls"]):
                urls.append(a["urls"][0])
        for _, x in s.sort_values("date", ascending=False).iterrows():
            if len(x["urls"]):
                urls.append(x["urls"][0])
        local = s[s["seizure_place"].isin(places)] if (len(s) and places) else s.iloc[0:0]
        kg_pre = sum(float(a["qty_kg"]) for a in d["precursor"] if pd.notna(a["qty_kg"]))
        out.append({"country": c, "n_precursor": len(d["precursor"]), "n_lab": len(d["lab"]), "n_synth": int(len(s)), "n_local": int(len(local)),
                    "precursors": sorted({a["primary_drug"] for a in d["precursor"]})[:4], "kg_precursor": round(kg_pre, 1),
                    "last_anchor": max(a["date"] for a in anchors).strftime("%Y-%m-%d"),
                    "last_synth": s["date"].max().strftime("%Y-%m-%d") if len(s) else None,
                    "linked": bool(len(local)) or (len(d["precursor"]) > 0 and len(s) > 0), "urls": list(dict.fromkeys(urls))[:4]})
    out.sort(key=lambda r: (-int(r["linked"]), -(r["n_precursor"] * 2 + r["n_lab"]), -r["n_synth"]))
    empty["countries"] = out
    return empty


def chain_alerts(chain, asof, limit=5):
    alerts = []
    for r in chain["countries"]:
        if len(alerts) >= limit:
            break                              # the table lists the rest; do not flood the alert box
        if not r["linked"]:
            continue
        recent = (asof - pd.Timestamp(r["last_anchor"])).days <= 30
        if not recent:
            continue
        what = []
        if r["n_precursor"]:
            what.append(f"{r['n_precursor']} precursor seizure(s)" + (f" ({', '.join(r['precursors'])})" if r["precursors"] else ""))
        if r["n_lab"]:
            what.append(f"{r['n_lab']} clandestine-lab report(s)")
        alerts.append({"severity": "Medium", "type": "PRODUCTION CHAIN",
                       "title": f"{r['country']}: {' and '.join(what)} close in time to synthetic-drug seizures"
                                + (f" in the same place ({r['n_local']})" if r["n_local"] else f" ({r['n_synth']})"),
                       "detail": f"Latest precursor/lab report {r['last_anchor']}, latest synthetic-drug seizure {r['last_synth']}. "
                                 "A possible link based on place and timing only, not proof.",
                       "urls": r["urls"]})
    return alerts
