# -*- coding: utf-8 -*-
"""Seizure events laid out like the UNODC-WCO open-source workbook (templates/OPEN_source_template.xlsx).

The Excel download opens on "Sheet1" with exactly the template's columns, one row per seizure
(duplicate reports of the same seizure are already merged into one event). The header row and the
column widths are read from the template file itself, so changing the template changes the output.
Only facts the tool actually extracted are filled in; every other cell is left empty, never guessed.
"""
import os
import pandas as pd

TEMPLATE = os.path.join(os.path.dirname(__file__), "..", "templates", "OPEN_source_template.xlsx")
SHEET = "Sheet1"

# fallback if the template file is missing (same columns, same order)
COLUMNS = ["title", "seizure_date", "article_date", "article_url", "seizure_country", "seizure_country_iso2", "seizure_city",
           "commodity", "commodity_l1", "commodity_detail", "quantity", "unit", "value_reported", "currency_reported", "est_value",
           "est_value_currency", "detection_method", "concealment", "conveyance", "conveyance_detail", "carrier_ref", "cargo_description",
           "departure_country", "departure_country_iso2", "departure_city", "departure_location", "transit_country", "transit_country_iso2",
           "transit_city", "transit_location", "destination_country", "destination_country_iso2", "destination_city", "destination_location",
           "seizing_agency", "suspects", "nationality", "note"]

ISO2 = {
    "Afghanistan": "AF", "Albania": "AL", "Algeria": "DZ", "Argentina": "AR", "Armenia": "AM", "Australia": "AU", "Austria": "AT",
    "Azerbaijan": "AZ", "Bahamas": "BS", "Bahrain": "BH", "Bangladesh": "BD", "Belarus": "BY", "Belgium": "BE", "Benin": "BJ",
    "Bolivia": "BO", "Bosnia and Herzegovina": "BA", "Brazil": "BR", "Bulgaria": "BG", "Cambodia": "KH", "Cameroon": "CM",
    "Canada": "CA", "Cape Verde": "CV", "Chile": "CL", "China": "CN", "Colombia": "CO", "Costa Rica": "CR", "Croatia": "HR",
    "Cuba": "CU", "Curacao": "CW", "Cyprus": "CY", "Czech Republic": "CZ", "Denmark": "DK", "Dominican Republic": "DO",
    "Ecuador": "EC", "Egypt": "EG", "El Salvador": "SV", "Estonia": "EE", "Ethiopia": "ET", "Fiji": "FJ", "Finland": "FI",
    "France": "FR", "French Guiana": "GF", "Germany": "DE", "Ghana": "GH", "Greece": "GR", "Guatemala": "GT", "Guinea": "GN",
    "Guinea-Bissau": "GW", "Guyana": "GY", "Honduras": "HN", "Hong Kong": "HK", "Hungary": "HU", "India": "IN", "Indonesia": "ID",
    "Iran": "IR", "Iraq": "IQ", "Ireland": "IE", "Israel": "IL", "Italy": "IT", "Ivory Coast": "CI", "Jamaica": "JM", "Japan": "JP",
    "Jordan": "JO", "Kazakhstan": "KZ", "Kenya": "KE", "Kosovo": "XK", "Kuwait": "KW", "Kyrgyzstan": "KG", "Laos": "LA",
    "Latvia": "LV", "Lebanon": "LB", "Liberia": "LR", "Libya": "LY", "Lithuania": "LT", "Luxembourg": "LU", "Madagascar": "MG",
    "Malaysia": "MY", "Maldives": "MV", "Mali": "ML", "Malta": "MT", "Martinique": "MQ", "Mauritius": "MU", "Mexico": "MX",
    "Moldova": "MD", "Montenegro": "ME", "Morocco": "MA", "Mozambique": "MZ", "Myanmar": "MM", "Namibia": "NA", "Nepal": "NP",
    "Netherlands": "NL", "New Zealand": "NZ", "Nicaragua": "NI", "Niger": "NE", "Nigeria": "NG", "North Macedonia": "MK",
    "Norway": "NO", "Oman": "OM", "Pakistan": "PK", "Panama": "PA", "Papua New Guinea": "PG", "Paraguay": "PY", "Peru": "PE",
    "Philippines": "PH", "Poland": "PL", "Portugal": "PT", "Puerto Rico": "PR", "Qatar": "QA", "Romania": "RO", "Russia": "RU",
    "Saudi Arabia": "SA", "Senegal": "SN", "Serbia": "RS", "Sierra Leone": "SL", "Singapore": "SG", "Slovakia": "SK",
    "Slovenia": "SI", "Somalia": "SO", "South Africa": "ZA", "South Korea": "KR", "Spain": "ES", "Sri Lanka": "LK", "Sudan": "SD",
    "Sweden": "SE", "Switzerland": "CH", "Syria": "SY", "Taiwan": "TW", "Tajikistan": "TJ", "Thailand": "TH",
    "Trinidad and Tobago": "TT", "Tunisia": "TN", "Turkey": "TR", "Turkmenistan": "TM", "Uganda": "UG", "Ukraine": "UA",
    "United Arab Emirates": "AE", "United Kingdom": "GB", "United States": "US", "Uruguay": "UY", "Uzbekistan": "UZ",
    "Venezuela": "VE", "Vietnam": "VN", "Yemen": "YE", "Zambia": "ZM", "Zimbabwe": "ZW",
}

