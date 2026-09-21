# -*- coding: utf-8 -*-
import sys, os, tempfile, datetime as dt
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import yaml
from swatch.extract import extract, _containers, _iso6346_ok, _LET
from swatch import lexicon as L, db, coverage, geo

CASES = [
    ("ضبط 2.5 طن من الكوكايين في ميناء جدة قادمة من كولومبيا", "Cocaine", 2500, "Saudi Arabia", "Colombia"),
    ("İstanbul Havalimanı'nda 45 kilo kokain ele geçirildi", "Cocaine", 45, "Turkey", None),
    ("Ekvador'dan gelen konteynerde 500 kilo kokain Mersin Limanı'nda ele geçirildi", "Cocaine", 500, "Turkey", "Ecuador"),
    ("В порту Гамбурга изъяли 1,5 тонны кокаина из Эквадора", "Cocaine", 1500, "Germany", "Ecuador"),
    ("海关在深圳港查获3.2吨可卡因，来自厄瓜多尔", "Cocaine", 3200, "China", "Ecuador"),
    ("香港海關檢獲約15公斤懷疑大麻花，拘捕一名男子", "Cannabis", 15, "Hong Kong", None),
    ("मुंबई एयरपोर्ट पर 5 किलो कोकीन जब्त, दो गिरफ्तार", "Cocaine", 5, "India", None),
    ("पाकिस्तान से आई 2 किलो हेरोइन पंजाब में बरामद", "Heroin/Opium", 2, None, "Pakistan"),
]


def test_new_languages_are_read():
    for title, drug, kg, country, origin in CASES:
        r = extract(title, "")
        assert r["relevant"] == 1, title
        assert r["primary_drug"] == drug, (title, r["primary_drug"])
        assert r["qty_kg"] == kg, (title, r["qty_kg"])
        if country:
            assert r["seizure_country"] == country, (title, r["seizure_country"])
        if origin:
            assert r["origin"] == origin, (title, r["origin"])


def test_air_and_port_words_are_not_mixed_up():
    assert extract("İstanbul Havalimanı'nda 45 kilo kokain ele geçirildi", "")["transport"] == "Air"
    assert extract("В аэропорту Шереметьево задержали курьера с 3 кг кокаина", "")["transport"] == "Air"
    assert extract("深圳港查获3.2吨可卡因", "")["transport"].startswith("Sea")


def test_unrelated_text_in_new_languages_is_ignored():
    assert extract("國際米蘭贏得歐洲聯賽", "")["relevant"] == 0
    assert extract("Ceza mahkemesi kokain davasında karar verdi", "")["relevant"] == 0


def test_words_that_only_look_like_countries():
    for txt in ["индивидуальный подход к кокаину изъяли 3 кг", "cinayet soruşturmasında 3 kilo kokain ele geçirildi"]:
        r = extract(txt, "")
        assert r.get("seizure_country") is None and r.get("origin") is None, txt


def test_headlines_in_other_scripts_do_not_collapse_into_one():
    keys = {db.title_key(t) for t, *_ in CASES}
    assert len(keys) == len(CASES) and "" not in keys


def _valid(prefix, six):
    chars = prefix + six
    return str(sum((_LET[c] if c.isalpha() else int(c)) * 2 ** i for i, c in enumerate(chars)) % 11 % 10)


def test_vessel_line_container_and_cover_cargo():
    num = "MSKU" + "123456" + _valid("MSKU", "123456")
    text = (f"Officers at the Port of Antwerp seized 1.2 tonnes of cocaine hidden among bananas in container {num[:4]} {num[4:10]} {num[10]}. "
            "The container arrived on the MV Maersk Kensington from Guayaquil. The goods were declared as fresh fruit pulp.")
    r = extract("Cocaine found in banana shipment at Antwerp", text)
    assert r["vessel"] == "Maersk Kensington", r["vessel"]
    assert r["shipping_line"] == "Maersk"
    assert r["container_numbers"] == num
    assert "fresh fruit pulp" in r["cover_cargo"] and "banana" in r["cover_cargo"]
    assert r["origin_place"] == "Guayaquil" and r["seizure_place"] == "Antwerp"


def test_wrong_container_number_is_ignored():
    good = "MSKU" + "123456" + _valid("MSKU", "123456")
    bad = good[:-1] + str((int(good[-1]) + 1) % 10)
    assert _containers(good) == [good] and _containers(bad) == []


def test_no_made_up_vessels_or_cargo():
    r = extract("Police seize cocaine", "Officers seized 3 kg of cocaine. The vessel was seized. A ship carrying timber was searched.")
    assert r["vessel"] is None and r["cover_cargo"] is None


def test_spanish_vessel_and_cargo():
    r = extract("Policia halla cocaina en buque Ocean Star en puerto de Manta",
                "Se incautaron 500 kg de cocaina ocultos entre carga de madera declarada como muebles en el buque Ocean Star.")
    assert r["vessel"] == "Ocean Star" and "madera" in r["cover_cargo"]


def test_coverage_and_map_data_are_complete():
    cfg = yaml.safe_load(open(os.path.join(os.path.dirname(__file__), "..", "config.yaml"), encoding="utf-8"))
    cov = coverage.payload(cfg)
    assert {"ar", "tr", "ru", "zh", "hi"} <= set(cov["searched"])
    assert set(cov["countries"]) == set(geo.COUNTRY)
    g = geo.payload(L.PLACE_ALIAS)
    assert set(L.COUNTRY_ALIAS.values()) <= set(g["c"])
    assert {d for d, c in L.PLACE_ALIAS.values()} == set(g["p"])


def test_bulletin_builds_and_sends_only_when_set_up():
    import subprocess, shutil
    from swatch import bulletin
    assert bulletin.is_due(None, dt.date(2026, 9, 21), 0) is True          # a Monday
    assert bulletin.is_due(None, dt.date(2026, 9, 22), 0) is False
    assert bulletin.is_due("2026-09-14", dt.date(2026, 9, 21), 0) is True
    assert bulletin.is_due("2026-09-18", dt.date(2026, 9, 21), 0) is False
    here = os.path.join(os.path.dirname(__file__), "..")
    out = tempfile.mkdtemp()
    subprocess.run([sys.executable, os.path.join(here, "run_daily.py"), "--demo", "--out", out], check=True, capture_output=True)
    assert os.path.exists(os.path.join(out, "bulletin.html")) and os.path.exists(os.path.join(out, "bulletin.txt"))
    txt = open(os.path.join(out, "bulletin.txt"), encoding="utf-8").read()
    assert "UNUSUAL EVENTS" in txt and "NEW AND SURGING CORRIDORS" in txt
    ok, msg = bulletin.send_email({"content": {"period": "x"}, "text": "t", "html": "<p>t</p>"}, env={})
    assert ok is False and "not set up" in msg
    demo_db = os.path.join(here, "data", "demo.db")
    if os.path.exists(demo_db):
        os.remove(demo_db)


if __name__ == "__main__":
    bad = 0
    for k, v in list(globals().items()):
        if k.startswith("test_"):
            try:
                v(); print("ok  ", k)
            except AssertionError:
                import traceback; bad += 1; print("FAIL", k); traceback.print_exc()
    sys.exit(1 if bad else 0)
