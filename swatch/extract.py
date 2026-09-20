# -*- coding: utf-8 -*-
"""
Turn one article (title + text) into structured seizure facts.
Pure rules - no API, no cost, deterministic. Accuracy is good for headline-style
facts (drug, weight, port, concealment) and weaker for routing, so every event
keeps its link for analyst verification.
"""
import re
from . import lexicon as L

NUMW = (r"(\d{1,3}|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|dos|tres|cuatro|cinco|seis|siete|"
        r"ocho|nueve|diez|deux|trois|quatre|cinq|sept|huit|neuf|dix)")
WORDNUM = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve".split())}
WORDNUM.update({"dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6, "siete": 7, "ocho": 8, "nueve": 9,
                "diez": 10, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5, "sept": 7, "huit": 8, "neuf": 9, "dix": 10})

NUM = r"(\d{1,3}(?:[.,]\d{3})+(?:[.,]\d+)?|\d+(?:[.,]\d+)?)"
MULT = r"(?:\s*(million|millions|millon|millones|milhao|milhoes|billion|thousand|mil)(?![a-z]))?"
W_UNITS = (r"(tonnes?|tons?|toneladas?|tonelada|kilograms?|kilogrammes?|kilogramos|kilogramas|quilogramas?|kilos?|kgs?|"
           r"grams?|grammes?|gramos?|gramas?|g|lbs?|pounds?|libras?)")
WEIGHT_RX = re.compile(NUM + MULT + r"[\s-]*" + W_UNITS + r"(?![a-z])")
UNIT_RX = re.compile(NUM + MULT + r"[\s-]*(?:[a-z]+\s+)?(pills|tablets|capsules|comprimidos|pastillas|pilulas|pilules|"
                     r"comprimes|cigarettes|cigarrillos|cigarros|sticks|packs|cartons|cajetillas|master\s+cases|"
                     r"plants|plantas|plantes|doses|bricks|ladrillos|packages|packets|paquetes|bales|fardos|bundles)"
                     r"(?![a-z])")
UNIT_KIND = {"pills": "pills", "tablets": "pills", "capsules": "pills", "comprimidos": "pills", "pastillas": "pills",
             "pilulas": "pills", "pilules": "pills", "comprimes": "pills", "doses": "doses",
             "cigarettes": "cigarettes", "cigarrillos": "cigarettes", "cigarros": "cigarettes", "sticks": "cigarettes",
             "packs": "packs", "cartons": "packs", "cajetillas": "packs", "master cases": "cases",
             "plants": "plants", "plantas": "plants", "plantes": "plants"}
ARREST_A = re.compile(NUMW + r"\s+(?:\w+\s+){0,3}?(?:were\s+|was\s+|have\s+been\s+|fueron\s+|han\s+sido\s+|ont\s+ete\s+)?"
                      r"(?:arrested|detained|charged|apprehended|captured|detenid\w+|arrestad\w+|capturad\w+|"
                      r"aprehendid\w+|interpelad\w+|arrete\w*|interpelle\w*|presos|detidos|presas)")
ARREST_B = re.compile(r"(?:arrested|detained|arrestaron\s+a|detuvieron\s+a|arrests?\s+of|arrestation\s+de|"
                      r"interpellation\s+de)\s+(?:a\s+total\s+of\s+)?" + NUMW +
                      r"\s+(?:people|persons|men|women|suspects|individuals|others|personas|hombres|mujeres|"
                      r"sospechosos|personnes|individus|pessoas)")
ARREST_C = re.compile(r"(?:detenid\w+|arrestad\w+|capturad\w+|aprehendid\w+|interpelad\w+|interpelle\w*|arrete\w*)\s+"
                      + NUMW + r"\s+\w+")


def parse_num(s):
    s = s.strip()
    if re.fullmatch(r"\d{1,3}([.,]\d{3})+", s) and not s.startswith("0"):
        return float(re.sub(r"[.,]", "", s))
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".") if s.rfind(",") > s.rfind(".") else s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".")
    return float(s)


def _mult(m):
    return {"million": 1e6, "millions": 1e6, "millon": 1e6, "millones": 1e6, "milhao": 1e6, "milhoes": 1e6,
            "billion": 1e9, "thousand": 1e3, "mil": 1e3}.get(m, 1.0) if m else 1.0


def _kg_factor(u):
    if u.startswith("ton"):
        return 1000.0
    if u.startswith(("kilo", "kg", "quilo")):
        return 1.0
    if u.startswith(("lb", "pound", "libra")):
        return 0.45359
    return 0.001  # gram, gramme, gramo, g


def _word_to_int(w):
    return int(w) if w.isdigit() else WORDNUM.get(w)


