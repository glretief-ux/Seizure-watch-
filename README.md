# Seizure Watch

Free, no-API-key platform that searches open-source news every day for illegal drug seizures, extracts the facts, and flags risk indicators.

## Quick start
```
pip install -r requirements.txt
python run_daily.py --demo            # offline test with invented data -> demo output in docs/
python run_daily.py --days 30         # first real run: 30-day backfill
python run_daily.py                   # daily run (incremental)
```
Outputs (in `docs/`): `index.html` (dashboard), `events.csv`, `seizure_watch.xlsx`.

## Daily automation
Push this folder to a GitHub repo and enable Actions. `.github/workflows/daily.yml` runs at 05:30 UTC, commits the updated database and `docs/`. Turn on GitHub Pages (branch, `/docs` folder) to get a live dashboard URL.

## Configure
Edit `config.yaml`: Google News editions/queries, GDELT queries, risk weights and thresholds, and `rss_feeds` (add customs / police / agency feeds you trust).

## What it flags
High-risk events (0-100 score), insider signals, new and surging corridors, and statistical spikes (drug x country, drug x origin, drug x concealment). Trend alerts stay quiet until ~42 days of history exist.

## Notes
- Only extracted facts and the article link are stored, not article text.
- Extraction is rule-based (EN/ES/FR/PT); treat output as leads to verify, not confirmed intelligence.
- Live collection was not tested in the build sandbox (no internet access to news sites); run the backfill once and check the counts.
