# ROTATE engine build steps

Nov 5, 2026 (rev 2, after the deep-research check) · @sudipta das

A step-by-step order for building the ROTATE engine. Finish one step, run its "Done when" check, tick it, then start the next.

This file sequences the "Improved engine implementation plan" in `ROTATE plan verification and upgrades.md` (called "the report" below). The report overrides `ROTATE engine plan.md` wherever they differ. For parameters, field names and formulas, read the report section named in each step; this file says what to do in which order and how you know a step is finished.

## Scope

This plan covers **the engine only** (owner: Sudipta). The engine is built, tested, documented and handed to the team ("shipped"). Everything else belongs to teammates: the frontend, backend and map, the 240 s and 30 s videos, the project page and submission, the pitch, and talking to the Local Lead.

What the engine delivers:

- the `rotate_engine` Python package and its CLI;
- the fetch scripts and the cached `data/`;
- the JSON schemas and fixtures;
- the tests and the backtest;
- **an engine doc** (`docs/ENGINE.md`): method, data sources, limits, backtest verdict and the facts teammates need for the README, `DATA_SOURCES.md` and the AI disclosure;
- **an integration guide** (`docs/INTEGRATION.md`): how the backend and frontend install, call and display the engine.

Both docs are written before the hand-off (Step 17). Where a step below mentions team work (the video, the presenting laptop), the engine's part is only to hand over what that work needs.

## How to use this plan

- **Gate rule.** Do not start step N+1 until step N's "Done when" check passes.
- **Two exceptions:**
  - Step 1 submits the AppEEARS task and moves on without waiting, because tasks can sit in a queue for hours.
  - Step 3 hands the contract fixture to the frontend and backend, so they can build in parallel.
- **Time boxes.** Each step has one. When a step runs over, take its "If stuck" fallback and move on.
- **Freeze gate.** Step 12 is a hard stop before the 18:30 video. No stretch work starts before it.
- **Clock.** Asia/Dhaka. Day 1 is 13 Nov and Day 2 is 14 Nov, as the report recommends. Confirm with the Local Lead (Step 0.1), then shift the blocks if needed.

## Progress