def _in_context(t, s, e, width=110):
    seg = t[max(0, s - width): e + width]
    return bool(L.ANY_DRUG.search(seg) or L.SEIZURE.search(seg))


def _drugs(title_n, text_n):
    counts = {}
    for name, pat in L.DRUG_PATTERNS.items():
        c = len(pat.findall(text_n)) + 3 * len(pat.findall(title_n))
        if c:
            counts[name] = c
    ordered = sorted(counts, key=counts.get, reverse=True)
    if ordered:
        return ordered[0], ordered
    if L.GENERIC_DRUG.search(title_n + " " + text_n):
        return "Unspecified", []
    return None, []


def _quantities(t, primary):
    best_kg, kg_hits = None, []
    for m in WEIGHT_RX.finditer(t):
        if not _in_context(t, m.start(), m.end()):
            continue
        try:
            kg = parse_num(m.group(1)) * _mult(m.group(2)) * _kg_factor(m.group(3))
        except ValueError:
            continue
        kg_hits.append(kg)
    if kg_hits:
        best_kg = max(kg_hits)
    best_units, unit_type = None, None
    for m in UNIT_RX.finditer(t):
        if not _in_context(t, m.start(), m.end()):
            continue
        try:
            v = parse_num(m.group(1)) * _mult(m.group(2))
        except ValueError:
            continue
        kind = UNIT_KIND.get(re.sub(r"\s+", " ", m.group(3)), "packages")
        if primary == "Cigarettes" and kind not in ("cigarettes", "packs", "cases"):
            continue
        if best_units is None or v > best_units:
            best_units, unit_type = v, kind
    return best_kg, best_units, unit_type


def _concealment(t, in_container):
    cats, detail = [], []
    for name, pat in L.CONCEALMENT.items():
        ms = list(pat.finditer(t))
        if ms:
            cats.append(name)
            detail.extend(m.group(0).strip() for m in ms[:2])
    gm = L.GENERIC_COMPARTMENT.search(t)
    if gm:
        if L.VEHICLE_WORDS.search(t):
            cats.append("Vehicle compartment") if "Vehicle compartment" not in cats else None
        elif in_container:
            cats.append("Container structure / false compartment") if \
                "Container structure / false compartment" not in cats else None
        else:
            cats.append("Hidden compartment (unspecified)")
        detail.append(gm.group(0).strip())
    return cats, detail[:4]


def _transport(t, cats, in_container):
    if "Postal / parcel" in cats and not in_container:
        return "Post/express"
    if in_container:
        return "Sea - container"
    scores = {k: len(p.findall(t)) for k, p in L.TRANSPORT.items()}
    if ("Body concealment" in cats or "Luggage / passenger goods" in cats) and scores["Air"] > 0:
        return "Air - passenger"
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "Unknown"
    # port/ship words but no container word -> general sea cargo
    return "Sea - cargo (other)" if best == "Sea - container/cargo" else best


def _mentions(t):
    ments = []
    masked = list(t)
    for m in L.PLACE_RX.finditer(t):
        disp, ctry = L.PLACE_ALIAS[m.group(1)]
        ments.append([m.start(), m.end(), "place", disp, ctry])
        for i in range(m.start(), m.end()):
            masked[i] = " "
    mt = "".join(masked)
    for m in L.COUNTRY_RX.finditer(mt):
        c = L.COUNTRY_ALIAS[m.group(1)]
        ments.append([m.start(), m.end(), "country", c, c])
    ments.sort(key=lambda x: x[0])
    # a country written right after one of its own ports ("Guayaquil, Ecuador") is a duplicate
    out = []
    for m in ments:
        if out and m[2] == "country" and out[-1][2] == "place" and out[-1][4] == m[4] and m[0] - out[-1][1] <= 4:
            continue
        out.append(m)
    return out


