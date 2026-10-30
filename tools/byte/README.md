# Byte for any page

`dist/byte.js` is Byte (animated helper, chat, microphone, read-aloud) as one file you can drop into any static page.

1. Copy `dist/byte.js` next to the page and write a `byte-config.js` (see the examples in the repos that use it): name, starter questions, `faqs` with keywords `k`, an answer `a` (HTML) and optional `go` buttons (`focus`, `click`, `go`, `set` or `href` plus a `label`), and optionally `search` (a CSS selector for the page's search box).
2. Add before `</body>`: `<script src="byte-config.js"></script>` and `<script src="byte.js"></script>`.

`build_generic.py` regenerates `dist/byte.js` from `swatch/byte_helper.html`, which is the source of truth for the look, the animation and the voice. After changing it, run the script and copy the new `byte.js` over the old one in each repo.
