# -*- coding: utf-8 -*-
"""German (Austria), Danish, Estonian, Amharic, Icelandic, Mongolian, Norwegian, Slovak and Swedish."""
import os
import sys

import pytest
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from swatch import collect, coverage, cover, geo, translate           # noqa: E402
from swatch import lexicon as L                                       # noqa: E402
from swatch.extract import extract                                    # noqa: E402

# (headline, drug, kg, seizure country)
SEIZURES = [
    ("Zoll stellt 150 Kilogramm Kokain im Hamburger Hafen sicher", "Cocaine", 150, "Germany"),
    ("Polizei beschlagnahmt 20 Kilo Cannabis in Wien", "Cannabis", 20, "Austria"),
    ("Drogenfund: 3 Kilo Heroin im Auto bei Salzburg entdeckt", "Heroin/Opium", 3, "Austria"),
    ("Zoll findet 2 Tonnen Kokain in Bananenkisten im Hafen von Hamburg", "Cocaine", 2000, "Germany"),
    ("Wiener Polizei hebt Drogenlabor aus: Chemikalien und 3 Kilo Crystal Meth beschlagnahmt", "Methamphetamine", 3, "Austria"),
    ("Politiet beslaglagde 50 kilo kokain i Københavns Havn", "Cocaine", 50, "Denmark"),
    ("Told beslaglagde 200 kilo hash fra Marokko i Esbjerg", "Cannabis", 200, "Denmark"),
    ("Tollvesenet tok i beslag 30 kilo kokain i Oslo havn", "Cocaine", 30, "Norway"),
    ("Politiet tok i beslag 2,5 kilo heroin på Gardermoen", "Heroin/Opium", 2.5, "Norway"),
    ("Tullen beslagtog 100 kilo kokain i Göteborgs hamn", "Cocaine", 100, "Sweden"),
    ("Polisen tog beslag på 15 kilo hasch i Malmö", "Cannabis", 15, "Sweden"),
    ("Tullverket beslagtog 1,2 ton kokain i Göteborgs hamn – på väg till Norge", "Cocaine", 1200, "Sweden"),
    ("Politsei konfiskeeris Tallinnas 5 kilogrammi kokaiini", "Cocaine", 5, "Estonia"),
    ("Muuga sadamas avastati 200 kilo kokaiini Ecuadorist saabunud konteineris", "Cocaine", 200, "Estonia"),
    ("Policajti zaistili v Bratislave 2 kilogramy kokaínu", "Cocaine", 2, "Slovakia"),
    ("Colníci zadržali pri Čiernej nad Tisou 500 kilogramov cigariet", "Cigarettes", 500, "Slovakia"),
    ("Pri Košiciach zaistili 10 kilogramov heroínu", "Heroin/Opium", 10, "Slovakia"),
    ("Lögreglan lagði hald á 3 kíló af kókaíni í Keflavík", "Cocaine", 3, "Iceland"),
    ("Lögreglan á Suðurnesjum handtók mann með kókaín á Keflavíkurflugvelli", "Cocaine", None, "Iceland"),
    ("Улаанбаатарт 2 кг кокаин хураан авлаа", "Cocaine", 2, "Mongolia"),
    ("Гаалийн байгууллага Замын-Үүдэд 15 кг мансууруулах бодис илрүүллээ", None, 15, "Mongolia"),
    ("በቦሌ አየር ማረፊያ 5 ኪሎ ግራም ኮኬይን ተያዘ", "Cocaine", 5, "Ethiopia"),
    ("ጉምሩክ በሞያሌ 10 ኪሎ ሄሮይን ያዘ", "Heroin/Opium", 10, "Ethiopia"),
]


@pytest.mark.parametrize("headline,drug,kg,country", SEIZURES)
def test_seizure_headlines_are_read(headline, drug, kg, country):
    r = extract(headline, "")
    assert r["relevant"] == 1, headline
    if drug:
        assert r["primary_drug"] == drug, (headline, r["primary_drug"])
    if kg is not None:
        assert abs(r["qty_kg"] - kg) < 0.01, (headline, r["qty_kg"])
    assert r["seizure_country"] == country, (headline, r["seizure_country"])


def test_german_separable_verb_and_arrest_with_drugs():
    r = extract("Zollfahnder fangen Container mit 400 Kilo Kokain aus Ecuador ab", "")
    assert r["relevant"] == 1 and r["origin"] == "Ecuador" and abs(r["qty_kg"] - 400) < 0.01
    assert extract("Mann mit 3 Kilo Kokain erwischt", "")["relevant"] == 1


