# Using the ROTATE engine (integration guide)

For the backend and frontend teammates, and for whoever sets up the presenting laptop. It covers installing the engine from a fresh clone, getting cards and charts out of it, and showing them without breaking the project's rules. Why the engine works the way it does is in `docs/ENGINE.md`.

- **Status:** built through Step 17, 6 Nov 2026. Engine `0.1.0`, JSON contract `1.0`. What was built and why, in plain language: `docs/ENGINE_PROGRESS.md`.
- **Demo decision date:** `2026-11-13` at both sites.
- **Questions:** Sudipta (engine owner). The goal is that you never need to ask.

## Contents

1. What the engine is
2. Install from a fresh clone
3. Command-line reference
4. Python API
5. Request fields and errors
6. The JSON contract
7. Showing the output in the UI
8. Rules the UI must keep
9. Fixtures and the static fallback
10. Running offline
11. Things to know and troubleshooting

## 1. What the engine is

A plain Python 3.12 package, `rotate_engine`, in `engine/`.

- **In:** a cached site, a decision date and the farmer's choices (current rotation, salinity class, priorities, constraints).
- **Out:** JSON. The main output is a card set with three strategy cards to compare; there are also outputs for the NDVI chart, per-year NDVI and the backtest.
- **Reads:** only local files: `data/` (POWER, NDVI, `sites.json`) and `rules/rules.json`. It never touches the network.
- **Has no:** web server, UI or database. Those are yours.

## 2. Install from a fresh clone

You need Python **3.12** (`python3.12 --version`) and git. About 2 minutes with a normal connection; after that no network is needed.

```sh
git clone <repo-url> rotate && cd rotate
python3.12 -m venv .venv
.venv/bin/pip install -e "engine[dev]"
```

If `.venv/bin/pip` does not exist after the first line (Ubuntu or Debian without the `python3.12-venv` package), delete `.venv` and create it with `uv venv --seed -p 3.12 .venv` instead, or install `python3.12-venv` and repeat.

On Windows use `py -3.12 -m venv .venv`, then `.venv\Scripts\pip` and `.venv\Scripts\python` in place of `.venv/bin/...` everywhere in this guide.

`engine[dev]` adds the test tools. A backend that only calls the engine can use `pip install -e engine`.

**Check it works** (each takes seconds):

```sh
.venv/bin/python -m pytest -q engine                 # all tests pass
.venv/bin/python -m rotate_engine sites              # lists ctg_anwara and barind_godagari
.venv/bin/python -m rotate_engine cards --site ctg_anwara --date 2026-11-13 --out cards.json
```

The last command writes `cards.json` with three cards. If you get that far, the engine works on your machine.

**What the clone must contain:** `engine/`, `data/` (POWER and NDVI, about 8 MB), `rules/rules.json`, `schemas/` and `fixtures/`. Without `data/ndvi/`, cards come back as `not_cached` ("NDVI pending").

**Where the engine looks for data:** it walks upward from its own folder until it finds `data/` and `rules/`, which works with the editable install above. If you install it another way or move it, set `ROTATE_ROOT` to the repo root:

```sh
ROTATE_ROOT=/path/to/rotate .venv/bin/python -m rotate_engine sites
```

**Not needed:** `.env` and the `scripts/` folder. Those are for the engine owner's data fetches, which need the network and an Earthdata login.

## 3. Command-line reference

Every command is `.venv/bin/python -m rotate_engine <command> ...`. JSON goes to `--out <file>`, or to the screen without `--out`. The exit code is 0 on success (including a `not_cached` result) and 2 on bad input, with the reason on stderr.

