# -*- coding: utf-8 -*-
"""Where the tool can and cannot see: which languages it searches, and the main languages of each country."""

LANG_NAMES = {
    "en": "English", "es": "Spanish", "fr": "French", "pt": "Portuguese", "ar": "Arabic", "tr": "Turkish", "ru": "Russian",
    "zh": "Chinese", "hi": "Hindi", "fa": "Persian", "ps": "Pashto", "sq": "Albanian", "hy": "Armenian", "de": "German",
    "az": "Azerbaijani", "bn": "Bengali", "be": "Belarusian", "nl": "Dutch", "bs": "Bosnian", "sr": "Serbian", "hr": "Croatian",
    "bg": "Bulgarian", "km": "Khmer", "cs": "Czech", "da": "Danish", "el": "Greek", "et": "Estonian", "am": "Amharic",
    "fi": "Finnish", "hu": "Hungarian", "is": "Icelandic", "id": "Indonesian", "he": "Hebrew", "it": "Italian", "ja": "Japanese",
    "kk": "Kazakh", "sw": "Swahili", "ky": "Kyrgyz", "lo": "Lao", "lv": "Latvian", "lt": "Lithuanian", "mg": "Malagasy",
    "ms": "Malay", "dv": "Dhivehi", "mt": "Maltese", "ro": "Romanian", "mn": "Mongolian", "my": "Burmese", "ne": "Nepali",
    "mk": "Macedonian", "no": "Norwegian", "ur": "Urdu", "tl": "Filipino", "pl": "Polish", "rw": "Kinyarwanda", "sk": "Slovak",
    "sl": "Slovenian", "so": "Somali", "ko": "Korean", "si": "Sinhala", "ta": "Tamil", "sv": "Swedish", "tg": "Tajik", "th": "Thai",
    "tk": "Turkmen", "uk": "Ukrainian", "uz": "Uzbek", "vi": "Vietnamese",
}

