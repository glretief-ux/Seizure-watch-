# -*- coding: utf-8 -*-
"""
Free, no-API-key translation of article headlines to English.

Uses deep-translator's GoogleTranslator, which calls Google's public
translation endpoint - no account or API key needed, matching the rest of
this project's "free, no-API-key" design. On any failure (network hiccup,
endpoint rate limit, unsupported language code, empty text) this falls back
to returning the original text unchanged, so a translation problem never
breaks a collection run.

Results are cached in memory for the life of one run, since the same
headline often comes from several outlets on the same day.
"""
_cache = {}


def to_english(text, lang):
    """Translate `text` (in `lang`) to English. Returns the original text
    unchanged if `lang` is already English/unknown, or if translation fails."""
    if not text:
        return text
    if not lang or str(lang).lower().startswith("en"):
        return text

    key = (str(lang).lower(), text)
    if key in _cache:
        return _cache[key]

    try:
        from deep_translator import GoogleTranslator
        translated = GoogleTranslator(source="auto", target="en").translate(text)
        result = translated.strip() if translated and translated.strip() else text
    except Exception:
        result = text

    _cache[key] = result
    return result
