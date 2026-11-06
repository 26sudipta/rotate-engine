# Fixtures

Real engine output for the demo decision date, 13 Nov 2026. `python scripts/build_fixtures.py` regenerates them; the card sets come from the requests in `requests/demo_requests.json`. A test fails when these files are out of date.

| File | What it shows |
|---|---|
| `cards_ctg.json` | Anwara (coastal salinity), salt class 4–8 dS/m, salinity first, water available |
| `cards_ctg_farm_a.json` | Anwara, same weather, no salt problem, water first, little water |
| `cards_barind.json` | Godagari (Barind drought), water first, little water |
| `cards_ctg_high_salinity.json` | Anwara at 8–12 dS/m: card 2 is salt-tolerant Boro; card 3 is "Fallow, short oilseed, or local review" |
| `cards_ctg_tercile_dry.json` | tercile scenario on `cards_ctg`: look-alike years only from past seasons that turned out dry (Scenario tags) |
| `cards_barind_four.json` | `cards_barind` with the optional 4th card |
| `cards_barind_whatif_dry.json` | what-if on `cards_barind`: half the rain and 1.5 °C warmer in this season's window (Scenario tags) |
| `ndvi_<site>.json` | the full 250 m greenness curve, 2000–2026 |
| `ndvi_<site>_extras.json` | Terra plus Aqua points and the 3×3-pixel spread from Nov 2023 |
| `ndvi_<site>_hls.json` | the separate 30 m HLS curve, Nov 2015 on |
| `ndvi_years_<site>.json` | the Boro-season curves of the site's 5 NDVI look-alike years |
| `backtest_<site>.json` | the leave-one-year-out backtest, with its verdict |

`<site>` is `ctg_anwara` or `barind_godagari`.

**Demo pairs:**
- **Two farms, same weather:** `cards_ctg_farm_a.json` against `cards_ctg.json`.
- **Two regions, two hazards:** `cards_ctg.json` against `cards_barind.json`.

How to read and show them: `docs/INTEGRATION.md`, sections 6–9.
