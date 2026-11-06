# ROTATE

Explore and compare crop-rotation strategies for Bangladeshi farms under changing rainfall, heat and soil salinity, using NASA POWER and MODIS data. NASA Space Apps Challenge 2026 (Chattogram), "Field Shift: Adapting Farms with NASA Data".

ROTATE supports, and does not replace, local agricultural expertise. It does not forecast the season.

## What it does

For a farm site, a decision date and the farmer's choices (current rotation, soil salinity class, priorities, water availability), ROTATE:

1. finds the 5 past Boro seasons whose 60 days before the decision date looked most like this season's (NASA POWER weather, Mahalanobis distance with a Ledoit-Wolf covariance);
2. shows what the vegetation did in those seasons (MODIS NDVI, 250 m);
3. lays out three rotations to compare: the farmer's own and two alternatives, with benefits and risks taken only from a cited crop rule table;
4. says how often the look-alike seasons agree, alongside how often random seasons would agree that much;
5. reports a leave-one-year-out backtest of the method. At both demo sites it found **no demonstrable skill**, so the look-alike seasons are shown as historical examples only.

Every card carries a "needs local review" flag, and every evidence item is tagged Observed (NASA values), Derived (computed by ROTATE) or Scenario (what-if).

## This repository

This repo holds **the engine**: a plain Python 3.12 package with a command line. It has no web server and no UI; those are built by the rest of the team on top of its JSON output. The engine reads only cached files, so it runs with no network.

| Path | What |
|---|---|
| `engine/` | the `rotate_engine` package and its tests |
| `scripts/` | data fetching (the only code that uses the network) and the fixture builder |
| `data/` | cached POWER and NDVI data for the two demo sites |
| `rules/rules.json` | the cited crop rule table (a draft awaiting expert review) |
| `schemas/` | the JSON contract (v1.0) |
| `fixtures/` | ready-made engine output for the demo and the UI |
| `docs/` | the engine documentation (below) |
| `Plan/` | planning documents and the build checklist |

**Demo sites:** Anwara, Chattogram (coastal salinity) and Godagari, Rajshahi (Barind drought).

## Quick start

You need Python 3.12.

```sh
python3.12 -m venv .venv
.venv/bin/pip install -e "engine[dev]"
.venv/bin/python -m pytest -q engine
.venv/bin/python -m rotate_engine sites
.venv/bin/python -m rotate_engine cards --site ctg_anwara --date 2026-11-13 --out cards.json
```

Every command, the request fields and the Python API are in [docs/INTEGRATION.md](docs/INTEGRATION.md).

## Documentation

| Read | For |
|---|---|
| [docs/ENGINE_PROGRESS.md](docs/ENGINE_PROGRESS.md) | the plain-language story: what was built, step by step, and why |
| [docs/ENGINE.md](docs/ENGINE.md) | the method, the backtest, data sources, limits, Use of AI and references |
| [docs/INTEGRATION.md](docs/INTEGRATION.md) | installing and calling the engine, and showing its output in the UI |
| [DATA_SOURCES.md](DATA_SOURCES.md) | every NASA data source, its version, access date and use, and the data breaks found |
| [fixtures/README.md](fixtures/README.md) | the demo outputs |
| [docs/rules_json_guide.pdf](docs/rules_json_guide.pdf) | how the crop rule table works |

## Data

- **NASA POWER** Daily API v2.10.2 (accessed 2026-11-05).
- **MODIS Terra MOD13Q1.061** via AppEEARS.
- For display only: **MODIS Aqua MYD13Q1.061** and a 3×3-pixel window via ORNL DAAC, and **HLS** 30 m NDVI via AppEEARS.

Citations and details are in [DATA_SOURCES.md](DATA_SOURCES.md). POWER values are reanalysis and model output, not field measurement.

## Use of AI

Google Gemini and Claude were used for planning and research. Claude also helped draft the crop rule table from the cited papers, with each value checked against its source. Claude Code wrote the engine code, tests and docs under the engine owner's direction. The product itself contains no language model. Details: [docs/ENGINE.md → Use of AI](docs/ENGINE.md#use-of-ai).

## Licence

To be added (Apache-2.0 or MIT, the team's choice).

Uses NASA data. Not endorsed by NASA.