COUNTRY_LANGS = {
    "Afghanistan": ["fa", "ps"], "Albania": ["sq"], "Algeria": ["ar", "fr"], "Angola": ["pt"], "Argentina": ["es"], "Armenia": ["hy"],
    "Australia": ["en"], "Austria": ["de"], "Azerbaijan": ["az"], "Bahamas": ["en"], "Bahrain": ["ar"], "Bangladesh": ["bn"],
    "Belarus": ["ru", "be"], "Belgium": ["nl", "fr"], "Benin": ["fr"], "Bolivia": ["es"], "Bosnia and Herzegovina": ["bs", "sr", "hr"],
    "Brazil": ["pt"], "Bulgaria": ["bg"], "Burkina Faso": ["fr"], "Cambodia": ["km"], "Cameroon": ["fr", "en"], "Canada": ["en", "fr"],
    "Cape Verde": ["pt"], "Chile": ["es"], "China": ["zh"], "Colombia": ["es"], "Congo": ["fr"], "Costa Rica": ["es"], "Croatia": ["hr"],
    "Cuba": ["es"], "Curacao": ["nl"], "Cyprus": ["el", "tr"], "Czech Republic": ["cs"], "Denmark": ["da"], "Dominican Republic": ["es"],
    "Ecuador": ["es"], "Egypt": ["ar"], "El Salvador": ["es"], "Equatorial Guinea": ["es", "fr"], "Estonia": ["et"], "Ethiopia": ["am"],
    "Finland": ["fi"], "France": ["fr"], "French Guiana": ["fr"], "Gambia": ["en"], "Germany": ["de"], "Ghana": ["en"], "Greece": ["el"],
    "Guadeloupe": ["fr"], "Guatemala": ["es"], "Guinea": ["fr"], "Guinea-Bissau": ["pt"], "Guyana": ["en"], "Haiti": ["fr"],
    "Honduras": ["es"], "Hong Kong": ["zh", "en"], "Hungary": ["hu"], "Iceland": ["is"], "India": ["hi", "en"], "Indonesia": ["id"],
    "Iran": ["fa"], "Iraq": ["ar"], "Ireland": ["en"], "Israel": ["he"], "Italy": ["it"], "Ivory Coast": ["fr"], "Jamaica": ["en"],
    "Japan": ["ja"], "Jordan": ["ar"], "Kazakhstan": ["kk", "ru"], "Kenya": ["en", "sw"], "Kosovo": ["sq"], "Kuwait": ["ar"],
    "Kyrgyzstan": ["ky", "ru"], "Laos": ["lo"], "Latvia": ["lv"], "Lebanon": ["ar", "fr"], "Liberia": ["en"], "Libya": ["ar"],
    "Lithuania": ["lt"], "Luxembourg": ["fr", "de"], "Madagascar": ["mg", "fr"], "Malaysia": ["ms"], "Maldives": ["dv"], "Mali": ["fr"],
    "Malta": ["mt", "en"], "Martinique": ["fr"], "Mauritania": ["ar"], "Mauritius": ["en", "fr"], "Mexico": ["es"], "Moldova": ["ro", "ru"],
    "Mongolia": ["mn"], "Montenegro": ["sr"], "Morocco": ["ar", "fr"], "Mozambique": ["pt"], "Myanmar": ["my"], "Namibia": ["en"],
    "Nepal": ["ne"], "Netherlands": ["nl"], "New Zealand": ["en"], "Nicaragua": ["es"], "Niger": ["fr"], "Nigeria": ["en"],
    "North Macedonia": ["mk"], "Norway": ["no"], "Oman": ["ar"], "Pakistan": ["ur", "en"], "Panama": ["es"], "Papua New Guinea": ["en"],
    "Paraguay": ["es"], "Peru": ["es"], "Philippines": ["tl", "en"], "Poland": ["pl"], "Portugal": ["pt"], "Puerto Rico": ["es", "en"],
    "Qatar": ["ar"], "Romania": ["ro"], "Russia": ["ru"], "Rwanda": ["rw", "fr", "en"], "Saudi Arabia": ["ar"], "Senegal": ["fr"],
    "Serbia": ["sr"], "Sierra Leone": ["en"], "Singapore": ["en", "zh"], "Slovakia": ["sk"], "Slovenia": ["sl"], "Somalia": ["so", "ar"],
    "South Africa": ["en"], "South Korea": ["ko"], "Spain": ["es"], "Sri Lanka": ["si", "ta"], "Sudan": ["ar"], "Suriname": ["nl"],
    "Sweden": ["sv"], "Switzerland": ["de", "fr"], "Syria": ["ar"], "Taiwan": ["zh"], "Tajikistan": ["tg", "ru"], "Tanzania": ["sw", "en"],
    "Thailand": ["th"], "Togo": ["fr"], "Trinidad and Tobago": ["en"], "Tunisia": ["ar", "fr"], "Turkey": ["tr"], "Turkmenistan": ["tk", "ru"],
    "Uganda": ["en"], "Ukraine": ["uk", "ru"], "United Arab Emirates": ["ar", "en"], "United Kingdom": ["en"], "United States": ["en", "es"],
    "Uruguay": ["es"], "Uzbekistan": ["uz", "ru"], "Venezuela": ["es"], "Vietnam": ["vi"], "Yemen": ["ar"], "Zambia": ["en"], "Zimbabwe": ["en"],
}

# official websites searched by the tool (config.yaml -> official_sites) and the country each one belongs to
SITE_COUNTRY = {
    "cbp.gov": "United States", "dea.gov": "United States", "justice.gov": "United States", "ice.gov": "United States",
    "uscg.mil": "United States", "gov.uk": "United Kingdom", "afp.gov.au": "Australia", "abf.gov.au": "Australia",
    "sars.gov.za": "South Africa", "saps.gov.za": "South Africa", "ndlea.gov.ng": "Nigeria", "nacoc.gov.gh": "Ghana",
    "pib.gov.in": "India", "pdea.gov.ph": "Philippines", "cnb.gov.sg": "Singapore", "douane.gouv.fr": "France", "zoll.de": "Germany",
    "guardiacivil.es": "Spain", "agenciatributaria.es": "Spain", "policia.gov.co": "Colombia", "aduana.gob.ec": "Ecuador",
    "gob.pe": "Peru", "gob.mx": "Mexico", "gov.br": "Brazil",
}


def payload(cfg):
    """What the dashboard needs to draw the coverage map."""
    src = cfg.get("sources", {})
    searched = sorted({e["lang"] for e in src.get("google_news", {}).get("editions", [])} or {"en"})
    official = {SITE_COUNTRY[s] for s in (src.get("official_sites", {}) or {}).get("sites", []) if s in SITE_COUNTRY}
    official |= {f["country"] for f in (src.get("rss_feeds") or []) if f.get("country")}
    return {"searched": searched, "names": {k: v for k, v in LANG_NAMES.items()},
            "countries": {c: {"langs": l, "official": c in official} for c, l in COUNTRY_LANGS.items()}}