| Command | Example | Output | Schema |
|---|---|---|---|
| `sites` | `sites` | the cached sites: id, name, lat, lon, hazard (screen only) | none |
| `cards` | `cards --site ctg_anwara --date 2026-11-13 --input request.json --out cards.json` | the card set | `card_set` |
| `analogs` | `analogs --site ctg_anwara --date 2026-11-13 --out analogs.json` | the look-alike years and confidence, without cards | `analog_result` |
| `ndvi` | `ndvi --site ctg_anwara --from 2024-11-01 --to 2026-10-31 --out ndvi.json` | the greenness curve. `--from`/`--to` are optional (default: the whole record, 2000 on). Add `--aqua` and `--window` for the extras. `--hls` instead returns the separate 30 m HLS curve (Nov 2015 on); it cannot be combined with `--aqua` or `--window` | `ndvi_series` (`hls=True`) |
| `ndvi-years` | `ndvi-years --site ctg_anwara --years 2003 2015 2019 --out years.json` | one Boro-season curve (1 Nov–31 May) per harvest year. `--aqua` optional | `ndvi_years` |
| `backtest` | `backtest --site ctg_anwara --date 2026-11-13 --out backtest.json` | how the look-alike method did on past seasons, with the verdict | `backtest_result` |
| `features` | `features --site ctg_anwara --date 2026-11-13` | a debug table of window features per season (screen only) | none |
| `schemas` | `schemas --out-dir schemas` | rewrites `schemas/*.schema.json` from the code (engine owner only) | none |

`--date` defaults to today, so always pass it in the demo. `--input` is optional: without it, `cards` uses the defaults in section 5.

`request.json` holds only the farmer's choices:

```json
{"current_rotation": "boro-fallow-t_aman", "salinity_class": "slight_4_8",
 "priorities": {"salinity": 0.7, "soil_n": 0.1, "yield_stability": 0.2},
 "constraints": {"water_availability": "high"}}
```

## 4. Python API

For a Python backend: `from rotate_engine import ...`. Every function returns a pydantic model; call `.model_dump_json()` to send it, or `.model_dump(mode="json")` for a dict.

| Function | Arguments | Returns |
|---|---|---|
| `list_sites()` | none | `list[Site]` |
| `cards_for_site(site_id, decision_date, **choices)` | `choices` are the request fields in section 5 | `CardSet` or `NotCached` |
| `default_request(site_id, decision_date, **choices)` | as above | `Request` (validated, defaults filled in) |
| `build_cards(request)` | a `Request` | `CardSet` or `NotCached` |
| `find_analogs(site_id, decision_date, k=5, shift=None, tercile=None)` | `shift` is a `Shift`; `tercile` is `"dry"`, `"normal"` or `"wet"` | `AnalogResult` or `NotCached` |
| `ndvi_series(site_id, start=None, end=None, aqua=False, window=False, hls=False)` | `start`, `end` are `date`s; `hls=True` returns the separate 30 m curve and raises `ValueError` if combined with `aqua` or `window` | `NdviSeries` or `NotCached` |
| `ndvi_for_years(site_id, years, aqua=False)` | `years` is a list of Boro harvest years | `NdviYears` or `NotCached` |
| `run_backtest(site_id, decision_date, k=5)` | none besides these | `BacktestResult` or `NotCached` |

Model classes are in `rotate_engine.models` (`CardSet`, `Request`, `Shift`, `NotCached`, ...).

```python
from datetime import date
from rotate_engine import cards_for_site
from rotate_engine.models import NotCached

try:
    result = cards_for_site("ctg_anwara", date(2026, 11, 13),
                            current_rotation="boro-fallow-t_aman", salinity_class="slight_4_8",
                            priorities={"salinity": 0.7, "soil_n": 0.1, "yield_stability": 0.2},
                            constraints={"water_availability": "high"})
except ValueError as exc:          # bad input: show the message, ask the user to change it
    ...
if isinstance(result, NotCached):  # unknown site, or NDVI pending: show result.message
    ...
json_text = result.model_dump_json()
```

**Errors:** bad input raises `ValueError`. That covers pydantic's `ValidationError` (an unknown salinity class, a priority above 1), an unknown `current_rotation`, and a date with too little history. An unknown site is not an error: it returns `NotCached`.

**Speed:** the first card set for a site takes a few seconds, because it runs that site's backtest once. Later calls reuse it until a data file changes.

## 5. Request fields and errors

