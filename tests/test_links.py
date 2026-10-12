# -*- coding: utf-8 -*-
import pandas as pd
from swatch import analyze, checklists, lexicon, links

ASOF = pd.Timestamp("2026-10-12")
CFG = {"links": {}}


def _ev(rows):
    base = {"event_id": 0, "date": ASOF, "primary_drug": "Cocaine", "category": "Drug", "vessel": None, "shipping_line": None,
            "container_numbers": None, "cover_cargo": None, "corridor": None, "origin_place": None, "seizure_country": "Spain",
            "seizure_place": None, "risk_band": "Low", "urls": ["http://x/1"], "qty_kg": None, "destination": None,
            "title": "", "title_en": "", "mo_summary": None, "drug_list": []}
    out = []
    for i, r in enumerate(rows):
        d = dict(base); d.update(r); d["event_id"] = i + 1; out.append(d)
    return pd.DataFrame(out)


def test_clean_lines_drops_agencies_and_words():
    assert links.clean_lines("PRF; Maersk; un; RCMP") == "Maersk"
    assert links.clean_lines("geçirildi") is None


def test_clean_vessel_drops_non_names():
    assert links.clean_vessel("Show") is None and links.clean_vessel("ZIMRA") is None
    assert links.clean_vessel("Mashaallah") == "Mashaallah"
    assert links.clean_vessel("CSPC PISCES") == "CSPC PISCES"


def test_same_vessel_in_two_events_is_a_strong_lead():
    ev = _ev([{"vessel": "Mashaallah"}, {"vessel": "Mashaallah", "date": ASOF - pd.Timedelta(days=3)}, {"vessel": "Other One"}])
    out = links.repeat_links(ev, ASOF, CFG)
    assert [r["name"] for r in out] == ["Mashaallah"] and out[0]["strength"] == "High" and out[0]["n"] == 2
    assert links.link_alerts(out)[0]["severity"] == "High"


def test_big_carrier_is_table_only_and_old_links_drop_out():
    ev = _ev([{"shipping_line": "Maersk"}] * 5)
    out = links.repeat_links(ev, ASOF, CFG)
    assert out and out[0]["strength"] == "Low" and not links.link_alerts(out)
    old = _ev([{"vessel": "Old Boat", "date": ASOF - pd.Timedelta(days=90)}] * 2)
    assert links.repeat_links(old, ASOF, CFG) == []


def test_containers_always_found_together_are_merged_as_one_case():
    ev = _ev([{"container_numbers": "AAAU1111111; BBBU2222222"}, {"container_numbers": "AAAU1111111; BBBU2222222"}])
    out = links.repeat_links(ev, ASOF, CFG)
    assert len(out) == 1 and out[0]["strength"] == "Low" and "one case" in out[0]["note"]


def test_production_chain_needs_same_place_or_a_precursor():
    ev = _ev([
        {"title": "Clandestine laboratory dismantled", "primary_drug": "Methamphetamine", "seizure_place": "Sinaloa", "seizure_country": "Mexico",
         "date": ASOF - pd.Timedelta(days=10), "drug_list": ["Methamphetamine"]},
        {"primary_drug": "Methamphetamine", "seizure_place": "Sinaloa", "seizure_country": "Mexico", "drug_list": ["Methamphetamine"]},
        {"primary_drug": "Methamphetamine", "seizure_place": "Other", "seizure_country": "Chile", "drug_list": ["Methamphetamine"]},
    ])
    ch = links.production_chain(ev, ASOF, CFG)
    mex = [r for r in ch["countries"] if r["country"] == "Mexico"][0]
    assert ch["n_lab"] == 1 and mex["linked"] and mex["n_local"] == 1
    assert links.chain_alerts(ch, ASOF)[0]["type"] == "PRODUCTION CHAIN"


def test_checklist_keys_match_real_indicator_names():
    assert set(checklists.FLAGS) <= set(analyze.FLAG_LABELS.values())
    assert set(checklists.CONCEAL) <= set(lexicon.CONCEALMENT)
    assert all(v for d in (checklists.FLAGS, checklists.CONCEAL, checklists.CATEGORY, checklists.TRANSPORT) for v in d.values())
