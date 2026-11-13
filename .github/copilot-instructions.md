# Copilot instructions for ROTATE

## Repository scope

ROTATE is a NASA Space Apps prototype for exploring crop-rotation options in Bangladesh under changing rainfall, heat, and salinity. Keep scientific wording conservative: the product compares historical examples and supports local agricultural expertise; it does not forecast the season, measure a field, diagnose salinity, or claim that NASA data shows how a rotation performed.

The repository contains two related surfaces:

- `engine/` is the authoritative offline Python engine. It reads cached files from `data/` and `rules/rules.json`, returns Pydantic models, and exposes the `python -m rotate_engine` CLI.
- `rotate_main_app/` is a separate demonstration React/Vite frontend and Express API using mock data. It is not yet wired to the Python engine.

Network access belongs in `scripts/` only. Do not add network clients to `engine/`; the offline demo must work with Wi-Fi disabled. Earthdata credentials belong in `.env`, never in source or fixtures.

## Setup, tests, and checks

Run commands from the repository root with the Python 3.12 virtual environment:

```sh
.venv/bin/pip install -e "engine[dev]"
.venv/bin/python -m pytest -q engine
```

Run one test file, one test function, or a focused test selection with pytest:

```sh
.venv/bin/python -m pytest -q engine/tests/test_cards.py
.venv/bin/python -m pytest -q engine/tests/test_cards.py::test_name
.venv/bin/python -m pytest -q engine -k golden
```

There is no repository-wide Python lint command. The frontend has its own commands:

```sh
cd rotate_main_app/server && npm install && npm start
cd rotate_main_app/client && npm install && npm run dev
cd rotate_main_app/client && npm run build
cd rotate_main_app/client && npm run lint
```

Useful engine commands:

```sh
.venv/bin/python -m rotate_engine sites
.venv/bin/python -m rotate_engine features --site ctg_anwara --date 2026-11-13
.venv/bin/python -m rotate_engine analogs --site ctg_anwara --date 2026-11-13 --out analogs.json
.venv/bin/python -m rotate_engine cards --site ctg_anwara --date 2026-11-13 --input request.json --out cards.json
.venv/bin/python -m rotate_engine ndvi --site ctg_anwara --out ndvi.json
.venv/bin/python -m rotate_engine backtest --site ctg_anwara --date 2026-11-13 --out backtest.json
.venv/bin/python -m rotate_engine schemas --out-dir schemas
.venv/bin/python scripts/build_fixtures.py
```

After changing `models.py`, regenerate `schemas/`. After changing engine code, cached data, or rules, regenerate fixtures with `scripts/build_fixtures.py`. The golden card fixture is intentionally updated only with `UPDATE_GOLDEN=1`.

The fetch scripts are the only networked workflows:

```sh
.venv/bin/python scripts/fetch_power.py
.venv/bin/python scripts/fetch_ndvi_appeears.py
```

## Architecture

The engine pipeline is assembled in `engine/src/rotate_engine/pipeline.py`:

1. `io.py` locates the repository (or `ROTATE_ROOT`) and loads cached site, POWER, NDVI, ORNL, HLS, and rules data.
2. `seasons.py` defines the Boro season and the 60-day window immediately before the decision date; missing days are not filled.
3. `features.py` builds season-level weather features. Site configuration in `data/sites.json` controls matching features.
4. `analogs.py` detrends temperature, standardizes using training years only, fits Ledoit-Wolf precision, and selects five weighted analog years. Euclidean distance is the explicit robustness/fallback method.
5. `ndvi.py` performs MODIS/HLS quality filtering, acquisition-date placement, gap handling, smoothing, and low-vegetation-window detection. `confidence.py` turns analog NDVI anomalies into agreement and chance-rate language.
6. `cards.py` scores patterns from `rules/rules.json` against farmer priorities and constraints, always keeping the existing rotation first and adding two alternatives (or an explicitly requested fourth card).
7. `backtest.py` evaluates the method leave-one-year-out and reports MSE skill score, Euclidean comparison, permutation/sign tests, and the fixed verdict wording.
8. `models.py` defines the strict JSON contract. CLI output and public Python results use these Pydantic models; `schemas/` is generated from them.

The UI/API demo is independent: `rotate_main_app/server/server.js` mounts route modules and controllers over in-memory/demo data, while `rotate_main_app/client/src/App.jsx` defines lazy-loaded pages and `src/services/api.js` is the single fetch wrapper. Keep the frontend's mock-data limitation visible when changing that surface.

## Repository-specific conventions

- Treat `docs/ENGINE.md` and the research-verified implementation plan in `Plan/` as the method authority. Keep `docs/ENGINE_PROGRESS.md` synchronized with build-step status.
- Preserve the JSON contract rules in `models.py`: `schema_version` is present on every response, models forbid extra fields, and evidence tags are exactly `Observed`, `Derived`, or `Scenario`. Optional additions are contract changes; renames/removals require a major version.
- POWER fill values and precipitation source labels come from each raw response header. Convert fill values to missing values before feature calculations; never hard-code a source as “MERRA-2”.
- Analog fitting must avoid leakage: detrending, z-scores, covariance, and precision are fit on training seasons only and refit for every backtest fold. Keep `k=5` fixed.
- Use only whole-season salinity tolerance for card filtering; never substitute seedling tolerance. Benefits and risks come from cited entries in `rules/rules.json`, not from NASA evidence.
- Keep NASA observations, local inputs, ROTATE-derived reasoning, and scenario values visibly distinct. What-if and tercile outputs must be marked `Scenario`; low NDVI means a low-vegetation window and is not a salinity diagnosis.
- Preserve explicit “not cached”/“NDVI pending” behavior for missing inputs rather than silently substituting data. The engine is designed to run offline.
- Do not use MinCovDet, covariance pseudo-inverse shortcuts, solar as a default matching feature, or both Tmax and Tmin together. Extreme-day counts and soil wetness are display evidence, not default matching features.
- Keep generated outputs and citations consistent with the committed data. Changes to `data/`, `rules/rules.json`, or algorithm parameters may require fixture, schema, documentation, and golden-file updates together.
