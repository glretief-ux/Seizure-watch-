# -*- coding: utf-8 -*-
"""
Optional Named Entity Recognition (NER) over already-translated (English)
headlines - a supplement to the rule-based extraction in extract.py, not
a replacement for it.

Runs on title_en, never on the original-language text, so only one
lightweight English model is needed regardless of how many source
languages are collected (9, at last count). Results are only used as a
fallback: when extract.py's cue-based _route()/_vessel()/_shipping_lines()
already found something, that stays - NER is strictly for the cases the
lexicon comes up empty on, and for flagging unrecognised place names as a
worklist for growing the gazetteer in lexicon.py/geo.py over time.

PERSON entities are deliberately never returned as text: names of
suspects or officials add legal/privacy risk with no analytical benefit
here, in the same spirit as the "facts and links only, not article text"
rule already applied elsewhere in this project. Only a count is exposed.

If spaCy or its English model isn't installed, every function here
degrades to a no-op empty result, exactly like translate.py's fallback -
a missing NER model should never break a collection run.
"""
_nlp = None
_load_failed = False


def _get_model():
    global _nlp, _load_failed
    if _nlp is not None or _load_failed:
        return _nlp
    try:
        import spacy
        _nlp = spacy.load("en_core_web_sm", disable=["parser", "lemmatizer", "tagger"])
    except Exception:
        _load_failed = True
        _nlp = None
    return _nlp


_ORG_BLOCKLIST = {
    "customs", "police", "coast guard", "coastguard", "border force", "border patrol",
    "navy", "army", "immigration", "interpol", "europol", "dea", "fbi", "cbp", "hmrc",
    "authorities", "officials", "government", "ministry", "airport", "port authority",
}


def _looks_like_org(text):
    """Reject an ORG candidate that's actually a law-enforcement agency, a
    known place/port name, or a drug name - the small English model mixes
    these up constantly on this kind of headline (e.g. tagging "Sines" or
    "MDMA" as an organisation), and a wrong shipping-line guess is worse
    than none at all."""
    t = text.strip().lower()
    if not t or t in _ORG_BLOCKLIST:
        return False
    from .lexicon import norm, PLACE_ALIAS, COUNTRY_ALIAS, ANY_DRUG
    if norm(text) in PLACE_ALIAS or norm(text) in COUNTRY_ALIAS:
        return False
    if ANY_DRUG.search(text):
        return False
    return True


def extract_entities(text_en):
    """Returns {"places": [...], "orgs": [...], "person_count": N} from
    English text. Empty/zero result if NER isn't available or the text
    is empty - callers should treat this as "no extra information", not
    as an error."""
    empty = {"places": [], "orgs": [], "person_count": 0}
    if not text_en:
        return empty
    nlp = _get_model()
    if nlp is None:
        return empty
    try:
        doc = nlp(text_en)
    except Exception:
        return empty
    places, orgs, persons = [], [], 0
    for ent in doc.ents:
        if ent.label_ in ("GPE", "LOC"):
            places.append(ent.text)
        elif ent.label_ == "ORG":
            if _looks_like_org(ent.text):
                orgs.append(ent.text)
        elif ent.label_ == "PERSON":
            persons += 1
    return {"places": _dedup(places), "orgs": _dedup(orgs), "person_count": persons}


def _dedup(items):
    seen, out = set(), []
    for x in items:
        k = x.strip().lower()
        if k and k not in seen:
            seen.add(k)
            out.append(x.strip())
    return out


def resolve_country(place_text):
    """Try to match a free-text place name (e.g. from NER) against the
    existing COUNTRY_ALIAS and PLACE_ALIAS gazetteers (checking both, since
    a port/city like "Antwerp" only appears in PLACE_ALIAS, not as a
    country name itself). Returns the canonical country name, or None if
    the text isn't recognised in either - an unmatched name is a genuine
    candidate to add to the gazetteer, not something to discard silently."""
    if not place_text:
        return None
    from .lexicon import norm, COUNTRY_ALIAS, PLACE_ALIAS
    key = norm(place_text)
    if key in COUNTRY_ALIAS:
        return COUNTRY_ALIAS[key]
    if key in PLACE_ALIAS:
        return PLACE_ALIAS[key][1]  # (display_name, country) -> country
    return None