- [x] 0.1 Ask the Local Lead (team-owned; 5 Nov answer: the hackathon has started)
- [x] 0.2 Accounts
- [x] 0.3 Read the docs (notes in `ROTATE docs notes.md`; the ORNL page is still unread and is needed by Step 13)
- [x] 0.4 Install the environment (this machine done 5 Nov in `.venv`; the presenting laptop is the team's, installed from the integration guide; command in `ROTATE docs notes.md`)
- [x] 0.5 Practise on toy data (5 Nov; one-sentence explanations in `ROTATE docs notes.md` §7; Q8 still open before reusing code)
- [x] 0.6 Team agreements (5 Nov; defaults in `ROTATE team agreements.md`; teammate names per role still to fill; rules.json columns and field names wait for Step 3 (the event has now started, so they freeze there as planned))
- [x] 1 Hour-1 checks and the AppEEARS task (5 Nov; task_id, layers, quality meanings and demo points in `ROTATE docs notes.md` §8)
- [x] 2 Repo skeleton and one live POWER call (5 Nov; local `git init` only: no commit, push or LICENSE yet. Header facts and the 1997/2015 data breaks are in `DATA_SOURCES.md`)
- [x] 3 Freeze the contract (5 Nov; `models.py` v1.0 adds `analogs.method`, `confidence.basis`, `provenance.power.api_version`, `NotCached` and `AnalogResult.season_year`, and makes `features.rain_mm` nullable (null at Anwara); the fixture is not yet sent to teammates)
- [x] 4 Fetch POWER for both sites (5 Nov: both CSVs, raw JSON and IMERG fetched. **Not committed**: the owner commits. The window before 13 Nov is covered only up to 2 Nov, so refetch on event day)
- [x] 5 Seasons and features (5 Nov: the POWER 1997/2015 breaks mean the pool starts at season 1999 and Anwara has no rain feature; see `DATA_SOURCES.md`)
- [x] 6 Analogs (5 Nov: real analog years for both sites; `ndvi_pool` is filled since the NDVI download on 5 Nov)
- [x] 7 Load and validate `rules.json` (5 Nov: **self-drafted by the engine owner with AI help, unreviewed**. Every value is quoted from 5 cited sources and the rest is null. `review_status` is `engine_draft_unreviewed` until the science translator signs it off)
- [x] 8 Confidence (5 Nov, done ahead of the Step 7 gate with the owner's OK: NDVI-based from the start. The minimal `ndvi.py` slice is QA filter, acquisition day, peak window and anomaly. Godagari uses a Feb peak window, day 33–64, pending the science translator)
- [x] 9 Card rule and cards (5 Nov: rule in `docs/ENGINE.md`; `cards` CLI; Risk gained an optional `citation_id`, still v1.0 because the contract is unshared)
- [x] 10 Tests, fixtures and offline checkpoint (5 Nov: 81 tests offline in ~8 s. Every CLI command was run in a no-network namespace; Wi-Fi off on the presenting laptop is still the team's check. Four fixtures plus both demo pairs; `docs/INTEGRATION.md` first draft. The two-farm pair differs by salt class and priorities. The priority dial alone changes cards at Anwara once a salt class is set, but not at Godagari (too few sourced water and nitrogen values); fixed presets are the fallback there. Not committed, per the owner)
- [x] 11 Bug fixes and minimal NDVI (5 Nov: 10 bugs fixed from the full code check; `ndvi` command and `ndvi_series` give the QA-filtered curve with cloud gaps, low-vegetation windows, flags and the monthly QA share; NDVI fixtures for both sites. At 8 dS/m or more, card 2 now prefers a sourced salt-tolerant option. Smoothing and the per-year views remain for Step 13)
- [ ] 12 Freeze gate and `demo-v1` hand-over (6 Nov: gate check passed: all 4 must-haves, no "best", disclaimer present. **Skipped for now: no commit or tag, per the owner.** Anwara LW shrinkage is 1.0, so its match is effectively Euclidean)
- [x] 13 Full NDVI (6 Nov: Savitzky-Golay `ndvi_smooth` beside the raw points; low-vegetation windows now use the smoothed line; `ndvi_for_years` and the `ndvi-years` CLI give one Boro season (1 Nov–31 May) per harvest year; `ndvi_years_<site>.json` fixtures. 120 tests offline. Contract kept at 1.0 (unshared), although it adds `NdviPoint.ndvi_smooth` and the `ndvi_years` schema)
- [x] 14 Backtest (6 Nov: verdict rule and protocol written into `docs/ENGINE.md` before the first run; `backtest.py`, `run_backtest`, `backtest` CLI and `backtest_<site>.json` fixtures; 130 tests offline. **Result: no demonstrable skill at either site** (SS_MSE −0.148 Anwara, −0.311 Godagari; permutation p 0.53 and 0.87). `BacktestResult` gained `decision_date`, `years` and `flagged_years`, still v1.0 because the contract is unshared. With the owner's OK, the verdict is now a warning on analogs and card sets and a Derived evidence item on every card. The confidence sentence is reworded as past examples, "not a prediction for this season". The backtest is cached per data state and never tests the decision season; 132 tests)
- [x] 15 Stretch (all 5 items; HLS fetch waits for the owner's Earthdata login). Item 1 (what-if slider) done 6 Nov: `mode: "scenario"` plus `shift` (rain %, temperature °C, RH points) on the current window's raw daily POWER; the output carries only Scenario tags, which a test checks; fixture `cards_barind_whatif_dry.json`; 142 tests. `Request.shift` and the Scenario confidence tag were added, still v1.0 because the contract is unshared. Item 3 (GWETROOT) done 6 Nov: Observed evidence labelled "model output", only where the site's rain is usable (Godagari); hidden at Anwara (same 2015 jump, recorded in `DATA_SOURCES.md`) and in a what-if; never matched; 146 tests. Item 4 (4th card) done 6 Nov: opt-in `extra_card: true`, the next-ranked candidate with new dry-season crops; `cards` now allows 3 or 4; fixture `cards_barind_four.json`; 153 tests. Item 2 (tercile scenario) done 6 Nov: `tercile: dry|normal|wet` in scenario mode; past seasons ranked by IMERG rain after the decision day up to 30 Apr; scaling fitted on all years, analogs only from the third; only Scenario tags; fixture `cards_ctg_tercile_dry.json`; 167 tests. Item 5 done 6 Nov: ORNL MYD13Q1 (Aqua) centre pixel and a MOD13Q1 9×9 window (Nov 2023 on) fetched for both sites; the window centre equals AppEEARS on all 66 dates; Aqua vs Terra r = 0.90/0.95; `aqua` and `window` options are display only (matching and backtest stay Terra); fixtures `ndvi_<site>_extras.json`; 177 tests. HLS: AppEEARS lists HLSS30/HLSL30 VI, and `scripts/submit_ndvi_hls.py` was submitted 6 Nov (task_id `1a7fe273-b13a-4d94-a0de-3c4f7565a469`, done the same day); bundle fetched into `data/ndvi/hls/` (Sentinel-2 ~600 dates per site, Landsat 648 Godagari / 298 Anwara; one tile per site; no user id in the files). HLS reader done 6 Nov: `ndvi --hls` / `ndvi_series(hls=True)` is a separate 30 m curve (Fmask drops cloud, adjacent, shadow and snow; high aerosol kept but flagged), display only; r = 0.91/0.90 with Terra; fixtures `ndvi_<site>_hls.json`; `NdviPoint.satellite` gained `hls_s30`/`hls_l30`, still v1.0 because the contract is unshared; 188 tests
- [ ] 16 Final backtest and engine freeze (6 Nov: final run on the cached data (POWER to 2 Nov) is byte-identical to the fixtures and the first run at both sites: SS_MSE −0.148 / −0.311, permutation p 0.528 / 0.871, no demonstrable skill. Numbers and both `verdict_text` strings are in `docs/ENGINE.md`; 177 tests passed then, 188 after the HLS reader. **Open:** the `engine-freeze` tag; the owner commits and tags. An event-day POWER refetch means rerunning this step)
- [ ] 17 Engine doc and integration guide (6 Nov: both docs written. `ENGINE.md` adds the method, data sources with citations, limits, Use of AI and references (9 checked against OpenAlex); the backtest rule section is unchanged. `INTEGRATION.md` is rewritten: fresh-clone install, every CLI command, the Python API, contract and versioning, UI mapping, offline run and troubleshooting. Simulated fresh clone: install, then every CLI command offline (`unshare -rn`); cards match the fixture. **Open:** the "Done when" needs a real teammate on their own machine; Step 16 (final backtest, freeze tag) is not done, so numbers are the first run. The Step 15.5 ORNL fetch has since finished, the extras fixtures are built, and all 177 tests pass. Re-checked 6 Nov after 15.5: both docs cover every listed item, including the Aqua/3×3 extras. A scratch copy of exactly the files git would commit (8.5 MB data, no `.env`), installed through the guide's `uv venv --seed` fallback, then run with no network: 177 tests pass, every CLI command runs at both sites, the unknown site gives `not_cached`, bad input exits 2, and all 7 card fixtures and both backtest fixtures match byte for byte apart from `generated_at`. Docs pass after the build finished (6 Nov): README rewritten from the stub; `docs/ENGINE_PROGRESS.md` (the plain-language build story, Steps 1–17, replaces the Step 11 `engine_progress.pdf`); `fixtures/README.md` lists all 14 fixtures; status lines, the `hls` API argument and test counts updated (188 tests). Only the teammate run is left)
- [ ] 18 Hand-off

---

## Phase 0 · Before the opening (questions, reading and setup only)

The rule comes from the Space Apps Participant FAQ, and we follow the strict reading. Before the opening, these are not allowed:

- ROTATE code;
- data pulls or AppEEARS tasks for the demo sites;
- `rules.json`;
- fixtures.

Drafting the JSON schema or a rule table is "ask first". See the report's "Pre-event checklist" for the full list.

### Step 0.1 · Ask the Local Lead (15 min to send)

- **Do:** send the 11 questions in the report's "Questions for the Local Lead" today, in writing. These are the most urgent:
  - **Q3:** the team missed the 1 Nov 240-second video. Does that affect eligibility?
  - **Q4:** the NASA form may only open at 09:00 on 14 Nov, which collides with the local 09:00 deadline. What does "submitted by 09:00" mean?
  - **Q2:** what exact time may coding and data pulls begin: the local start or the global start?
  - **Q7:** what is allowed before the event? This decides Step 0.6.
- **Done when:** the questions are sent. Save each answer when it arrives.
- **Answers so far:**
  - **5 Nov, Local Lead:** the hackathon has started, so coding may begin. This settles Q2 and Q7 for now (the strict FAQ rule no longer blocks code). The real Day 1 and Day 2 dates and deadlines are not yet confirmed.

### Step 0.2 · Accounts (15 min)

- **Do:** every team member creates an Earthdata Login and tests signing in to AppEEARS. Submit no task for ROTATE sites.
- **Done when:** every member can sign in.

### Step 0.3 · Read the docs (60 min)

- **Do:** read these:
  
  - the POWER data-sources, referencing and API pages;
  - the AppEEARS API (`/product`, `/quality`, the point-task flow, HTTP 429);
  - the ORNL MODIS subset service;
  - the scikit-learn covariance guide (LedoitWolf);
  - the pydantic JSON-schema docs;
  - requests-cache and tenacity.
  
  Also check whether scikit-learn's `.mahalanobis()` returns squared distances. The report flags that as unchecked.

- **Done when:** you have notes with links, split into two lists:
  
  - **Settled by the report:** solar starts in 1984; the NDVI layer names; the pixel-reliability meanings; the 0.0001 scale factor; POWER latency of about 2 days.
  - **To check live in Step 1–2:** the fill value; the precipitation source; the response shape; the day-of-year layer name; GWETROOT.

### Step 0.4 · Install the environment (20 min)

- **Do:** create a Python 3.12 virtual environment with:
  
  - engine: numpy, pandas, scikit-learn, pydantic;
  - tests: pytest, jsonschema;
  - fetch scripts only: requests, requests-cache, tenacity.
  
  The presenting laptop is the team's: they install from `docs/INTEGRATION.md` (Step 17).

- **Done when:** one import line for all nine libraries runs on your machine.

### Step 0.5 · Practise on toy data (60 min)

- **Do:** use random numbers, in a scratch folder outside this project:
  - z-scores;
  - the Ledoit-Wolf precision matrix, and Mahalanobis distance computed by hand from it (an exact copy of a row gives 0);
  - leave-one-out with the MSE skill score against a plain-mean baseline;
  - a permutation p-value;
  - the exact binomial chance rate for k = 5.
- **Done when:** you can explain each idea in one sentence, and your chance rates come out as 0.375 for ≥4 of 5 and 0.0625 for 5 of 5. Ask Q8 before reusing any of this code.

### Step 0.6 · Team agreements (30 min)

- **Do:** write these down:
  
  - roles;
  - git conventions: folder ownership, `main` always runs, tag before recording;
  - the cut order from report risk 18;
  - whether the backend imports Python, uses the CLI or reads static JSON;
  - who builds the cards (the default is the engine);
  - candidate demo points: a coastal salinity point in Chattogram (e.g. Anwara or Banshkhali) and a northwest Barind drought point.
  
  **Only if the Local Lead says yes to Q7:** agree the `rules.json` columns and the JSON field names now. Otherwise both freeze in Step 3.

- **Done when:** every item is written down or has a stated default.

---

## Phase 1 · Day 1, 11:30–12:30 · Checks, data requests, contract

Start nothing before the official opening. The first commit happens after it. (5 Nov: the Local Lead says the opening has happened.)

### Step 1 · Hour-1 checks and the AppEEARS task (11:30–11:50)

- **Do,** in this order:
  1. Check in imagery that both demo points sit on cropland, not a pond, river or village.
  2. AppEEARS:
     - log in;
     - read the NDVI, pixel-reliability, VI_Quality and composite day-of-year layer names from `/product/MOD13Q1.061`;
     - read the quality meanings from `/quality`.
  3. Submit **one** point task for both sites with all four layers, 01-01-2000 to today. The web form is fastest. Record the `task_id`. The token stays in `.env` or memory only.
  4. Read the Field Shift Resources tab and note any NASA products it lists.
  5. Note the latest available MOD13Q1 composite date.
- **Done when:** the task is accepted, the `task_id` is recorded, and the layer names and quality meanings are written down. **Do not wait for the task.**
- **If stuck:** submit from a teammate's account. The ORNL fallback belongs in Step 13, not now.

### Step 2 · Repo skeleton and one live POWER call (11:50–12:05)

- **Do:**
  - Set up the repo:
    - `git init` here, then push to a public GitHub repo.
    - Create the report's "Module layout": `engine/src/rotate_engine/`, `scripts/`, `data/`, `rules/`, `fixtures/`, `schemas/`.
    - Add `.gitignore` covering `.env`, `.venv`, `__pycache__`, `cache/`, plus by name `Rotate_Team_Plan_v2.docx`, `ROTATE implementation plan.pdf`, `ROTATE engine plan.pdf` and `NASA Space Apps Plan Optimization.pdf`. Never use a `*.md` pattern.
    - Add `.env.example`, `LICENSE` (Apache-2.0 or MIT; the team decides) and a stub `README.md`.
    - Keep `CLAUDE.md` and the three plan `.md` files tracked unless the team objects.
  - Make one POWER daily-point call for site 1 (curl is fine) with PRECTOTCORR, T2M_MIN, T2M_MAX, RH2M, ALLSKY_SFC_SW_DWN and GWETROOT. Save the raw JSON to `data/raw/power/`.
- **Done when:**
  - `pip install -e engine` then `python -m rotate_engine --help` works;
  - `git check-ignore .env` prints `.env`;
  - the raw POWER JSON is saved;
  - a draft `DATA_SOURCES.md` records what the header says: the precipitation source, the fill value, the version, the latest date, whether 1981–83 solar values are fill values, and whether GWETROOT exists.
- **If stuck:** if POWER refuses the call, go on to Step 3; Step 4 retries it.

### Step 3 · Freeze the contract (12:05–12:30)

This step is a gate exception: once it's done, teammates build against the fixture while you continue.

- **Do:**
  - Write `models.py`: pydantic models for CardSet, AnalogResult, NdviSeries and BacktestResult, with field names exactly as in the report's "Data contract".
    - Use `ConfigDict(extra="forbid")`.
    - Tags are `Literal["Observed","Derived","Scenario"]`.
    - Every response carries `schema_version: "1.0"`.
  - Write `config.py` with the constants: K, WINDOW_DAYS, FEATURES, the thresholds and SCHEMA_VERSION.
  - Export `schemas/*.schema.json`.
  - Hand-write `fixtures/cards_ctg.json`. Placeholder values are fine.
  - Push, and send the fixture to the frontend and backend.
- **Done when:** `test_fixtures_match_schema` passes and the teammates can render the fixture. From now on, adding an optional field bumps the version to 1.1, and renaming or removing a field bumps it to 2.0 and must be announced.
- **If stuck:** at 12:30, push whatever validates. Field names matter more than completeness.

---

## Phase 2 · Day 1, 12:30–16:30 · The engine

Check the AppEEARS task at 13:30 and 14:30. When scripting, poll at most every 30–60 s; an HTTP 429 means slow down. When the task is done, save the CSV and raw bundle into `data/ndvi/` and commit them. Cleaning comes in Steps 11 and 13.

### Step 4 · Fetch POWER for both sites (12:30–12:50)

- **Do:**
  - Write `data/sites.json` with id, name, latitude, longitude and hazard for both sites.
  - Write `scripts/fetch_power.py` as in the report's "Offline caching" section: a requests-cache session, tenacity retries, a timeout, and the raw JSON with its header saved next to the CSV.
  - Convert the header's fill value to NaN in the CSV.
  - The script prints the first and last date, the first valid year per parameter, and the missing-day counts.
- **Done when:** both CSVs and their raw JSON are committed, and you have noted whether the 60-day window before 13 Nov is covered.
- **If stuck:** download the CSV by hand from the POWER Data Access Viewer, and record the header details manually.

### Step 5 · Seasons and features (12:50–13:30)

- **Do:** write `seasons.py` and `features.py`, following report algorithm Steps 0–2:
  - the window is the 60 days ending at the last valid day before the decision date, with the same calendar window for every past year;
  - fewer than about 55 valid days means a warning and a stop;
  - Boro seasons are labelled by harvest year;
  - the default features are log1p of total rain, mean T2M_MIN and mean RH2M;
  - solar is off by default; if it is ever switched on, the pool starts in 1984;
  - extreme-day counts (Tmax ≥ 35 °C, rain ≥ 50 mm) are display evidence only, and their thresholds must be confirmed before they go on screen.
- **Done when:** the 1981–2026 feature table prints and looks sane, with skipped years listed, and these tests pass: `test_no_future_data`, `test_fill_value_becomes_nan`, `test_solar_pre1984_excluded`.
- **If stuck:** drop a year with gaps and list it. Never fill a gap.

### Step 6 · Analogs (13:30–14:30)

- **Do:** write `analogs.py`, following report algorithm Steps 3–7:
  
  - detrend temperature using the training years only;
  - compute z-scores from the training years only;
  - use the LedoitWolf precision matrix, and compute D from it yourself;
  - assert that every D is finite, and fall back to the identity matrix with a warning;
  - build `weather_pool` (k = 5, from 1981 to last year) and `ndvi_pool` (k = 5, NDVI Boro years 2001–2024 with 2025 flagged; empty with "pending" until NDVI arrives);
  - sort ties by (distance, year);
  - apply kernel weights and the `close_match` cutoff, and say "no close look-alike year" when nothing is close;
  - report the Euclidean overlap and log `shrinkage`.
  
  The core function takes the training years as an argument, so the backtest can refit per fold. Add the CLI command `analogs`.

- **Done when:** real analog years print for site 1, and these tests pass:
  
  - `test_distances_finite`, including a near-duplicate column;
  - a duplicate row has D = 0 and ranks first;
  - the identity precision matrix gives Euclidean distance on the z-scores;
  - the target year never appears in its own training set.

- **If stuck:** at 14:30, ship standardised Euclidean distance with `method: "euclidean"` and a warning. Come back to Ledoit-Wolf in the evening.

### Step 7 · Load and validate `rules.json` (14:30–14:45; the file is due 14:00)

- **Do:** write `rules.py`, which loads `rules/rules.json` through a pydantic model with `extra="forbid"`, using the report's row columns. It also loads the BRRI top-15 pattern catalogue, which the translator delivers with the rules. The catalogue fills the current-rotation dropdown and supplies candidate alternatives.
  - Every benefit has a `citation_id`.
  - `evidence_strength` is set on every row.
  - Salinity filters use whole-season values, never seedling figures.
- **Done when:** the real file validates. Send failures back to the translator with the row id.
- **Open questions for the translator.** Send these as soon as you are allowed to; never answer them yourself.
  - How does each row's columns turn into a score per priority (water, soil_n, salinity, yield_stability, income, forage)?
  - No column covers yield stability.
  - No column covers required equipment, even though equipment is a constraint.
  - Does a named variety need its own "verified" flag, or does `evidence_strength` cover it?
- **If stuck:** if no file has arrived by 14:30, ask for just the cited rows. Never write crop facts yourself.

### Step 8 · Confidence (14:45–15:00)

- **Do:** write `confidence.py`, following report algorithm Step 8. Each analog votes on the sign of its anomaly. Report:
  
  - the count;
  - the weighted agreement;
  - the exact binomial chance rate;
  - a label: high at 5/5, moderate at 4/5, split otherwise;
  - a sentence that includes the chance rate.
  
  Until NDVI arrives, vote on the analog years' observed post-decision season rainfall anomaly instead, and label the result rainfall-based.

- **Done when:** `test_chance_rate_k5` passes, and the analog output carries a confidence block tagged Derived.

### Step 9 · Card rule and cards (15:00–15:30)

- **Do:**
  - First, write the selection rule into the method section of `docs/ENGINE.md`, following report algorithm Step 9:
    - the existing rotation is card 1;
    - candidates come from the pattern catalogue plus the rule rows that fit the hazard and tolerate the farmer's salinity class over the whole season;
    - above about 8 dS/m, show a "fallow, short oilseed, or local review" card;
    - score = Σ priority_weight × attribute_score, with the breakdown shown;
    - take the top two that differ in kind;
    - the "why" sentence comes from a template;
    - every benefit has a `citation_id`, every card has `needs_local_review`, and risks are ranked.
  - Then write `cards.py` and `provenance.py`. Source labels come from the saved POWER header and are never hard-coded. Add the `disclaimer` and the `warnings`, such as "current-year weather comes from GEOS FP-IT".
  - Add the CLI command `cards --site --date --input --out`.
- **Done when:** `python -m rotate_engine cards …` writes JSON that validates against the schema, and these pass:
  - `test_three_cards_first_is_existing`;
  - `test_every_evidence_has_tag_and_source`;
  - `test_every_benefit_has_citation`;
  - a check that no card text contains "best", "should plant" or "you should".
- **If stuck:** use fixed priority presets instead of a live dial. That is the report's fallback.

### Step 10 · Tests, fixtures and offline checkpoint (15:30–16:30)

- **Do:**
  - Add `test_cards_golden` (regenerate it deliberately with `UPDATE_GOLDEN=1`) and `test_engine_runs_offline`, which monkeypatches `socket.socket`.
  - Write `scripts/build_fixtures.py`. It writes fixtures for the demo inputs:
    - the two-region pair: the salinity site and the drought site;
    - the two-farm pair: the same site and weather with different priorities.
  - Hand the engine over to the backend, with a first draft of `docs/INTEGRATION.md` (install, the CLI commands, the fixtures).
- **Checkpoint:** run every CLI command on your machine with Wi-Fi off.
- **Done when:** the full test suite passes offline in under a minute, and every CLI command works with Wi-Fi off.
- **If stuck:** at 16:15, fall back to Euclidean distance plus fixed priority presets, or have the frontend serve the static fixtures.

---

## Phase 3 · Day 1, 16:30–18:30 · Freeze

### Step 11 · Bug fixes and minimal NDVI (16:30–17:15)

- **Do:** bug fixes only. If NDVI has arrived, apply the minimal QA filter (pixel reliability 0 or 1, plus the scale factor) and draw one curve for the demo site. Otherwise show "NDVI pending".
- **Done when:** the tests are green, and the demo shows either the NDVI curve or "NDVI pending".

### Step 12 · Freeze gate and `demo-v1` hand-over (17:15–18:30)

- **Check** the engine side of the video must-haves:
  
  1. analogs: season-to-date, Ledoit-Wolf (or the Euclidean fallback), and confidence with its chance rate;
  2. three cards, with the existing rotation first;
  3. priorities and constraints change the ranking (or presets do);
  4. the NDVI series, or "NDVI pending".
  
  The output carries the "does not forecast" text, and no card text says "best".

- **Do:** tag `demo-v1` and tell the team. Recording and uploading the video is the team's job; answer their questions about the method while they do.

- **If behind,** cut in this order: Bangla narrative → slider → second site → NDVI curve → live dial (presets).

- **Done when:** `demo-v1` is tagged and the team has confirmed it runs for them. Stretch work may start only now.

---

## Phase 4 · Day 1 evening (must-haves first)

### Step 13 · Full NDVI (60 min)

- **Do:**
  - Write `ndvi.py`, following the report's "NDVI processing" items 1–7:
    - the QA filter and scale factor;
    - each value placed on its actual acquisition day;
    - gaps longer than 32 days labelled "cloud gap";
    - optional smoothing, always keeping the raw points;
    - the predictand: the Boro peak-window mean, minus the training-year trend;
    - the "low-vegetation window (bare, flooded or newly planted)" label;
    - the QA pass share per month.
  - Flag composites from 2025 onward.
  - Add `ndvi_for_years` and its CLI command.
  - Fill `ndvi_pool`, and switch confidence to NDVI-based votes.
  - If AppEEARS errored, resubmit a smaller task or run `scripts/fetch_ndvi_ornl.py`.
- **Done when:** the `ndvi_for_years` output validates, a test shows that a gap stays a marked gap, and confidence says it is NDVI-based.

### Step 14 · Backtest (must-have, 75 min)

- **First,** before running anything, write the verdict wording into `docs/ENGINE.md`: "SS > 0 and permutation p < 0.10 = some skill. Otherwise: no demonstrable skill, and the analog years are shown as historical examples only."

- **Do:** write `backtest.py`, following the report's "Backtest protocol":
  
  - leave one year out for each Boro year 2001–2024, refitting everything per fold;
  - predict the held-out year as the weighted mean of its analogs, with a climatology baseline of 0;
  - report SS_MSE, the Euclidean SS, the anomaly correlation, the tercile hit rate, the beat count with a sign test, a permutation p (1,000 runs, fixed seed), and the hit rate by agreement bin;
  - report 2025 separately.
  
  Return a `BacktestResult` and add the CLI command `backtest`.

- **Done when:** `test_backtest_refits_per_fold` passes, the first numbers exist, and `verdict_text` follows the pre-written rule, whatever the numbers say.

### Step 15 · Stretch (only after Step 14, in this order)

1. A what-if slider. It shifts the raw features, reruns report algorithm Steps 4–8, and tags every output Scenario.

2. Tercile scenario mode (dry, normal or wet).

3. GWETROOT soil wetness, labelled "model output", if Step 2 found it.

4. A 4th card.

5. MYD13Q1 interleaving, a 3×3-pixel window via ORNL, and the HLS 30 m layer.
- **Done when (each item):** its tests pass, and any scenario output carries only Scenario tags.

---

## Phase 5 · Day 2, 07:30–09:00 · Hand off

### Step 16 · Final backtest and engine freeze (07:30–07:50)

- **Do:** do the final backtest run, then tag the engine freeze. Put the numbers and `verdict_text` in `docs/ENGINE.md`.
- **Done when:** the freeze tag exists and the numbers are in the engine doc.

### Step 17 · Engine doc and integration guide (07:50–08:30)

- **Do:** write two documents in `docs/`, for teammates who did not build the engine.
  - **`ENGINE.md`** (what the engine does and what it cannot claim):
    - the method: window, features, detrending, Ledoit-Wolf distance, k = 5, kernel weights, `close_match`, confidence with its chance rate, the card rule;
    - the backtest numbers and `verdict_text`, with the verdict wording written before the first run;
    - data sources: POWER's referencing text with the real version and access date, the MOD13Q1.061 citation from the AppEEARS bundle README, source labels exactly as the header gave them, what each source was used for, and references for every library, paper and dataset (teammates turn this into `DATA_SOURCES.md`);
    - limits: the tool does not forecast; reanalysis is not field measurement; the latest days come from GEOS FP-IT (weather) and FLASHFlux (solar), named as the header gives them; the POWER cell versus the 250 m pixel (about 5–6 ha); NDVI is consistent with, but cannot diagnose, salinity stress; MODIS 2025+ is flagged and VIIRS is the successor; any skipped years; any fallback that was used;
    - AI notes: Gemini and Claude for planning and research, plus Claude Code for engine code, with representative prompts. Mahalanobis belongs under Methods, not Use of AI.
  - **`INTEGRATION.md`** (how to use it):
    - install from a fresh clone (Python 3.12, `pip install -e engine`);
    - every CLI command with an example and its output file;
    - the Python API for a Python backend: the public functions, their arguments and the pydantic models they return;
    - the JSON contract: `schemas/*.schema.json`, the `schema_version` rules (optional field → 1.1, rename or removal → 2.0), and the fixtures to build against;
    - what each part of the output is for in the UI: the five pipeline stages, the Observed/Derived/Scenario tags, `needs_local_review`, the chance-rate text, "NDVI pending", the "not cached" result, and the warnings to show;
    - wording rules the UI must keep: "compare", never "best"; no forecast claims; NASA data versus rule-table benefits kept separate;
    - running offline with Wi-Fi off, and the static-fixture fallback.
- **Done when:** a teammate follows `INTEGRATION.md` from a fresh clone on their own machine and gets cards without asking you anything.

### Step 18 · Hand-off (08:30–09:00)

- **Do:** walk the team through both docs, run the engine once on the presenting laptop with them, and fix anything the guide got wrong.
- **Done when:** the team confirms they have the engine, both docs and the final numbers. The engine work ends here; submission is the team's.

Local judging is at 11:00.
