# -*- coding: utf-8 -*-
"""
Free, no-API-key translation of article headlines to English.

Tries deep-translator's GoogleTranslator first (Google's public translation
endpoint), falling back to MyMemory (also free, no key) if that fails -
useful because Google's free endpoint is sometimes rate-limited or blocked
on shared CI IP ranges like GitHub Actions runners. On total failure
(network hiccup, both endpoints rate-limited, unsupported language code,
empty text) this falls back to returning the original text unchanged, so a
translation problem never breaks a collection run.

`stats` tracks how many calls succeeded/failed and the last error seen, so
run_daily.py can report it in the run log instead of failures being
completely invisible, as they were before.

Results are cached in memory for the life of one run, since the same
headline often comes from several outlets on the same day.
"""
_cache = {}
stats = {"ok": 0, "fail": 0, "last_error": None}


def _via_google(text):
    from deep_translator import GoogleTranslator
    return GoogleTranslator(source="auto", target="en").translate(text)


# MyMemory wants a full locale code (e.g. "es-ES"), not a bare ISO code - this
# covers the source languages this project actually collects (see config.yaml).
_MYMEMORY_LOCALE = {
    "es": "es-ES", "fr": "fr-FR", "de": "de-DE", "pt": "pt-PT", "ar": "ar-SA",
    "tr": "tr-TR", "ru": "ru-RU", "zh": "zh-CN", "hi": "hi-IN", "vi": "vi-VN",
}


def _via_mymemory(text, lang):
    from deep_translator import MyMemoryTranslator
    source = _MYMEMORY_LOCALE.get(str(lang).lower(), lang)
    return MyMemoryTranslator(source=source, target="en-GB").translate(text)


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

    result = None
    for backend, args in ((_via_google, (text,)), (_via_mymemory, (text, lang))):
        try:
            out = backend(*args)
            if out and out.strip():
                result = out.strip()
                break
        except Exception as e:
            stats["last_error"] = f"{backend.__name__}: {type(e).__name__}: {e}"

    if result is None:
        stats["fail"] += 1
        result = text
    else:
        stats["ok"] += 1

    _cache[key] = result
    return result