def _route(t, source_country):
    ments = _mentions(t)
    roles = []
    for i, (s, e, kind, disp, ctry) in enumerate(ments):
        pre = t[max(0, s - 60): s]
        role = None
        if L.ORIGIN_CUE.search(pre):
            role = "origin"
        elif L.TRANSIT_CUE.search(pre):
            role = "transit"
        elif L.DEST_CUE.search(pre):
            role = "dest"
        elif L.TO_CUE.search(pre) and i > 0 and roles[i - 1] in ("origin", "transit") and s - ments[i - 1][1] <= 30:
            role = "dest"
        roles.append(role)

    def first(role):
        for m, r in zip(ments, roles):
            if r == role:
                return m
        return None

    o, d = first("origin"), first("dest")
    transit = []
    for m, r in zip(ments, roles):
        if r == "transit" and m[4] not in transit and (not o or m[4] != o[4]) and (not d or m[4] != d[4]):
            transit.append(m[4])
    unl = [m for m, r in zip(ments, roles) if r is None]
    sz_place = next((m for m in unl if m[2] == "place"), None)
    sz_ctry = next((m for m in unl if m[2] == "country"), None)
    seizure_place = sz_place[3] if sz_place else None
    seizure_country, conf = None, "low"
    if sz_place:
        seizure_country, conf = sz_place[4], "high"
    elif sz_ctry:
        seizure_country, conf = sz_ctry[4], "medium"
    elif source_country:
        seizure_country = source_country
    origin = o[4] if o else None
    dest = d[4] if d else None
    res = {
        "origin": origin, "origin_place": o[3] if o and o[2] == "place" else None,
        "destination": dest, "destination_place": d[3] if d and d[2] == "place" else None,
        "transit": "|".join(transit) or None,
        "seizure_country": seizure_country, "seizure_place": seizure_place, "location_conf": conf,
    }
    corridor = None
    if origin and dest and origin != dest:
        corridor = f"{origin} -> {dest}"
    elif origin and seizure_country and origin != seizure_country and not dest:
        corridor = f"{origin} -> {seizure_country}"
    elif dest and seizure_country and dest != seizure_country and not origin:
        corridor = f"{seizure_country} -> {dest}"
    res["corridor"] = corridor
    parts = [p for p in [origin] + transit + [dest or (seizure_country if seizure_country != origin else None)] if p]
    dedup = [p for i, p in enumerate(parts) if i == 0 or p != parts[i - 1]]
    res["route"] = " -> ".join(dedup) if len(dedup) >= 2 else None
    return res


def _arrests(t):
    best = 0
    for rxp in (ARREST_A, ARREST_B, ARREST_C):
        for m in rxp.finditer(t):
            v = _word_to_int(m.group(1))
            if v and v < 200:
                best = max(best, v)
    return best or None


def fmt_qty(kg, units, unit_type):
    parts = []
    if kg:
        parts.append(f"{kg / 1000:.1f} t" if kg >= 1000 else f"{kg:.0f} kg")
    if units:
        parts.append(f"{units:,.0f} {unit_type}")
    return ", ".join(parts)


def extract(title, text="", source_country=None):
    """Return a dict of facts. rec['relevant'] tells whether it is a real seizure story."""
    title_n, text_n = L.norm(title), L.norm(text)
    t = (title_n + ". " + text_n).strip()
    primary, drugs = _drugs(title_n, text_n)
    rec = {"relevant": 0}
    if not primary or not L.SEIZURE.search(t) or L.EXCLUDE.search(title_n):
        return rec
    kg, units, unit_type = _quantities(t, primary)
    in_container = 1 if L.CONTAINER.search(t) else 0
    cats, detail = _concealment(t, in_container)
    route = _route(t, source_country)
    arrests = _arrests(t)
    has_substance = bool(kg or units or arrests or cats or route["seizure_country"])
    if not has_substance or (primary == "Unspecified" and not (kg or units)):
        return rec
    transport = _transport(t, cats, in_container)
    organized = 1 if L.ORGANIZED.search(t) else 0
    insider = 1 if L.INSIDER.search(t) else 0
    controlled = 1 if L.CONTROLLED_DELIVERY.search(t) else 0
    coverload = 1 if re.search(r"cover\s*load|carga\s+de\s+cobertura", t) else 0
    rec.update({
        "relevant": 1, "primary_drug": primary, "drugs": "|".join(drugs),
        "qty_kg": kg, "qty_units": units, "unit_type": unit_type,
        "concealment": "|".join(cats) or None, "concealment_detail": "; ".join(detail) or None,
        "transport": transport, "in_container": in_container,
        "arrests": arrests, "organized": organized, "insider": insider,
        "controlled_delivery": controlled, "coverload": coverload,
    })
    rec.update(route)
    q = fmt_qty(kg, units, unit_type)
    bits = [f"{primary}" + (f" ({q})" if q else ""), transport if transport != "Unknown" else None,
            ("concealed: " + "; ".join(cats)) if cats else None,
            ("route: " + route["route"]) if route["route"] else None,
            f"{arrests} arrests" if arrests else None,
            "insider indicators" if insider else None, "controlled delivery" if controlled else None]
    rec["mo_summary"] = " | ".join(b for b in bits if b)
    rec["completeness"] = sum([primary != "Unspecified", bool(kg or units), bool(cats), transport != "Unknown",
                               bool(route["origin"]), bool(route["destination"]), bool(route["seizure_country"])])
    return rec
