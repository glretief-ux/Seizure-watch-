# -*- coding: utf-8 -*-
"""
Free, no-API-key translation of article headlines to English.

Tries MyMemory's free translation API first, falling back to deep-translator's
GoogleTranslator if that fails. MyMemory goes first because Google's free
endpoint has, in practice, never once succeeded from this project's run
environment (every historical headline was left untranslated with no error
ever surfaced - translate.py used to swallow every exception silently).
Neither library call takes an explicit network timeout, and a request that
hangs instead of cleanly failing can silently eat the whole run (this is
what caused a 45-minute workflow timeout the first time this was tried with
no cap) - _with_timeout() below bounds every single call.

On total failure (network hiccup, both endpoints down, unsupported language
code, empty text) this falls back to returning the original text unchanged,
so a translation problem never breaks a collection run.

`stats` tracks how many calls succeeded/failed and the last error seen, so
run_daily.py can report it in the run log instead of failures being
completely invisible, as they were before.

Results are cached in memory for the life of one run, since the same
headline often comes from several outlets on the same day.
"""
import threading

_cache = {}
stats = {"ok": 0, "fail": 0, "last_error": None, "streak": 0, "disabled": False}
MAX_FAIL_STREAK = 8   # after this many failures in a row both backends are treated as down for the rest of the run
CALL_TIMEOUT = 5  # seconds - deliberately short; there are a lot of headlines to get through,
# and the GitHub Actions job as a whole is only given 45 minutes (see .github/workflows/daily.yaml)


def _with_timeout(fn, timeout):
    """Run `fn` in a background thread and give up after `timeout` seconds.
    Needed because neither translation backend accepts a timeout of its own,
    and a hung connection otherwise blocks forever."""
    box = {}

    def worker():
        try:
            box["value"] = fn()
        except Exception as e:
            box["error"] = e

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        raise TimeoutError(f"no response within {timeout}s")
    if "error" in box:
        raise box["error"]
    return box.get("value")


def _via_mymemory(text, lang):
    from deep_translator import MyMemoryTranslator
    source = _MYMEMORY_LOCALE.get(str(lang).lower(), lang)
    return MyMemoryTranslator(source=source, target="en-GB").translate(text)


def _via_google(text):
    from deep_translator import GoogleTranslator
    return GoogleTranslator(source="auto", target="en").translate(text)


# MyMemory wants a full locale code (e.g. "es-ES"), not a bare ISO code - this
# covers the source languages this project actually collects (see config.yaml).
_MYMEMORY_LOCALE = {
    "es": "es-ES", "fr": "fr-FR", "de": "de-DE", "pt": "pt-PT", "ar": "ar-SA",
    "tr": "tr-TR", "ru": "ru-RU", "zh": "zh-CN", "hi": "hi-IN", "vi": "vi-VN", "nl": "nl-NL",
    "da": "da-DK", "et": "et-EE", "am": "am-ET", "is": "is-IS", "mn": "mn-MN", "no": "no-NO", "sk": "sk-SK", "sv": "sv-SE",
}


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
    if stats["disabled"]:  # backends are down: do not burn up to 10 s per headline (this caused the 45-minute timeouts)
        return text

    result = None
    for backend, args in ((_via_mymemory, (text, lang)), (_via_google, (text,))):
        try:
            out = _with_timeout(lambda: backend(*args), CALL_TIMEOUT)
            if out and out.strip():
                result = out.strip()
                break
        except Exception as e:
            stats["last_error"] = f"{backend.__name__}: {type(e).__name__}: {e}"

    if result is None:
        stats["fail"] += 1
        stats["streak"] += 1
        if stats["streak"] >= MAX_FAIL_STREAK:
            stats["disabled"] = True
        result = text
    else:
        stats["ok"] += 1
        stats["streak"] = 0

    _cache[key] = result
    return result