| Field | Allowed values |
|---|---|
| site (`--site`) | `ctg_anwara`, `barind_godagari` (see `sites`) |
| date (`--date`) | `YYYY-MM-DD`, the decision date. The demo uses `2026-11-13` |
| `current_rotation` | a `pattern_id` from `rules/rules.json` → `patterns` (28 of them, e.g. `boro-fallow-t_aman`, `fallow-fallow-t_aman`, `wheat-jute-t_aman`). Default `boro-fallow-t_aman`. Use each pattern's `name` as the dropdown label |
| `salinity_class` | `unknown` (default), `non_saline_lt2`, `very_slight_2_4`, `slight_4_8`, `moderate_8_12`, `strong_12_16`, `very_strong_gt16`. Label the selector "local information, not NASA" |
| `priorities` | `water`, `soil_n`, `salinity`, `yield_stability`, `income`, `forage`, each 0 to 1. Default: 0.25 each for the first four. A field you leave out counts as 0 |
| `constraints` | `water_availability`: `low`, `medium` (default) or `high`. `equipment` and `market`: free text, shown as gaps only |
| `extra_card` | `false` (default) or `true` for an optional 4th card: the next-ranked option whose dry-season crops differ from every card shown. It can be missing if no such option exists, so lay out for 3 or 4 |
| `mode` + `shift` (what-if slider) | `"mode": "scenario"` with `"shift": {"rain_pct": -100…200, "temp_c": -5…5, "rh_points": -30…30}` (each optional, default 0). Only this season's 60-day window weather changes before matching; past seasons stay as observed |
| `mode` + `tercile` (scenario) | `"mode": "scenario"` with `"tercile": "dry"`, `"normal"` or `"wet"`. Look-alike years come only from past seasons whose rain after the decision day up to 30 Apr fell in that third. It can be combined with `shift` |

In scenario mode every tag becomes `Scenario`, and the first warning names the change.

**Errors:**

| Case | CLI | Python |
|---|---|---|
| A wrong value, e.g. `"salinity_class": "very_salty"` | exit 2, `error: invalid input: …` | `ValueError` |
| Unknown `current_rotation` | exit 2, `error: invalid input: unknown current_rotation …` | `ValueError` |
| Unknown site | exit 0, a `not_cached` result | `NotCached` |
| Decision date before mid-2003 (fewer than 5 past seasons from 1999) | exit 2 with a clear message | `ValueError` |
| Decision date before mid-2005 (fewer than 5 NDVI years from 2001) | exit 0, `not_cached` ("NDVI pending") | `NotCached` |

## 6. The JSON contract

**Schemas:** `schemas/*.schema.json`, generated from the code. Build against them, and validate fixtures with them in your tests.

| Schema | Output |
|---|---|
| `card_set.schema.json` | `cards` |
| `analog_result.schema.json` | `analogs` |
| `ndvi_series.schema.json` | `ndvi` |
| `ndvi_years.schema.json` | `ndvi-years` |
| `backtest_result.schema.json` | `backtest` |
| `not_cached.schema.json` | any command, for an uncached site or pending NDVI |

**Versioning:** every response carries `schema_version`.
- `1.0` today. Field names are frozen.
- Adding an optional field moves it to `1.1`; your code keeps working.
- Renaming or removing a field moves it to `2.0`, and the change is announced first.
- Unknown fields are rejected on the way in (`extra="forbid"`), so a typo in a request field is an error, not silently ignored.

**Always check for `status` first.** A `not_cached` result is `{"schema_version": "1.0", "status": "not_cached", "site_id": …, "message": …}`. Show its `message`.

### Card set (`card_set.schema.json`)

| Key | What it is |
|---|---|
| `cards` | 3, or 4 when the request has `extra_card: true`. `cards[0]` is always the farmer's current rotation (`is_existing: true`). A 4th card is `alt_3`, and its `why` starts "Shown as a fourth option to compare" |
| `cards[i].strategy` | `name`, `slots` (crop ids) and `seasons` (one per slot: `rabi`, `kharif1`, `kharif2`) |
| `cards[i].why` | one sentence on why this card is shown |
| `cards[i].evidence` | items with `label`, `value`, `unit`, `source` and `tag`, plus `analog_year` when it is about one year |
| `cards[i].benefits` | from the crop rule table, each with a `citation_id` |
| `cards[i].risks` | `text`, `review_need` (high, medium or low; high first) and `citation_id` (null means a stated gap, not a claim) |
| `cards[i].gaps` | information we don't have |
| `cards[i].score_breakdown` | points per priority. **`null` means no data, not zero** |
| `cards[i].needs_local_review` | always `true` |
| `confidence` | agreement among the 5 look-alike years: `agree_count`, `chance_rate`, `label`, `basis`, `tag` and a ready `sentence` |
| `analogs` | `weather_pool` and `ndvi_pool` (the look-alike years), `method`, `shrinkage` and `euclid_overlap` |
| `window` | the 60 days of weather used for matching |
| `ndvi_status` | `ok` in every card set today (without NDVI there are no cards). `partial` and `pending` are reserved in the contract |
| `warnings` | text that must be shown (section 8) |
| `provenance` | the exact POWER request and the NDVI task and file hash, for the data sources page |
| `disclaimer` | the standard sentence |
| `request`, `site`, `engine_version`, `generated_at` | echo and bookkeeping |

