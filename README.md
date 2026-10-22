# Seizure Watch

Free, no-API-key platform that searches open-source news every day for illegal drug seizures, extracts the facts, and flags risk indicators.

## Quick start
```
pip install -r requirements.txt
python run_daily.py --demo            # offline test with invented data -> demo output in docs/
python run_daily.py --days 30         # first real run: 30-day backfill
python run_daily.py                   # daily run (incremental)
```
Outputs (in `docs/`): `index.html` (dashboard), `events.csv`, `seizure_watch.xlsx`, `bulletin.html` / `bulletin.txt` (weekly one-page bulletin).

## Daily automation
Push this folder to a GitHub repo and enable Actions. `.github/workflows/daily.yaml` runs three times a day (05:17, 11:17 and 17:17 UTC), commits the updated database and `docs/`. Turn on GitHub Pages (branch, `/docs` folder) to get a live dashboard URL.

## Configure
Edit `config.yaml`: Google News editions/queries, GDELT queries, risk points, commodity tiers and thresholds (the dashboard has a "How risk is scored" box that stays in sync), and `rss_feeds` (add customs / police / agency feeds you trust).

## Cargo risk indicators
The score applies the news-detectable part of the Cargo Risk Indicators master list: false declaration or missing permit, front or new company, transshipment or free zone, route change, repeat vessel/container, intelligence-led finds (plus the existing concealment, container, network, route, scale and commodity signs). Dimensions are capped (method 30, network 30, route 20). `risk.watchlist` in `config.yaml` forces a matching vessel, container or term to High. Weak data is listed as "Data gaps" and never scored. Indicators are phrases in the article, never traits of a person or nationality; they justify a closer look and are not proof.

## What it flags
High-risk events (0-100 score), insider signals, new and surging corridors, and statistical spikes (drug x country, drug x origin, drug x concealment). Trend alerts stay quiet until ~42 days of history exist.

## Notes
- Only extracted facts and the article link are stored, not article text.
- Extraction is rule-based (English, Spanish, French, Portuguese, Dutch and Flemish, German (Austria and Germany), Danish, Norwegian, Swedish, Estonian, Slovak, Icelandic, Mongolian, Amharic, Arabic, Turkish, Russian, Chinese, Hindi; Vietnamese for elephant-ivory seizures only); treat output as leads to verify, not confirmed intelligence.
- Live collection was not tested in the build sandbox (no internet access to news sites); run the backfill once and check the counts.

## Languages, coverage and detail
- The dashboard's **Coverage** map shows where the tool may be blind: countries whose main language is not searched (red), quiet ones (yellow) and those with reports (green).
- Each report can carry the ports/airports, vessel name, shipping line, container number (check-digit validated) and the cover cargo, when the article names them.

### Austria, Nordic and Baltic countries, Slovakia, Ethiopia and Mongolia
German (Austria), Danish, Estonian, Amharic, Icelandic, Mongolian, Norwegian, Slovak and Swedish are collected (Google News edition, GDELT and the police and customs newsrooms in `config.yaml`) and read by `swatch/lang_more.py`, which holds the word lists in one place (drugs, seizure verbs, ports, units, concealment, chemicals, ivory, arms, heritage, stolen vehicles, risk phrases, countries, ports and cities). To add a word, add it there.
- **Good coverage:** German, Danish, Norwegian, Swedish. **Good for common words, names expanded into their inflected forms:** Estonian, Slovak, Icelandic. **Basic - the common drug, seizure and place words only; please have a native speaker extend them:** Mongolian and Amharic.
- Estonian case endings tell the direction ("Ecuadorist" = from Ecuador, "Soomesse" = to Finland); the other languages use prepositions ("fra", "från", "aus", "nach", "z", "do").
- Google News may not publish an edition for every one of these (Iceland and Mongolia in particular). The run log prints one line per edition, for example `edition IS/is: 0 headlines`; a 0 means that edition returned nothing and GDELT and the official sites carry that language. Remove an edition that stays at 0.
- YAML reads a bare `no` as the boolean false. Norwegian is therefore written `"no"` (in quotes) everywhere in `config.yaml`; keep the quotes.

## Weekly bulletin
`docs/bulletin.html` is rebuilt every run. To also e-mail it every Monday, add these GitHub secrets (Settings > Secrets and variables > Actions): `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `BULLETIN_TO` (comma-separated), optionally `BULLETIN_FROM`. Never put them in the repository (it is public).