# Seizure Watch category -> the template's "commodity" vocabulary
COMMODITY = {"Drug": "Drug", "Precursor chemical": "Precursor", "Arms and ammunition": "Weapon"}
# other quantity units -> the template's units (kg, pcs, litres, units)
UNIT = {"pills": "pcs", "cigarettes": "pcs", "rounds": "pcs", "doses": "pcs", "packs": "pcs"}
TRANSPORT = {"Road": ("Road", ""), "Rail": ("Rail", ""), "Post/express": ("Post", ""), "Air": ("Air", ""), "Air - passenger": ("Air", "Passenger"),
             "Sea - container": ("Sea", "Container"), "Sea - cargo (other)": ("Sea", "Cargo"), "Sea - vessel/small craft": ("Sea", "Vessel / small craft")}


def _s(v):
    """Text or None: empty, NaN and list-like blanks all become None."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    if isinstance(v, (list, tuple, set)):
        v = "; ".join(str(x) for x in v if x)
    v = str(v).strip()
    return v or None


def _iso(name):
    if not name:
        return None
    return "; ".join(ISO2.get(p.strip()) or "" for p in str(name).split(";")) if ";" in str(name) else ISO2.get(str(name).strip())


def _num(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if pd.isna(f) else (int(f) if f == int(f) else round(f, 3))


def template_headers():
    """Header row of the template file (falls back to the built-in list)."""
    try:
        import openpyxl
        ws = openpyxl.load_workbook(TEMPLATE, read_only=True).active
        row = [c for c in next(ws.iter_rows(min_row=1, max_row=1, values_only=True)) if c]
        return row or COLUMNS
    except Exception:
        return COLUMNS


def template_widths(headers):
    """Column widths copied from the template (capped so one long text column cannot take the screen)."""
    out = {}
    try:
        import openpyxl
        from openpyxl.utils import get_column_letter
        ws = openpyxl.load_workbook(TEMPLATE).active
        for i, _h in enumerate(headers, 1):
            w = ws.column_dimensions[get_column_letter(i)].width
            out[i] = min(80, w) if w else 18
    except Exception:
        out = {i: 18 for i in range(1, len(headers) + 1)}
    return out


def template_table(ev, verifications=None):
    """One row per seizure event, columns named and ordered like the template."""
    verifications = verifications or {}
    rows = []
    for g in ev.to_dict("records"):
        kg, other, unit = _num(g.get("qty_kg")), _num(g.get("qty_units")), _s(g.get("unit_type"))
        detail = [_s(g.get("mo_summary"))]
        if kg is not None and other is not None and unit:
            detail.insert(0, f"{other:,} {unit}")
        if kg is not None:
            quantity, qunit = kg, "kg"
        elif other is not None:
            quantity, qunit = other, UNIT.get(unit or "", "units")
        else:
            quantity, qunit = None, None
        conv, conv_detail = TRANSPORT.get(_s(g.get("transport")) or "", (None, None))
        transit = _s(g.get("transit_list"))
        flags = _s(g.get("risk_flags")) or ""
        arrests = _num(g.get("arrests"))
        n_src = _num(g.get("n_sources")) or 1
        outlets = g.get("outlets")
        outlets = ", ".join(str(x) for x in outlets if x) if isinstance(outlets, (list, tuple, set)) else _s(outlets)
        v = verifications.get(g.get("event_id"), {}) or {}
        note = " ".join(x for x in [
            (f"Merged from {n_src} reports" if n_src > 1 else "Single report") + (f": {outlets}." if outlets else "."),
            f"Verification: {v['status']}." if v.get("status") else None, _s(v.get("note"))] if x)
        urls = g.get("urls")
        rows.append({
            "title": _s(g.get("title_en")) or _s(g.get("title")),
            "seizure_date": None,                                    # the tool only knows the first report date
            "article_date": pd.Timestamp(g["date"]).strftime("%Y-%m-%d") if pd.notna(g.get("date")) else None,
            "article_url": (urls[0] if urls is not None and len(urls) else None),
            "seizure_country": _s(g.get("seizure_country")), "seizure_country_iso2": _iso(_s(g.get("seizure_country"))),
            "seizure_city": _s(g.get("seizure_place")),
            "commodity": COMMODITY.get(_s(g.get("category")) or "Drug", "Other"),
            "commodity_l1": "Suspected illicit substance" if _s(g.get("primary_drug")) == "Unspecified" else _s(g.get("primary_drug")),
            "commodity_detail": "; ".join(x for x in detail if x) or None,
            "quantity": quantity, "unit": qunit,
            "value_reported": None, "currency_reported": None, "est_value": None, "est_value_currency": "USD",
            "detection_method": "Intelligence-led operation" if "Intelligence-led" in flags else None,
            "concealment": _s(g.get("conceal_list")),
            "conveyance": conv, "conveyance_detail": conv_detail or None,
            "carrier_ref": _s(g.get("container_numbers")),         # container numbers only; vessel names are too noisy to publish here
            "cargo_description": _s(g.get("cover_cargo")),
            "departure_country": _s(g.get("origin")), "departure_country_iso2": _iso(_s(g.get("origin"))),
            "departure_city": _s(g.get("origin_place")), "departure_location": None,
            "transit_country": transit, "transit_country_iso2": _iso(transit), "transit_city": None, "transit_location": None,
            "destination_country": _s(g.get("destination")), "destination_country_iso2": _iso(_s(g.get("destination"))),
            "destination_city": _s(g.get("destination_place")), "destination_location": None,
            "seizing_agency": None,
            "suspects": (f"{int(arrests)} arrest{'s' if arrests != 1 else ''}" if arrests and arrests > 0 else None),
            "nationality": None, "note": note,
        })
    df = pd.DataFrame(rows, columns=COLUMNS)
    return df.sort_values(["article_date"], ascending=False, kind="stable").reset_index(drop=True)


def write_template_sheet(xw, ev, verifications=None):
    """Add Sheet1 (template layout) as the first sheet of an open pandas ExcelWriter, with the template's widths."""
    headers = template_headers()
    df = template_table(ev, verifications)
    for h in headers:
        if h not in df.columns:
            df[h] = None
    df = df[headers]
    ws = xw.book.create_sheet(SHEET, 0)
    ws.append(headers)
    for rec in df.itertuples(index=False, name=None):
        ws.append([None if (isinstance(x, float) and pd.isna(x)) else x for x in rec])
    ws.auto_filter.ref = ws.dimensions
    for i, w in template_widths(headers).items():
        ws.column_dimensions[ws.cell(1, i).column_letter].width = w
    xw.book.active = 0
    return ws
