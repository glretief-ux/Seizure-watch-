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
Edit `config.yaml`: Google News editions/queries, GDELT queries, risk weights and thresholds, and `rss_feeds` (add customs / police / agency feeds you trust).

## What it flags
High-risk events (0-100 score), insider signals, new and surging corridors, and statistical spikes (drug x country, drug x origin, drug x concealment). Trend alerts stay quiet until ~42 days of history exist.

## Notes
- Only extracted facts and the article link are stored, not article text.
- Extraction is rule-based (English, Spanish, French, Portuguese, Arabic, Turkish, Russian, Chinese, Hindi); treat output as leads to verify, not confirmed intelligence.
- Live collection was not tested in the build sandbox (no internet access to news sites); run the backfill once and check the counts.

## Languages, coverage and detail
- The dashboard's **Coverage** map shows where the tool may be blind: countries whose main language is not searched (red), quiet ones (yellow) and those with reports (green).
- Each report can carry the ports/airports, vessel name, shipping line, container number (check-digit validated) and the cover cargo, when the article names them.

## Weekly bulletin
`docs/bulletin.html` is rebuilt every run. To also e-mail it every Monday, add these GitHub secrets (Settings > Secrets and variables > Actions): `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `BULLETIN_TO` (comma-separated), optionally `BULLETIN_FROM`. Never put them in the repository (it is public).