def test_routes_in_the_new_languages():
    r = extract("Zoll findet 2 Tonnen Kokain in Bananenkisten im Hafen von Hamburg – Ware aus Ecuador, bestimmt für Rotterdam", "")
    assert r["origin"] == "Ecuador" and r["destination"] == "Netherlands"
    r = extract("Tullverket beslagtog 1,2 ton kokain i Göteborgs hamn – på väg till Norge", "")
    assert r["destination"] == "Norway"
    r = extract("Tolden beslaglagde 2 ton kokain i havnen i Aarhus – skjult i bananer fra Colombia", "")
    assert r["origin"] == "Colombia" and r["concealment"] == "Legitimate cargo (food/produce)"
    # Estonian case endings carry the direction: -st = from, -sse = to
    r = extract("Tollid konfiskeeris Tallinna sadamas 300 kilogrammi kokaiini, mis saabus Brasiiliast ja oli mõeldud Soomesse", "")
    assert r["origin"] == "Brazil" and r["destination"] == "Finland"
    r = extract("Colníci zaistili na letisku v Bratislave 4 kilogramy kokaínu zo Španielska", "")
    assert r["origin"] == "Spain" and r["transport"] == "Air"
    r = extract("Tollgæslan lagði hald á 15 kíló af amfetamíni í Keflavík – efnin komu frá Hollandi", "")
    assert r["origin"] == "Netherlands"
    r = extract("Монголын гаалийн байгууллага Хятадаас оруулж ирсэн 30 кг мансууруулах бодис илрүүллээ", "")
    assert r["origin"] == "China" and r["seizure_country"] == "Mongolia"
    r = extract("በቦሌ አየር ማረፊያ ከዱባይ የመጣ 3 ኪሎ ኮኬይን ተያዘ", "")
    assert r["origin"] == "United Arab Emirates" and r["transport"] == "Air"


def test_units_and_number_formats():
    assert abs(extract("Politiet tok i beslag 2,5 kilo heroin", "")["qty_kg"] - 2.5) < 1e-6          # decimal comma
    r = extract("Zoll beschlagnahmt 200.000 Zigaretten am Flughafen Wien-Schwechat", "")
    assert r["primary_drug"] == "Cigarettes" and r["qty_units"] == 200000 and r["qty_kg"] is None  # German thousands dot
    r = extract("Pri Vyšnom Nemeckom zaistili 20 000 kusov cigariet, pašované z Ukrajiny", "")
    assert r["qty_units"] == 20000 and r["origin"] == "Ukraine"
    # a running total is not one seizure
    r = extract("Seit Jahresbeginn wurden 500 Kilo Kokain beschlagnahmt", "")
    assert r["qty_kg"] is None


def test_ivory_and_cites_words():
    r = extract("Elfenbein im Wert von 50.000 Euro in Salzburg sichergestellt", "")
    assert r["category"] == "CITES elephant ivory" and r["seizure_country"] == "Austria"
    r = extract("Toll beslaglagde 30 kg elfenben i København", "")
    assert r["category"] == "CITES elephant ivory"
    r = extract("Tolden beslagla 12 elefantbein-gjenstander", "")
    assert r["relevant"] in (0, 1)                                       # must not crash on unknown words


def test_ivory_coast_is_a_country_in_every_language():
    for t in ("3 kilo kokain beslaglagt i Elfenbenskysten", "3 Kilo Kokain in Elfenbeinküste sichergestellt",
              "Tullen beslagtog 3 kilo kokain från Elfenbenskusten", "Zaistili 3 kilogramy kokaínu v Pobrežie Slonoviny"):
        r = extract(t, "")
        assert r.get("category") != "CITES elephant ivory", t
    assert extract("Elfenbeinküste gewinnt Afrika-Cup", "")["relevant"] == 0


def test_arms_precursors_and_stolen_vehicles():
    r = extract("Zoll beschlagnahmt 12 Pistolen und Munition bei Kontrolle in Passau", "")
    assert r["category"] == "Arms and ammunition" and r["seizure_country"] == "Germany"
    r = extract("Politiet beslaglagde 40 liter ephedrin og kemikalier i narkolaboratorium", "")
    assert r["relevant"] == 1
    r = extract("Tullen beslagtog stulna bilar i Trelleborgs hamn", "")
    assert r["category"] == "Stolen vehicle" and r["seizure_country"] == "Sweden"


@pytest.mark.parametrize("headline", [
    "Rapid Wien gewinnt das Derby gegen Salzburg", "Regeringen presenterar ny budget för 2027", "Novo Nordisk hæver forventningerne til året",
    "Det blir sol og varme i helgen", "Eesti jalgpallikoondis alistas Läti", "Slovan Bratislava vyhral derby",
    "Gos í Fagradalsfjalli heldur áfram", "Mongolian wrestler wins gold", "Der Hass im Netz nimmt zu, Polizei ermittelt",
    "Polizei beschlagnahmt Waffen von Neonazis in Linz", "Hamburger SV verliert gegen Kiel",
])
def test_unrelated_headlines_are_not_drug_seizures(headline):
    r = extract(headline, "")
    assert r["relevant"] == 0 or r.get("category") != "Drug", headline


