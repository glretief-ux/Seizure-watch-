# -*- coding: utf-8 -*-
"""Second-pass merge: news about the same seizure often lands in several events (different outlets name different
countries, or only some give the quantity). Here events are joined into one CASE when they clearly describe the same
seizure, so the dashboard counts it once and lists every news article underneath.
Rules are deliberately conservative: same item, within 3 days, quantities not in conflict, and at least one hard link."""
import re
from .db import _tokens, _jaccard


def _ends(corridor):
    """The set of country names in a 'A -> B' corridor."""
    return {p.strip().lower() for p in re.split(r"->|→|>", corridor or "") if p.strip()}


def _amount(a, b):
    """True/False when both quantities are known; None when we cannot tell."""
    for k in ("qty_kg", "qty_units"):
        x, y = a.get(k), b.get(k)
        if x and y:
            return abs(x - y) / max(x, y) <= 0.08
    return None


def _countries(e):
    s = _ends(e.get("corridor"))
    for k in ("seizure_country", "seizure_place", "origin", "destination"):
        if e.get(k):
            s.add(str(e[k]).strip().lower())
    return s


def _sim(a, b):
    return _jaccard(a["_tok"], b["_tok"])


def _same_case(a, b):
    if a["primary_drug"] != b["primary_drug"]:
        return False
    if abs((a["published"] - b["published"]).days) > 3:
        return False
    amt = _amount(a, b)
    if amt is False:
        return False
    ca, cb = _ends(a.get("corridor")), _ends(b.get("corridor"))
    # a shared vessel or container number is the strongest link
    for k in ("vessel", "container_numbers"):
        if a.get(k) and b.get(k) and set(map(str.strip, re.split(r"[;,]", str(a[k])))) & set(map(str.strip, re.split(r"[;,]", str(b[k])))):
            return True
    sa, sb = str(a.get("seizure_country") or "").strip().lower(), str(b.get("seizure_country") or "").strip().lower()
    # same full route (both ends named): same amount, or no amount to compare but seized in the same country
    sim = _sim(a, b)
    if len(ca) >= 2 and ca == cb and (amt is True or (sa and sa == sb and sim >= 0.2)):
        return True
    # same quantity and the countries overlap
    if amt is True and _countries(a) & _countries(b):
        return True
    # no amount in one of them, but the same named place of seizure within 2 days
    pa, pb = str(a.get("seizure_place") or "").strip().lower(), str(b.get("seizure_place") or "").strip().lower()
    if amt is None and sa and sa == sb and pa and pa == pb and abs((a["published"] - b["published"]).days) <= 2 and sim >= 0.1:
        return True
    # one report names the route, the other only the place of seizure, and that place is one end of the route
    for x, y, cx in ((a, b, ca), (b, a, cb)):
        if len(cx) >= 2 and not y.get("corridor") and sa and sa == sb and amt is not False and sim >= 0.25:
            return True
    return False


def merge_cases(df):
    """df: one row per article with event_id. Returns df with event_id replaced by the case id (smallest event_id)."""
    if df.empty:
        return df
    cols = [c for c in ("primary_drug", "published", "qty_kg", "qty_units", "corridor", "seizure_country", "seizure_place", "origin",
                        "destination", "vessel", "container_numbers", "completeness", "title", "title_en") if c in df.columns]
    best = df.sort_values(["event_id", "completeness"], ascending=[True, False]).groupby("event_id", sort=False).head(1)
    recs = [{k: (None if (not isinstance(v, str) and v != v) else v) for k, v in r.items()}      # NaN -> None
            for r in best[["event_id"] + cols].to_dict("records")]
    for r in recs:                                   # tokenise each headline once (slow otherwise)
        r["_tok"] = _tokens(r.get("title") or "") | _tokens(r.get("title_en") or "")
    by_drug = {}
    for r in recs:
        by_drug.setdefault(r["primary_drug"], []).append(r)
    root = {}
    for rs in by_drug.values():
        rs.sort(key=lambda r: r["published"])
        cases = []                                   # each case: [first_date, [member records]]
        for r in rs:
            home = None
            for c in reversed(cases):
                if (r["published"] - c[0]).days > 3:  # a case spans at most 3 days from its first report
                    break
                if _same_case(c[1][0], r):          # compared with the case's first report only, so cases cannot drift
                    home = c
                    break
            if home is None:
                cases.append([r["published"], [r]])
                root[r["event_id"]] = r["event_id"]
            else:
                home[1].append(r)
                root[r["event_id"]] = root[home[1][0]["event_id"]]
    find = lambda x: root[x]
    out = df.copy()
    out["event_id"] = out["event_id"].map(find)
    return out