### NDVI curve (`ndvi_series.schema.json`)

| Key | What it is |
|---|---|
| `status` | `ok`, or `pending` (no NDVI for this site or range): then show "NDVI pending" |
| `points` | `date` (the day the satellite took it), `ndvi` (raw), `ndvi_smooth` (Savitzky-Golay line; `null` where a gap-free stretch has fewer than 5 points), `reliability` (0 good, 1 marginal; for HLS 0 clear, 1 high aerosol), `flagged` and `satellite` (`terra`, `aqua` with `--aqua`, or `hls_s30` / `hls_l30` in the `--hls` curve) |
| `gaps` | spans of more than 32 days with no usable point, each labelled "cloud gap" |
| `low_veg_windows` | at least 2 points in a row below 0.3 on the smoothed line (raw where there is no smoothed value), labelled "low-vegetation window (bare, flooded or newly planted)" |
| `qa_pass_share_by_month` | the share of composites per month ("01" to "12") that passed quality checks. June–August is low because of monsoon cloud |
| `window_3x3` | only with `--window`: per composite from Nov 2023, the mean, min and max NDVI of the QA-passed pixels in the 3×3 block (about 700 m) around the point, plus `n_ok` |
| `tag` | always `Observed` |

**Per-year curves** (`ndvi_years.schema.json`) return `years`: one entry per Boro harvest year, 1 Nov of the year before to 31 May. Each has `points`, `gaps` and `low_veg_windows` as above, plus `status`: `ok`, `flagged` (the season reaches into 2025 or later, after the orbit drift) or `missing` (no usable NDVI that season: say so and draw nothing). Use it for the years in `analogs.ndvi_pool`.

### Backtest (`backtest_result.schema.json`)

- `verdict_text`: show it word for word wherever the look-alike years or the confidence appear. Today, at both sites, it says "No demonstrable skill … The analog years are shown as historical examples only."
- `ss_mse`, `ss_mse_euclid`, `permutation_p`, `anomaly_corr`, `tercile_hit_rate`, `beat_clim_count`, `calibration_bins`: the numbers behind it, for a methods or "how good is this?" panel.
- `years`: one row per tested season (truth, prediction, analog years), for an optional chart.
- `flagged_years`: 2025 onward, reported separately and never scored.

## 7. Showing the output in the UI

Keep the five pipeline stages visually distinct. Each part of the output belongs to one stage:

| Stage | Show from |
|---|---|
| 1. NASA observation | evidence with `tag: "Observed"`; the NDVI chart (`ndvi`, `ndvi-years`); `window`; source labels from `evidence[].source` and `provenance` |
| 2. Local information (not NASA) | the salinity class the user picked; benefits and risks with their rule-table citations; season labels from `rules/rules.json` → `seasons.defs` |
| 3. Farmer priorities and constraints | the request's `priorities` and `constraints`; each card's `score_breakdown` |
| 4. ROTATE's reasoning | `analogs`, `confidence.sentence`, evidence with `tag: "Derived"`, the backtest verdict |
| 5. Output | the three (or four) cards |

**Suggested card layout:** strategy name with its season labels → `why` → evidence (grouped by tag) → benefits (with citation) → risks (high first) → information gaps → score breakdown → the "needs local review" flag.