def test_english_text_is_not_changed_by_the_new_words():
    # these read as Iceland / Pakistan / NSA / tobacco before the fix
    assert extract("Firearms, drugs and weapons seized on Kangaroo Island", "").get("seizure_country") is None
    r = extract("Major seizure of 580 pounds of cocaine at a storage facility in Long Island City", "")
    assert r["seizure_country"] != "Iceland"
    r = extract("Pakistani man held with RM36,000 smuggled cigarettes in Tanjung Malim", "")
    assert r["seizure_country"] == "Malaysia"
    r = extract("CBP officers seize methamphetamine, heroin, fentanyl at Del Rio Port of Entry", "")
    assert r["primary_drug"] != "NSA"
    r = extract("Dozens of kilograms of crystal methamphetamine and thousands of ecstasy pills were seized", "")
    assert r["primary_drug"] == "Methamphetamine"


def test_turkish_packet_is_not_a_post_parcel():
    r = extract("Evinde 49 Paket Kokain Ele Geçirildi", "")
    assert r["transport"] != "Post/express"


def test_alias_conflicts():
    """A name must never be one country in one language and another in a second one."""
    from swatch import lang_more as M
    seen = {}
    for eng, aliases in M.country_rows():
        for a in aliases:
            n = L.norm(a)
            if n in seen and seen[n] != eng:
                raise AssertionError(f"{a!r} is both {seen[n]} and {eng}")
            seen[n] = eng
    for n, eng in seen.items():                      # nothing may override an alias that already meant something else
        old = L.COUNTRY_ALIAS.get(n)
        if old and not any("Ѐ" <= ch <= "ӿ" for ch in n):
            assert old == eng, (n, old, eng)


def test_all_nine_languages_are_searched():
    cfg = yaml.safe_load(open(os.path.join(os.path.dirname(__file__), "..", "config.yaml"), encoding="utf-8"))
    g = cfg["sources"]["google_news"]
    want = {"de": "AT", "da": "DK", "et": "EE", "am": "ET", "is": "IS", "mn": "MN", "no": "NO", "sk": "SK", "sv": "SE"}
    got = {e["lang"]: e["gl"] for e in g["editions"] if e["lang"] in want}
    assert got == want, got                         # YAML would turn a bare "no" into False: both must be quoted strings
    for lang in want:
        assert len(g["queries"][lang]) >= 8, lang
        assert cfg["sources"]["gdelt"]["queries"][lang], lang
        assert collect.GDELT_LANGS[lang] and translate._MYMEMORY_LOCALE[lang]
    for ed in g["editions"]:
        assert g["queries"].get(ed["lang"]), ed
        assert isinstance(ed["lang"], str) and isinstance(ed["gl"], str), ed
    sites = {s["site"]: s["lang"] for s in cfg["sources"]["official_sites"]["sites"]}
    for site in ("politi.dk", "toll.no", "tullverket.se", "emta.ee", "tollur.is", "customs.gov.mn", "financnasprava.sk", "bmi.gv.at", "ecc.gov.et"):
        assert site in sites and site in coverage.SITE_COUNTRY, site
    assert sites["toll.no"] == "no" and sites["tullverket.se"] == "sv"
    cov = coverage.payload(cfg)
    for lang in want:
        assert lang in cov["searched"] and lang in cov["names"], lang
    for c in ("Austria", "Denmark", "Estonia", "Ethiopia", "Iceland", "Mongolia", "Norway", "Slovakia", "Sweden"):
        assert c in cov["countries"] and cov["countries"][c]["langs"], c
    assert collect._ED_COUNTRY["IS"] == "Iceland" and collect._ED_COUNTRY["MN"] == "Mongolia"


def test_new_places_and_countries_have_map_coordinates():
    for name in ("Vienna", "Aarhus", "Oslo", "Gothenburg", "Tallinn", "Bratislava", "Reykjavik", "Keflavik", "Ulaanbaatar", "Addis Ababa", "Moyale"):
        assert name in geo.PLACE or name in geo.COUNTRY, name
    for c in ("Djibouti", "Eritrea", "South Sudan", "Iceland", "Mongolia", "Slovakia", "Estonia", "Ethiopia"):
        assert c in geo.COUNTRY, c
    for _disp, country, _als in L.PLACES:
        if country in ("Djibouti", "Eritrea", "South Sudan"):
            assert country in geo.COUNTRY


def test_cover_load_words_in_the_new_languages():
    assert cover.items("kaffee", "Kokain in Kaffee") == ["coffee"]
    assert cover.items("bananer", "") == ["banana"]
    assert cover.items("mobel", "") == ["furniture"]
    assert cover.items("kleidung", "Kokain in Paketen") == []            # body/clothing words are only kept when they stand alone
    assert cover.items("ቡና", "") == ["coffee"]