**NDVI chart, drawn honestly:**
- Plot the raw points and break the line at every gap. Never draw across a gap or fill it in.
- The smoothed line is optional. If you draw it, always draw the raw points with it, and leave it out where `ndvi_smooth` is `null`.
- Show `flagged` points differently, for example hollow. They are marginal-quality points, or from 2025 on, when the satellite's orbit drifted.
- Aqua points (`satellite: "aqua"`) get a different marker. They are for display only.
- `window_3x3` can be a band behind the curve to show how much neighbouring land differs.
- Title it "Vegetation in the area around this field (250 m)".
- The HLS curve (`--hls`) is a **separate chart or toggle**, titled "Vegetation around this field (30 m pixel, about 0.09 ha)". Never draw it on the same line as the 250 m curve. Name its source as HLS (Harmonized Landsat Sentinel-2) via AppEEARS, never Landsat or Sentinel-2 on their own. Most of its points are `flagged` for haze, so hollow markers will be common; that is expected. It starts in Nov 2015.

## 8. Rules the UI must keep

These come from the project rules, and judges will look for them.

1. **The disclaimer on every screen:** show `disclaimer`. It includes "does not forecast the season" and "does not replace local agricultural advice".
2. **Tags on all evidence:** colour or label every evidence item by its `tag`.
   - `Observed` means NASA values.
   - `Derived` means something ROTATE computed.
   - `Scenario` means what-if output. In scenario mode every evidence item and the confidence are `Scenario`, every evidence label starts "What-if: ", and the first warning names the change. Show the whole card set as a what-if, for example with a banner, and never next to observed cards without that label.
   - Benefits and risks come from the cited rule table. Never give them a NASA tag.
3. **"Needs local review" on every card:** `needs_local_review` is always true, so show the flag.
4. **Benefits with their citation:** look up `citation_id` in `rules/rules.json` → `citations` and show the reference, or link `url`.
5. **The chance rate with every confidence label:** never show "moderate" or "high" alone. Show `confidence.sentence`, which already contains the chance rate and ends with "These are past examples, not a prediction for this season." Keep that ending. Every card's evidence also carries a Derived item, "How the look-alike method did on past seasons", whose value is the backtest verdict.
6. **Null scores shown as "no data",** not as 0 or as an empty bar.
7. **Season labels:** use `rules/rules.json` → `seasons.defs`, for example "Rabi (winter, Boro season), mid-November to mid-March".
8. **Wording:** use "compare" and "explore". Never "best", "recommended" or "you should plant". Card text from the engine already follows this; keep it that way in your own text.
9. **Every warning shown,** in a visible notice area. Today they include:
   - the backtest verdict ("Backtest: No demonstrable skill … shown as historical examples only");
   - that the crop rule table is an unreviewed draft;
   - that look-alike years run from 1999 because of a POWER data break;
   - that Anwara matches without rain, and shows no soil wetness;
   - in a what-if at Godagari, that soil wetness is not shown;
   - the near-real-time POWER sources;
   - how old the matching window is, when it ends more than 7 days before the decision date;
   - that the extreme-day thresholds (35 °C, 50 mm) are working values pending review;
   - the Godagari NDVI peak window.
10. **NDVI wording:**
    - say "vegetation in the area around this field (250 m)", not "your field";
    - low greenness is a "low-vegetation window (bare, flooded or newly planted)", never "bare field";
    - NDVI is consistent with salinity stress but cannot diagnose it.
11. **Data source labels:** use the `source` strings as given. They name POWER's sources exactly as its response header lists them and say "reanalysis/model output, not field measurement". Don't shorten them to "MERRA-2".
12. **A "limits of this data" panel:** its content is the "Limits" section of `docs/ENGINE.md`.
13. **The footer:** "Uses NASA data. Not endorsed by NASA." No NASA or Space Apps logos.
14. **The five stages kept visually distinct** (section 7).

## 9. Fixtures and the static fallback

Ready-made engine output for the demo and for building the UI without the engine. They are real engine output, built by `scripts/build_fixtures.py` from `fixtures/requests/demo_requests.json`, and a test fails if they go stale.

| File | What it shows |
|---|---|
| `cards_ctg.json` | Anwara (coastal salinity), salt class 4–8 dS/m, salinity first, water available |
| `cards_ctg_farm_a.json` | Anwara, same weather, but no salt problem, water first, little water |
| `cards_barind.json` | Godagari (Barind drought), water first, little water |
| `cards_ctg_high_salinity.json` | Anwara at 8–12 dS/m: card 2 is salt-tolerant Boro (sourced tolerance 8 dS/m); card 3 is "Fallow, short oilseed, or local review" |
| `cards_ctg_tercile_dry.json` | tercile scenario on `cards_ctg`: look-alike years only from past seasons that turned out dry. All tags are Scenario |
| `cards_barind_four.json` | `cards_barind` with the optional 4th card (Maize–Fallow–T.Aman) |
| `cards_barind_whatif_dry.json` | what-if on `cards_barind`: this season's window with half the rain and 1.5 °C warmer. All tags are Scenario |
| `ndvi_ctg_anwara.json`, `ndvi_barind_godagari.json` | the full greenness curve for each site, 2000–2026 |
| `ndvi_<site>_extras.json` | Terra + Aqua points and the 3×3 spread from Nov 2023 (Anwara 114 points and 58 windows, Godagari 97 and 47) |
| `ndvi_<site>_hls.json` | the separate 30 m HLS curve, Nov 2015 to Oct 2026 (Anwara 421 points, Godagari 580) |
| `ndvi_years_ctg_anwara.json`, `ndvi_years_barind_godagari.json` | the Boro-season curves of each site's 5 NDVI look-alike years for 13 Nov 2026 |
| `backtest_ctg_anwara.json`, `backtest_barind_godagari.json` | the leave-one-year-out backtest for 13 Nov, with the verdict |

**Demo pairs:**
- **Two farms, same weather:** `cards_ctg_farm_a.json` against `cards_ctg.json`. Same look-alike years, different cards 2 and 3.
- **Two regions, two hazards:** `cards_ctg.json` against `cards_barind.json`.

**Static fallback:** if the engine can't run on the day, serve these files as they are. Ship `rules/rules.json` with them, because the citation texts and season labels the cards point to live there. The fallback order is: live engine → files written earlier by the CLI → `fixtures/`.

## 10. Running offline

The demo runs on the presenting laptop with Wi-Fi off. The engine needs no network after install, so the only things to check are your own parts (fonts, map tiles, scripts loaded from a CDN).

**Rehearsal on the presenting laptop:**
1. Install as in section 2 while online, and run the checks.
2. Turn Wi-Fi off.
3. Run `cards` for both sites and both demo pairs, then the whole UI, end to end.
4. Anything that fails now must be bundled locally or replaced by a fixture.

On Linux you can also run any command in a namespace with no network: `unshare -rn .venv/bin/python -m rotate_engine cards --site ctg_anwara --date 2026-11-13 --out cards.json`.

## 11. Things to know and troubleshooting

- **Restarts aren't needed after data updates:** the engine re-reads `data/raw/` and `rules/rules.json` when they change on disk, so a backend that runs all day picks up a POWER refetch or a rules edit.
- **What the priority dial does today:**
  - At Anwara, once a salt class is set, it changes cards 2 and 3 (water-first gives mungbean and wheat; salinity-first gives soybean and salt-tolerant Boro).
  - At Godagari, realistic mixes give the same cards, because few crops in the rule table have water or nitrogen figures yet. Until the science translator fills more values, fixed presets are the safer demo there.
- **The crop rule table is a draft.** It hasn't been reviewed by the science translator yet. Expect card text to change, but not field names.
- **The decision date:** POWER data currently ends on 2 Nov 2026, and the engine warns how old the window is. The engine owner refetches POWER on event day and rebuilds the fixtures (Step 16).
- **Field names are frozen at v1.0.** If one ever changes, the version goes to 2.0 and the change is announced.

| Symptom | Cause and fix |
|---|---|
| `No module named rotate_engine` | the venv isn't used or the install was skipped: run `.venv/bin/pip install -e "engine[dev]"` from the repo root |
| `requires a different Python` during install | not Python 3.12: recreate the venv with `python3.12` |
| every site is `not_cached` | the engine can't find `data/`: set `ROTATE_ROOT` to the repo root |
| `not_cached` with "NDVI pending" | `data/ndvi/` is missing from the clone, or the date is before mid-2005 |
| exit code 2, `invalid input` | a request value outside section 5; the message names the field |
| a test says a fixture or schema is stale | data or code changed after the last rebuild: tell the engine owner (it is a rebuild, not a bug) |
