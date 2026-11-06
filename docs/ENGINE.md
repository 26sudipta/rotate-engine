# ROTATE engine

What the engine does, how, and what it cannot claim. Written for teammates who did not build it: the frontend and backend builders, the storyteller (who turns the sources below into `DATA_SOURCES.md` and the project page) and anyone answering judges' questions. How to install and call it is in `docs/INTEGRATION.md`.

- **Status:** built through Step 17, 6 Nov 2026 (all must-haves and all five stretch items; 188 tests pass offline). Engine version `0.1.0`, JSON contract `1.0`. The plain-language build story is `docs/ENGINE_PROGRESS.md`.
- **Demo decision date:** 13 Nov 2026, with POWER data up to 2 Nov 2026. The numbers below are from that state. The final backtest (Step 16, 6 Nov 2026) gave the same numbers as the first run. The `engine-freeze` tag is still to be made, after the first commit. A POWER refetch on event day means rerunning Step 16.
- **Owner:** Sudipta (engine). The crop rule table still awaits the science translator's review.

## Contents

1. What the engine claims, and what it does not
2. Pipeline
3. Method: look-alike (analog) years
4. How the three cards are chosen
5. Backtest
6. Stretch modes and extra NDVI sources
7. Data sources
8. Limits of this data and method
9. Roadmap: the whole country, any point
10. Use of AI
11. References

## What the engine claims, and what it does not

**It does:**
- find the past Boro seasons whose 60 days before the decision date looked most like this season's 60 days (NASA POWER weather);
- show what the vegetation (MODIS NDVI, 250 m) did in those past seasons;
- lay out three rotation options to compare (the farmer's own plus two alternatives), with benefits and risks taken only from a cited crop rule table;
- say how often the look-alike years agree, with the rate at which random years would agree as often;
- report, in every output, a backtest of whether the look-alike years would have predicted past seasons. Today the answer is no (see "Backtest").

**It does not:**
- forecast the coming season;
- say how a rotation performed: NASA data gives observed conditions and vegetation response, never rotation outcomes;
- measure the farmer's field: POWER is reanalysis or model output for a grid cell, and NDVI is one 250 m pixel around the point;
- diagnose salinity: low NDVI is consistent with salt stress, but also with bare, flooded or newly planted land;
- rank one option as "best" or tell anyone what to plant. Every card says it needs local review.

## Pipeline

The five stages below are what the UI keeps visually distinct. The engine labels its output so each item can be placed in one stage.

| Stage | What it is | Where it is in the output |
|---|---|---|
| 1. NASA observation | POWER daily weather, MODIS NDVI. Not modelled by ROTATE | evidence items tagged `Observed`; `window`; the `ndvi` and `ndvi-years` outputs; `provenance` |
| 2. Local information (not NASA) | salinity class chosen by the user; crop traits and patterns from `rules/rules.json` | `request.salinity_class`; `benefits` and `risks`, each with a `citation_id` |
| 3. Farmer priorities and constraints | the priority dial and the water, equipment and market constraints | `request.priorities`, `request.constraints`; `score_breakdown` |
| 4. ROTATE's reasoning | look-alike matching, agreement, backtest, scoring | `analogs`, `confidence`, evidence tagged `Derived`; the `backtest` output |
| 5. Output | three cards to compare (four on request) | `cards` |

In a what-if or tercile scenario every evidence item and the confidence are tagged `Scenario` instead.

## Method: look-alike (analog) years

The method is analog-year matching (Lorenz 1969): compare the weeks before the decision with the same weeks in past years, then look at what followed in the closest years. It is a transparent statistical method with fixed settings, not a trained model. All settings are in `engine/src/rotate_engine/config.py`.

### Seasons and the decision window

- **Season label:** a Boro season is named by its harvest year. A decision from July onward belongs to next year's season, so 13 Nov 2026 is Boro 2027.
- **Window:** the 60 days ending at the last day before the decision date on which all matching parameters are present. For 13 Nov 2026 that is 4 Sep–2 Nov 2026.
- **Stale window:** if the window ends more than 7 days before the decision date, a warning says so and asks for a POWER refetch. Today it ends 11 days before.
- **Too few days:** fewer than 55 valid days in the window stops the run with a clear error. Missing days are never filled: features use the valid days only.
- **Past years:** the same calendar window in every earlier season (29 Feb becomes 28 Feb). A past season with fewer than 55 valid days is skipped and listed in a warning. None are skipped today.
- **Pool:** past seasons from Boro 1999 up to the season before the decision. POWER humidity, temperature and rain step in 1997 at both sites (see "Data sources"), so earlier years are not comparable. At least 5 past seasons are needed, which rules out decision dates before mid-2003.

### Matching features

| Feature | From POWER | Used at |
|---|---|---|
| `rain_log1p`: log(1 + 60-day total rain, mm) | `PRECTOTCORR` | Godagari only |
| `tmin_c`: mean daily minimum temperature, °C | `T2M_MIN` | both sites |
| `rh_pct`: mean relative humidity, % | `RH2M` | both sites |

- **Anwara has no rain feature.** Its POWER rain is not credible from 2015 on (2–4 times IMERG, single days up to 663 mm), so it is neither matched nor shown (`match_features` in `data/sites.json`).
- **Left out on purpose:** solar radiation (it starts only in 1984 and is not needed) and maximum temperature (never both Tmax and Tmin, which are strongly correlated).
- **Display only, never matched:** counts of hot days (Tmax ≥ 35 °C) and heavy-rain days (≥ 50 mm), and root-zone soil wetness. The two thresholds are working values awaiting the science translator.

### Distance

For each target season, using the training (past) seasons only:

1. **Detrend** `tmin_c` with a straight line fitted on the training seasons, to take out warming. Rain and humidity are not detrended.
2. **Standardise** each feature with the training seasons' mean and standard deviation (z-scores).
3. **Covariance:** fit `sklearn.covariance.LedoitWolf` on the training z-scores. Ledoit-Wolf shrinks the sample covariance towards a scaled identity, which keeps it well-conditioned with about 25 seasons and 2–3 features (Ledoit & Wolf 2004).
4. **Distance:** the Mahalanobis distance (Mahalanobis 1936), computed by hand from the fitted precision matrix: D = √(dᵀ P d), where d is the difference in z-scores.

The target season never enters its own fit, and the backtest refits all four steps in every fold, so nothing leaks from the year being tested.

- **Shrinkage today:** 1.0 at Anwara, which makes its distance identical to standardised Euclidean distance; 0.27 at Godagari. The output reports it in `analogs.shrinkage`.
- **Robustness check:** standardised Euclidean distance (identity precision) is run beside it. `analogs.euclid_overlap` says how many of the 5 years both methods pick (5 of 5 at Anwara, 4 of 5 at Godagari today).
- **Emergency fallback:** if any Ledoit-Wolf distance is not finite, the engine uses standardised Euclidean distance, sets `analogs.method` to `euclidean` and adds a warning. This has not happened on the demo data.
- **Not used:** MinCovDet, because it down-weights exactly the extreme years we want to find; and a pseudo-inverse of the plain covariance.

### Choosing and weighting the 5 years

- **k = 5,** fixed before any result was seen. Ties are broken by the earlier year.
- **Kernel weights:** w = exp(−D² / 2h²), with h the median distance of the 5, normalised to sum to 1. Closer years count more in the weighted agreement and in the backtest prediction.
- **`close_match`:** true when D is within the 95% chi-square cutoff for the number of features, √χ²₀.₉₅(p) (2.45 for 2 features, 2.80 for 3). If even the nearest year is outside it, a warning says there is no close look-alike year this time.

### Two pools

| Pool | Drawn from | Used for |
|---|---|---|
| `weather_pool` | every past season from 1999 | the "look-alike years (weather)" evidence |
| `ndvi_pool` | past seasons with Boro harvest years 2001–2024 and a peak NDVI value | greenness evidence, confidence, backtest |

Each pool fits its own detrending, scaling and covariance on its own years. 2025 onward is left out of the NDVI pool because of the Terra orbit drift.

### Greenness in the look-alike years (NDVI)

- **Product:** MODIS Terra MOD13Q1.061, 16-day composites at 250 m, read from the AppEEARS point extraction.
- **Quality filter:** keep pixel reliability 0 (good) and 1 (marginal); drop the fill value (−3000). Reliability 1 points and anything from 2025 on are marked `flagged`.
- **Date:** each point is placed on its actual acquisition day (from the composite day-of-year layer), not the composite start.
- **Peak value:** the mean NDVI of the points acquired in the site's peak window, per harvest year. Anwara uses day 81–112 (mid-March to mid-April, the Boro peak reported for MOD13Q1 in Bangladesh by Mosleh & Hassan 2014). Godagari uses day 33–64 (February), where its curve actually peaks; the crop behind that peak still needs the science translator's check, and a warning says so.
- **Anomaly:** the peak value minus a straight-line trend fitted on the pool's training years.
- **Curve for the chart:** cloud gaps longer than 32 days break the line and are never filled. An optional Savitzky-Golay line (window 5, order 2; Savitzky & Golay 1964) is fitted only inside gap-free runs, always next to the raw points. "Low-vegetation windows" are 2 or more points in a row below 0.3, a working threshold.

### Confidence

- **Vote:** each of the 5 NDVI look-alike years votes on whether its peak greenness was above or below its trend. `agree_count` is the size of the majority (3, 4 or 5).
- **Chance rate:** the exact binomial probability that 5 fair coin flips give a majority at least that large:

  | Agreement | Chance rate | Label |
  |---|---|---|
  | 3 of 5 | 100% | `split` |
  | 4 of 5 | 37.5% | `moderate` |
  | 5 of 5 | 6.25% | `high` |

- **Rule:** the label is `high` only at 5 of 5, and it is always shown with the chance rate. `weighted_agreement` is the kernel-weighted share.
- **Sentence:** `confidence.sentence` is ready to show, for example: "In 4 of the 5 past seasons that started like this one, Boro peak (mid-March to mid-April) greenness in the area around this field (250 m) was above normal. Random years agree this much about 38% of the time. These are past examples, not a prediction for this season."
- **Without NDVI:** the contract allows a rainfall-based confidence (`basis: "rainfall"`), but the engine does not build one. Without NDVI it returns "NDVI pending" and makes no cards. NDVI is cached for both demo sites, so `basis` is always `ndvi` today.
- **Reading it:** the backtest found no skill, and higher agreement did not go with more hits, so agreement describes the past examples. It is not a likelihood for this season.

## How the three cards are chosen

Rotation benefits and risks come only from `rules/rules.json`, each with its citation. NASA data supplies the weather and greenness evidence; it never says how a rotation performed.

> **The rule table is an unreviewed draft.** `rules/rules.json` was drafted by the engine owner with AI help (Claude) because the science translator's file had not arrived. Every non-null value is quoted from the source it cites; nothing was filled from memory, and anything unsourced is `null`. While `review_status` is not `"reviewed"`, every card set carries a warning saying so.

### 0. Seasons

Bangladesh has three cropping seasons. Every pattern lists one crop (or fallow) per season, in the order Nasim et al. 2017 use: "Rabi or Boro season followed by Kharif-I or Aus then Kharif-II or Aman season".

| Season id | Name | Months (Emran et al. 2022) | Dry season? |
|---|---|---|---|
| `rabi` | Rabi (winter, Boro season) | mid-November to mid-March | yes |
| `kharif1` | Kharif-1 (pre-monsoon, summer) | mid-March to mid-July | yes |
| `kharif2` | Kharif-2 (monsoon, Aman season) | mid-July to mid-November | no |

- **Season belongs to the slot, not the crop.** The same crop can sit in different seasons: mungbean is the Rabi crop in Mungbean–Fallow–T.Aman and the Kharif-1 crop in Wheat–Mungbean–T.Aman. Boro after mustard or potato sits in the Kharif-1 slot.
- **Scope:** the salinity filter and the water score apply to the dry-season slots (Rabi and Kharif-1), because "the problem of salinity increases in the dry season" (Nasim et al. 2017). Counting Kharif-1 as dry is the engine's reading, pending review.
- **Contract:** `strategy.seasons` gives the season of each slot, so the UI can label it.

### 1. Card 1 is the farmer's current rotation

`request.current_rotation` must be a `pattern_id` from the catalogue. The catalogue is the national cropping-pattern list in Nasim et al. 2017 (Bangladesh Rice Journal), plus a "salt-tolerant Boro variety" variant of Boro–Fallow–T.Aman. Card 1 is always shown, whatever it scores.

### 2. Candidates for cards 2 and 3

A pattern is a candidate if it meets all three conditions:

- it differs from the current rotation in a dry-season slot (Rabi or Kharif-1);
- it has at least one dry-season crop that is not fallow;
- it passes the salinity filter.

**The salinity filter:**
- It reads only `salinity_whole_season_max_dS_m`, never the seedling figure.
- A pattern drops out when the lower bound of the farmer's salinity class (SRDI 2010 classes, as reproduced by Debsharma et al. 2024) is above a dry-season crop's sourced whole-season value.
- A crop with no sourced value stays in, with a high-review risk.
- When the class is `unknown` or non-saline, nothing is filtered.

**Reading of "tolerates the class", pending the translator's review:** the filter compares the class's *lower* bound. A crop that passes but whose value is below the class's *upper* bound gets a high-review risk: "yield may fall in the saltier part of it".

**The two salinity sources measure different things.** FAO 29 values are the soil salinity up to which a crop gives *full* yield. Debsharma et al.'s 8 dS/m is the salinity at which the salt-tolerant lines *still produce grain*. The salinity score treats both the same way, so it overstates how far salt-tolerant Boro is ahead of the FAO crops.

**At 8 dS/m or more** (classes `moderate_8_12` and above), card 3 is "Fallow, short oilseed, or local review" (the Fallow–Fallow–T.Aman pattern). The reasons:
- The most salt-tolerant sourced Boro lines yield up to 8–10 dS/m (Debsharma et al. 2024).
- Nasim et al. 2017 report that "in tidal saline wetland, salinity restricts other crops to be included in dry season".

**Card 2 at 8 dS/m or more** is the top option whose *sourced* whole-season salt tolerance reaches the lower edge of the class. Today that is the BRRI salt-tolerant Boro variety (8 dS/m), at 8–12 dS/m. Only when no option has a sourced value that high (12 dS/m and above) does card 2 fall back to the top legume option, whose tolerance is unsourced and shown as a gap and a high-review risk.

If the farm already uses Fallow–Fallow–T.Aman, the fallow card would repeat card 1. So the same note goes into card 1's "why" instead. Card 2 is chosen as above, and card 3 is the top remaining option of the other kind (legume or not).

**"Saline class":** every class except `unknown` and the non-saline one (upper bound 2 dS/m or less). The filter and the salinity risks both use this one definition, so the 2–4 dS/m class is filtered too.

**History needed:**
- **Weather:** a date needs at least 5 comparable past seasons from 1999; otherwise the engine stops with a clear error. That rules out decision dates before mid-2003.
- **NDVI:** the NDVI pool needs at least 5 NDVI years from 2001; otherwise NDVI is "pending" and no cards are made. That rules out dates before mid-2005.
- **Sites missing from the NDVI file:** a site that isn't in the NDVI file is also "pending".

### 3. Scoring

Score = Σ priority weight × attribute score. Each attribute score is between 0 and 1, and the breakdown is shown on the card. The scores are computed over the pattern's dry-season (Rabi and Kharif-1) crops. A consequence to review: a pattern that drops a summer crop, such as Wheat–Fallow against Wheat–Jute, scores higher on water, because fewer crops use less water.

| Attribute | Score | Source column |
|---|---|---|
| `water` | 1 − (irrigation relative to Boro), summed over the dry-season crops. The ratio uses figures from the same study only (Hoque et al. 2023). Fallow counts as 0 irrigation by definition | `irrigation_mm` |
| `soil_n` | min(1, mid-point of `n_fix_kg_ha` / 40) for the best crop. 40 is the top of the only sourced range | `n_fix_kg_ha` |
| `salinity` | min(1, lowest whole-season threshold among the dry-season crops / 8) | `salinity_whole_season_max_dS_m` |
| `yield_stability`, `income`, `forage` | 0, plus an information gap: the table has no sourced column for them | none |

- **Unsourced values:** an attribute whose value is unsourced is `null` in `score_breakdown`, adds an information gap, and counts as 0 in the total. It is never estimated. A `null` means "no sourced value", which is not the same as a score of 0.
- **Constraint penalty:** when `constraints.water_availability` is `low`, the score loses 0.5 × (irrigation relative to Boro). This appears as `constraint_water` in the breakdown.
- **Gaps only:** equipment and market are information gaps, not filters, because there is no sourced data for them.

### 4. Picking two that differ in kind

- **Card 2:** the highest-scoring candidate that contains a legume.
- **Card 3:** the highest-scoring remaining candidate without a legume (the lower-water or salt-tolerant option).
- **If one kind is missing,** the next-highest candidate fills the slot.
- **Ties** are broken by national area share (`nca_pct`), then by `pattern_id`.

### 5. Card text

- **"Why":** a template that joins the card's role, the farmer's top-weighted priority and the confidence sentence.
- **Role words come only from sourced attributes:**
  - "lower-water" means the irrigation relative to Boro is known and below 1;
  - "salt-tolerant" means the sourced whole-season value is above Boro's 3.0 dS/m;
  - "with a nitrogen-fixing crop" means `n_fix_kg_ha` is sourced;
  - otherwise the text says "with a legume crop" or "without a legume".
- **A score of 0 or less:** the "why" says the card is shown as the most widespread pattern of its kind (Nasim et al. area share), because no sourced value separates the options.
- **Benefits:** the rule rows' benefit texts, each with its `citation_id`.
- **Risks:** the rule rows' risks plus rule-driven ones (salinity above a crop's threshold, unsourced tolerance, low water availability), ranked high, then medium, then low.
- **Fixed gaps:** field-level salinity, local prices, pest pressure and equipment.
- **Review flag:** every card has `needs_local_review: true`.
- **Banned wording:** "best", "should plant" and "you should" never appear.

### Answers to the four open translator questions (engine method, pending review)

1. **Turning columns into priority scores:** the table above.
2. **Yield stability:** no column, so it scores 0 and shows an information gap. No proxy is built.
3. **Equipment:** no column, so it is an information gap, not a filter.
4. **A separate "verified" flag for varieties:** not needed while cards show variety classes only. Named varieties stay off the cards.

## Backtest: rule fixed before the first run

Written 6 Nov 2026, before `backtest.py` existed and before any backtest number was seen. The verdict follows this rule whatever the numbers say.

**Verdict rule.** "SS > 0 and permutation p < 0.10 = some skill. Otherwise: no demonstrable skill, and the analog years are shown as historical examples only."

`verdict_text` is exactly one of:
- `Some skill: MSE skill score {ss} against the plain average over {n} Boro seasons ({first}–{last}), permutation p = {p}.`
- `No demonstrable skill: MSE skill score {ss} against the plain average over {n} Boro seasons ({first}–{last}), permutation p = {p}. The analog years are shown as historical examples only.`

**Protocol, also fixed before the first run:**
- **Years tested:** Boro harvest years 2001–2024 that have both a peak-window NDVI value and all matching features. Years that don't are listed in `excluded_years`.
- **Folds:** leave one year out. For held-out year t, the training years are all other tested years. Detrending, z-scores, Ledoit-Wolf and the NDVI trend are refitted on them alone.
- **Settings:** the same as the live `ndvi_pool`: k = 5, the site's matching features, the demo decision date's 60-day window (13 Nov), and the site's peak window.
- **Predictand:** t's peak-window NDVI minus the training years' linear trend.
- **Prediction:** the kernel-weighted mean of the 5 analogs' anomalies. The climatology prediction is 0.
- **Scores:**
  - `SS_MSE = 1 − MSE_analog / MSE_clim`, and the same for standardised-Euclidean analogs;
  - the Pearson anomaly correlation;
  - the tercile hit rate: terciles of the training anomalies in each fold, prediction and truth placed in them; chance is 1/3;
  - the beat count: years where |prediction − truth| < |truth|, with a one-sided sign test against 0.5.
- **Permutation p:** 1,000 runs with seed 20261113. In each run, every fold swaps its 5 analogs for 5 random training years and keeps the fold's own weights. p = (1 + runs with SS ≥ observed SS) / (1 + 1,000).
- **Calibration:** for agreement bins 3/5, 4/5 and 5/5, the hit rate is the share of years where the majority sign of the analog anomalies matched the sign of the truth.
- **2025 onward** (flagged for the Terra orbit drift) is never in the score. Each such year is predicted from all tested years and reported on its own in `flagged_years`.

### Final run (6 Nov 2026, Step 16; identical to the first run, after the rule above was written)

Decision date 13 Nov; 24 Boro seasons tested (2001–2024) at each site; no years excluded. Rerun with `python -m rotate_engine backtest --site <site> --date 2026-11-13`, or read `fixtures/backtest_<site>.json`.

| | Anwara (coastal) | Godagari (Barind) |
|---|---|---|
| SS_MSE, Ledoit-Wolf analogs | −0.148 | −0.311 |
| SS_MSE, standardised Euclidean | −0.148 (identical, because Anwara's shrinkage is 1.0) | −0.323 |
| Anomaly correlation | 0.08 | −0.27 |
| Tercile hit rate (chance 0.33) | 0.38 | 0.29 |
| Beat the plain average | 10 of 24 (sign test p = 0.85) | 10 of 24 (p = 0.85) |
| Permutation p | 0.53 | 0.87 |
| Hit rate at 3/5, 4/5, 5/5 agreement | 0.53 (n 17), 0.29 (n 7), none (n 0) | 0.54 (n 13), 0.40 (n 10), 1.0 (n 1) |
| **Verdict** | **No demonstrable skill** | **No demonstrable skill** |

`verdict_text`, exactly as the engine returns it:
- **Anwara:** "No demonstrable skill: MSE skill score -0.148 against the plain average over 24 Boro seasons (2001–2024), permutation p = 0.528. The analog years are shown as historical examples only."
- **Godagari:** "No demonstrable skill: MSE skill score -0.311 against the plain average over 24 Boro seasons (2001–2024), permutation p = 0.871. The analog years are shown as historical examples only."

**What this means:**
- **Analogs vs the average:** the 60 days of weather before 13 Nov do not predict the coming Boro peak greenness at either site better than the plain average.
- **Analog years:** under the rule, they are historical examples only. They show what past seasons that started like this one looked like, not what this season will do.
- **Confidence:** higher agreement among the look-alike years did not go with more hits. Treat the agreement count as a description of the examples, not as a likelihood.
- **In the output:** every analog result and card set carries the verdict as a warning, and every card carries it as a Derived evidence item. The confidence sentence describes past examples ("In 4 of the 5 past seasons that started like this one, …") and always ends "These are past examples, not a prediction for this season."
- **Past decision dates:** the decision season itself is never a tested year.
- **Flagged years:** in 2025 and 2026, both sites had peak anomalies well below trend (Anwara −0.18 and −0.17; Godagari −0.05 and −0.12). This fits the reported Terra drift, so it is no sign of a real crop change.

## Stretch modes and extra NDVI sources

Opt-in extras built after the must-haves (Step 15). None changes the default output.

### More NDVI sources (stretch, Step 15.5)

- **Aqua interleaving:**
  - `scripts/fetch_ndvi_ornl.py` pulls MYD13Q1 (Aqua) for the centre pixel from the ORNL DAAC web service, which needs no login.
  - With `aqua=True` the Aqua points sit beside the Terra points on their acquisition days, each marked with its satellite, and the same QA filter, gap rule, smoothing and 2025+ flag apply.
  - It is for display only. The predictand, the confidence and the backtest stay Terra-only, as the protocol fixed before the first run says.
- **3×3 window:**
  - The same script pulls a 9×9-pixel MOD13Q1 window (1 km each way) from Nov 2023 on.
  - With `window=True` the engine reports, per composite, the mean, min and max of the QA-passed pixels in the central 3×3 block.
  - It covers recent seasons only, because a full-record window costs about 2 hours of ORNL calls (30 s per call). The limit is marked in the script.
- **Checks on the fetched data (6 Nov):**
  - the window's centre pixel equals the AppEEARS Terra value on all 66 shared dates at both sites;
  - Aqua agrees with Terra within 8 days (r = 0.90 at Anwara and 0.95 at Godagari);
  - the 3×3 spread is typically 0.15 (Anwara) and 0.13 (Godagari) NDVI;
  - with `aqua=True` the smoothed line runs through the extra points, so `ndvi_smooth` and the low-vegetation windows can differ from the Terra-only view, while the raw Terra points stay identical.
- **HLS 30 m:**
  - AppEEARS lists `HLSS30_VI.020` (Sentinel-2) and `HLSL30_VI.020` (Landsat) NDVI. Their cloud mask is the `Fmask` layer of `HLSS30.020` and `HLSL30.020`.
  - `scripts/submit_ndvi_hls.py` submits one point task for both sites; it needs the Earthdata login in `.env`. When the task is done, `scripts/fetch_ndvi_appeears.py <task_id> hls` downloads the bundle into `data/ndvi/hls/` (fetched 6 Nov, task `1a7fe273-b13a-4d94-a0de-3c4f7565a469`).
  - With `hls=True` (`ndvi --hls`) the engine returns a **separate** 30 m curve: HLSS30 and HLSL30 points together on their acquisition days, marked `hls_s30` / `hls_l30`. It never joins the 250 m curve, because the pixels differ in size by about 70 times, so it cannot be combined with `aqua` or `window`.
  - **QA:** drop fill (−19999), points with no Fmask row, and any cloud, adjacent-to-cloud/shadow, cloud-shadow or snow/ice bit. Keep water. Keep high aerosol, but give it reliability 1 and flag it: haze marks about 85% of the clear Godagari points.
  - The same gap rule (more than 32 days breaks the line), Savitzky-Golay smoothing and low-vegetation rule apply. The smoother treats the irregular 2–16-day spacing as even, the same shortcut as for MODIS. The 2025+ orbit-drift flag is MODIS-only, so HLS points are not flagged for it.
  - **Checks (6 Nov):** Anwara 421 points, Godagari 580; within 8 days of a Terra point, r = 0.91 and 0.90, with mean NDVI within 0.02.
  - It is display only. The predictand, the confidence and the backtest stay Terra-only. There is no per-year HLS view (`ndvi-years`), because HLS starts in late 2015 and most look-alike years are older.

### Tercile scenario (stretch, Step 15.2)

- **Request:** `mode: "scenario"` with `tercile: "dry" | "normal" | "wet"`. It can be combined with a `shift`.
- **Ranking past seasons:** each training season (from Boro 1999) gets its total rain from the day after the decision's calendar day up to 30 Apr of its harvest year. Seasons are split into thirds at the 1/3 and 2/3 quantiles of those totals. A season with any missing day is left out, never filled.
- **Rain source:** GPM IMERG as served by POWER (`data/power/<site>_imerg.csv`). It is used at both sites because Anwara's `PRECTOTCORR` has the 2015 jump and IMERG does not.
- **Matching:**
  - z-scores, detrending and Ledoit-Wolf still use all training seasons;
  - only the choice of the k = 5 nearest is limited to the requested third, in both pools;
  - fewer than 5 seasons in the third gives a clear error.
- **Tags and wording:** everything is tagged Scenario, as with the slider. The first warning names the third, its mm range and the source, and says it is not a forecast that this season will turn out that way.
- **Demo date, 13 Nov (28 seasons, 1999–2026):**

  | Site | Dry third | Wet third |
  |---|---|---|
  | Anwara | 122 mm or less | more than 216 mm |
  | Godagari | 80 mm or less | more than 118 mm |

### Optional 4th card (stretch, Step 15.4)

- **Request:** `extra_card: true`. Without it the output stays at exactly three cards.
- **Which pattern:** the highest-ranked remaining candidate, using the same candidate rules, scoring and tie-breaks as cards 2 and 3, that is not already shown and whose dry-season crops differ from every card shown. If every remaining candidate repeats a dry-season set, the top remaining one is used. If none remains, there is no 4th card.
- **The card:** card id `alt_3`, the same evidence as the other cards, and "why" text starting "Shown as a fourth option to compare".
- **Demo examples (13 Nov):**
  - Godagari: Maize–Fallow–T.Aman;
  - Anwara at 4–8 dS/m: Wheat–Fallow–T.Aman;
  - Anwara at 8–12 dS/m: Mungbean–Fallow–T.Aman, whose salt tolerance is unsourced and shown as a high-review risk.

### What-if slider (stretch, Step 15.1)

- **Request:** `mode: "scenario"` plus a `shift`.
- **The change:** the shift alters only the current season's 60-day window, on the raw daily POWER values. Each day's rain is multiplied by (1 + `rain_pct`/100), `temp_c` is added to both Tmin and Tmax (so the hot-day count moves too), and `rh_points` is added to RH, which is kept within 0–100.
- **The rerun:** matching then reruns as usual (detrend, z-scores, Ledoit-Wolf, both pools, weights, confidence).
- **Unchanged:** past seasons and the backtest are not changed.
- **Tags:** every evidence item and the confidence are tagged Scenario and labelled "What-if"; the change is named in the first warning and in each evidence source.
- **Rain at Anwara:** rain isn't a matching feature there, so a rain shift changes nothing, and a warning says so.
- **How to read it:** the backtest shows no skill, so a what-if only shows which past seasons resemble the changed weather. It is not a prediction of what that weather would do.

### Soil wetness (stretch, Step 15.3)

- **What:** POWER `GWETROOT`, root-zone soil wetness from 0 (dry) to 1 (saturated), averaged over the 60-day window.
- **Shown as:** an Observed evidence item labelled "model output", compared with the average of Boro seasons from 1999. It is never a matching feature.
- **Where it is shown:** only where the site's rain is usable, today Godagari. At Anwara it carries the same 2015 jump as the rain (see `DATA_SOURCES.md`), so it is hidden, and the rain warning says so.
- **What-if:** in a what-if the window's soil wetness is set to unknown, because the model value can't be changed consistently by hand, so it is not shown, and a warning says so.
- **Glossary:** soil wetness here is the model's estimate for a grid cell of about 55 × 65 km (the POWER cell size given in the research report), not a field measurement.

## Data sources

Every value here comes from the saved responses in `data/`, not from memory. `DATA_SOURCES.md` holds the full detail (header fields, data breaks, quality counts); the storyteller owns its final version. Source labels are given exactly as the POWER response header gives them.

| Source | Version, access | What the engine uses it for | Where |
|---|---|---|---|
| NASA POWER Daily API, point, `community=AG` | API v2.10.2; accessed 2026-11-05 | `PRECTOTCORR`, `T2M_MIN`, `RH2M`: matching window. `T2M_MAX`: hot-day count. `GWETROOT`: soil-wetness evidence (Godagari). `ALLSKY_SFC_SW_DWN`: fetched, not used | `data/power/<site>.csv`, raw response `data/raw/power/<site>.json` |
| NASA POWER `IMERG_PRECTOT` (GPM IMERG as served by POWER) | same API; valid 1998-01-01 to 2026-09-14 | ranking past seasons in the tercile scenario only; never matched | `data/power/<site>_imerg.csv` |
| MODIS Terra MOD13Q1.061 via AppEEARS (task `dfdede24-460a-454b-bdcf-b4c52f397bf8`) | AppEEARS 3.135; accessed 2026-11-05 | NDVI curve, peak-window anomaly, confidence, backtest | `data/ndvi/`, hashes in `bundle_manifest.json` |
| MODIS Aqua MYD13Q1.061 and a 9×9-pixel MOD13Q1 window via the ORNL DAAC subsetting service | accessed 2026-11-06 | display-only extras: Aqua points beside Terra, 3×3 spread (Nov 2023 on) | `data/ndvi/ornl/` |
| HLS v2.0 NDVI (`HLSS30_VI.020`, `HLSL30_VI.020`) with `Fmask` (`HLSS30.020`, `HLSL30.020`) via AppEEARS (task `1a7fe273-b13a-4d94-a0de-3c4f7565a469`) | accessed 2026-11-06 | display-only separate 30 m curve, Nov 2015 on | `data/ndvi/hls/`, hashes in its `bundle_manifest.json` |
| Crop rule table (not NASA) | engine draft, 5 Nov 2026, unreviewed | benefits, risks, salinity filter, scoring | `rules/rules.json`, citations inside |

**POWER header sources** (one list for the whole response, not per parameter): MERRA2, GEOSIT, SRB, SYN1DEG, FLASHFLUX, POWER. Fill value −999.0, converted to missing before anything else. Time standard: local solar time (IMERG: UTC, because POWER does not serve it in LST). POWER's parameter metadata defines `PRECTOTCORR` as "The average MERRA-2 bias corrected total precipitation".

**Breaks in the POWER series:** `RH2M`, `T2M_MAX` and `PRECTOTCORR` step in 1997 at both sites; Anwara's `PRECTOTCORR` and `GWETROOT` jump again from 2015. Hence the pool from 1999, and no rain or soil wetness at Anwara. The numbers are in `DATA_SOURCES.md`.

**Citation text required by POWER (both lines):**
- "The data was obtained from National Aeronautics and Space Administration (NASA) Langley Research Center's Prediction Of Worldwide Energy Resources (POWER) project funded through the NASA Earth Science Division."
- "The data was obtained from the POWER Project's Daily v2.10.2 version on 2026/11/05."

**MOD13Q1 citation (from the AppEEARS bundle README):** Didan, K. (2021). MODIS/Terra Vegetation Indices 16-Day L3 Global 250m SIN Grid V061. NASA Land Processes Distributed Active Archive Center. https://doi.org/10.5067/MODIS/MOD13Q1.061. Accessed November 5, 2026.

**AppEEARS citation (from the same README):** AppEEARS Team. (2026). Application for Extracting and Exploring Analysis Ready Samples (AppEEARS). Ver. 3.135. NASA EOSDIS Land Processes Distributed Active Archive Center (LP DAAC), USGS/Earth Resources Observation and Science (EROS) Center, Sioux Falls, South Dakota, USA. Accessed November 5, 2026. https://appeears.earthdatacloud.nasa.gov

**Rule-table sources:** Nasim et al. 2017, FAO Irrigation and Drainage Paper 29, Debsharma et al. 2024, Emran et al. 2022 and Hoque et al. 2023. Full references and URLs are in `rules/rules.json` → `citations`. The SRDI salinity classes are used as reproduced by Debsharma et al. 2024.

**Not used, so not to be claimed:** BMD station data (restricted), ECOSTRESS, GRACE/GRACE-FO, SRTM, Landsat or Sentinel-2 as separate sources, SMAP, and crop models. HLS 30 m (via AppEEARS) is used only as a display curve.

## Limits of this data and method

This is the content for the UI's "limits of this data" panel.

- **No forecast.** The engine matches the 60 days before the decision and shows what followed in past seasons. The backtest found no demonstrable skill at either site, so the look-alike years are historical examples only.
- **Reanalysis, not measurement.** POWER values are reanalysis and model output for a grid cell of about 55 × 65 km (the cell size given in the research report), not readings from a field or a station.
- **The latest days are near-real-time.** The most recent days in the window come from POWER's near-real-time products, which the header names GEOSIT (weather) and FLASHFLUX (solar), not the long-term reanalysis. Every output carries this warning.
- **Data breaks.** POWER series step in 1997 (both sites) and Anwara's rain and soil wetness jump from 2015. Years before Boro 1999 are left out, and Anwara matches on temperature and humidity only.
- **Two scales.** A POWER cell is tens of kilometres across. One MODIS pixel is 250 m, about 5–6 ha, bigger than a smallholder plot, so NDVI is "vegetation in the area around this field (250 m)". At Anwara, 425 of 614 composites carry the "ocean coastlines and lake shorelines" land/water flag.
- **NDVI cannot diagnose.** Low NDVI is a low-vegetation window: bare, flooded or newly planted land. It is consistent with salinity stress but cannot show it.
- **Clouds.** In June–August only 6–46% of composites pass the quality filter. Gaps are shown as gaps, never filled.
- **MODIS is ending.** Terra's orbit drift affects data from 2025 on: those composites are flagged and never scored. Terra and Aqua end science operations in about 2027. VIIRS (VNP13A1, 500 m, from 2012) is the named successor and is not used here.
- **Godagari's peak window** (February) follows its observed curve; the crop behind it still needs the science translator's check. A rise in its Jan–Feb minimum from 2012 may be orchard expansion.
- **The rule table is a draft.** It was drafted by the engine owner with AI help, every value quoted from its cited source, and it is not yet reviewed. Unsourced values are null and shown as gaps. Yield stability, income, forage, equipment and market have no sourced data.
- **Salinity is the user's choice.** The class is local information, not NASA data. Field-level salinity is an information gap on every card.
- **Skipped years:** none at the demo date. Years excluded from the backtest: none.
- **Fallbacks:** the Euclidean fallback was not used. Anwara's Ledoit-Wolf shrinkage is 1.0, so its match is effectively standardised Euclidean.

## Roadmap: the whole country, any point

Roadmap only. Arbitrary locations are out of scope for the hackathon, and the map and backend are teammates' work. This section is for the pitch and for judges' questions ("you have two points; farmers are everywhere"). The estimates were written on 6 Nov 2026. The pixel, date and file-size figures come from our own downloads; queue times, compression and AppEEARS area limits are **unverified**.

### Why two points now

- **Not a limit of the method.** Nothing in the engine is written for Anwara or Godagari. A site is one entry in `data/sites.json` plus its cached files, and the same code runs for any entry.
- **Chosen to show two hazards.** Coastal salinity (Anwara) and northwest drought (Godagari) are Bangladesh's two main farm hazards. One point each shows the same method giving different answers ("two regions, two hazards").
- **Each site needs checks.** The two sites turned up real data problems: POWER rain at Anwara is 2–4 times IMERG from 2015 on, so rain is switched off there, and Godagari's crop peak is in February, not March–April. A new site needs the same checks.
- **The demo runs offline,** on one laptop with cached data.

### NASA services that make it possible

| Need | NASA service | Login | Speed for one point | Role in a national version |
|---|---|---|---|---|
| Weather history | NASA POWER API (used now) | none | seconds | download every grid cell (about 55 × 65 km) once; no exact rate limit is published, so retry when it answers 429 |
| NDVI, one point | ORNL DAAC MODIS web service (used now) | none | about 30 s per call, many calls for the full record | fine for adding one site; too slow while a farmer waits |
| NDVI, whole country | AppEEARS **area** request (point requests used now) | Earthdata Login | queued, once | upload a Bangladesh outline; get NDVI and quality maps (GeoTIFF or NetCDF) for every 16-day composite since 2000 |
| 30 m NDVI | HLS via AppEEARS (used now for two points) | Earthdata Login | queued | per registered farm only; nationwide is too large (below) |
| Is the point cropland? | MODIS land cover MCD12Q1 (500 m) via AppEEARS | Earthdata Login | once | warns when a tapped point is not farmland; replaces our manual imagery check |
| Map backgrounds | NASA GIBS (the imagery behind Worldview) | none | fast tiles | map pictures only, not data values |

No new kind of NASA data is needed: the same data, downloaded in bulk.

### How it would work

Ahead of time (a server job, refreshed every 16 days):

1. POWER: download every cell covering Bangladesh.
2. AppEEARS area request: NDVI, pixel reliability and composite day for all of Bangladesh, 2000 to now, stored as a data cube chunked so one pixel's history is a single read.
3. MCD12Q1: a cropland mask.
4. Automatic per-cell data checks, for example the Anwara rain jump (POWER rain vs IMERG before and after 2015) switching a feature off with a warning.

When a farmer taps a point (no NASA call at that moment):

1. Snap to the POWER cell: weather window and look-alike years.
2. Read the 250 m NDVI pixel from the cube: greenness curve.
3. Cropland mask says "not farmland": warn.
4. Salinity default from the SRDI map by upazila, labelled local information, not NASA; the user can change it.
5. The agro-ecological zone picks the rule table and the crop calendar (peak window).
6. The engine builds the cards, exactly as now.

### Engine changes

- A site built from latitude and longitude (POWER cell, NDVI pixel, zone, peak window) instead of a hand-written `sites.json` entry.
- The manual data checks turned into automatic checks that switch a feature off and warn.
- A reader for the NDVI cube beside the current CSV readers.
- Matching, confidence, cards and backtest stay as they are.

### Storage

| Data | How it was estimated | Size |
|---|---|---|
| POWER weather, every cell | about 104 cells in the bounding box × 3.85 MB per cell (our per-site CSV plus raw JSON) | about 0.4 GB |
| MODIS NDVI 250 m, whole country, 2000 on | 147,570 km² ÷ 0.054 km² per pixel ≈ 2.75 million pixels × 614 composites (our count, 2000-02-18 to 2026-10-16) × 5 bytes (NDVI, reliability, composite day) | 8.5 GB raw, about 3–6 GB compressed; the download may be about 18 GB if AppEEARS sends the whole bounding rectangle |
| MODIS land cover (cropland mask) | 500 m, yearly | about 50 MB |
| Update every 16 days | one new composite for the country | about 15 MB |
| HLS 30 m, whole country | about 164 million pixels × about 900 acquisitions (our HLS count, Nov 2015 to Oct 2026) × 3–4 bytes | about 0.5 TB: **not worth storing** |
| HLS 30 m, registered farms only | about 250 KB per point (our bundle) | 10,000 farms ≈ 2.5 GB |

**Total without nationwide HLS: under 10 GB.** One small server with a 50 GB disk is enough.

### Time

**One-off data fetch:**

| Step | Estimate |
|---|---|
| POWER, about 100 cells | under an hour, by a script that retries on 429 |
| AppEEARS area request, 26 years | queue: a few hours to a day or more (unverified; our point tasks finished the same day); then 30 min to 2 h to download 10–20 GB, depending on the connection |
| Building the data cube | about 1 hour of computing |
| Per-cell data checks | minutes, once automated |

About 1–2 days of waiting, mostly the AppEEARS queue, with little hands-on work.

**Per farmer query:** the current engine builds cards for Anwara in about 2 s, including Python start-up, using about 180 MB of memory (measured 6 Nov). Reading one pixel's history from the cube takes milliseconds. So a tap gives cards in about 2 s.

**Build effort:**

| Work | Who | Estimate |
|---|---|---|
| Nationwide POWER fetch and automatic data checks | engine | 1–2 days |
| AppEEARS area request, cube and engine reader | engine | 2–3 days |
| Site from latitude/longitude (cell, pixel, zone, peak window) | engine | 2–3 days |
| Cropland mask and SRDI salinity default by upazila | engine and data | 2–5 days (depends on getting SRDI map data) |
| Backend API, point-picking map, hosting | teammates | 1–2 weeks |
| `rules.json` per agro-ecological zone, reviewed by agronomists | domain experts | weeks to months: the real bottleneck |
| Backtest per region and a write-up | engine | 2–3 days |

A working nationwide prototype: about 3–4 weeks for 1–2 developers. Making it scientifically trustworthy (reviewed rules, regional backtests) takes months.

### What scaling does not fix

- **No demonstrable skill.** The backtest found none at either site. A national version needs a backtest per region, and the cards keep showing look-alike years as past examples only.
- **Rules and calendars are regional.** Each zone needs its own reviewed rules and crop calendar.
- **Two scales remain.** POWER stays a cell tens of kilometres across, and a MODIS pixel stays bigger than most plots.
- **Two points prove less than they seem.** They show the pipeline works for two hazards, not that it works everywhere.

### Pitch line

> "Nationwide needs under 10 GB of NASA data (POWER plus the MODIS NDVI archive for all of Bangladesh), refreshed with about 15 MB every 16 days, and runs on one small server with about 2 seconds per farmer query."

## Use of AI

This section is input for the project page's "Use of AI" disclosure. Statistical methods such as Mahalanobis distance and Ledoit-Wolf belong under Methods, not here.

| Tool | Where | How |
|---|---|---|
| Google Gemini | planning, before the event | produced a planning report (`Plan/NASA Space Apps Plan Optimization.pdf`). It is treated as unverified background, never as a source of facts or figures |
| Claude (Anthropic) | planning and research, before and during the event | cross-checked the plans against primary sources (`Plan/ROTATE plan verification and upgrades.md`) and helped draft `rules/rules.json` from the cited papers; each value was checked against the source text |
| Claude Code (Anthropic) | engine build, 5–6 Nov 2026 | wrote the engine code, tests, fixtures and these two documents step by step from `Plan/ROTATE engine build steps.md`, under the engine owner's direction; the owner decided every method choice and reviewed each step's "Done when" check |

**Representative prompts** (paraphrased from the build sessions):
- "Start step 15": build the stretch items in plan order, each with its tests.
- "Did the look-alike method actually predict past seasons? Did it match?" The answer (no demonstrable skill) was put into every output as a warning, with the owner's approval.
- "Complete stretch items 2 and 5 first": the tercile scenario and the extra NDVI sources.
- "Complete step 17": these two documents.

**Decisions made by the owner, not the AI:** starting the pool at 1999, dropping rain at Anwara, showing the backtest verdict on every card set, and keeping the rule table marked unreviewed.

**No AI in the product.** The engine contains no language model. Card text is filled from fixed templates and computed values. If the team adds an LLM narrative later, it may only narrate computed evidence and never decide.

## References

**Method**
- Ledoit, O. & Wolf, M. (2004). A well-conditioned estimator for large-dimensional covariance matrices. *Journal of Multivariate Analysis* 88(2): 365–411. https://doi.org/10.1016/S0047-259X(03)00096-4
- Lorenz, E. N. (1969). Atmospheric predictability as revealed by naturally occurring analogues. *Journal of the Atmospheric Sciences* 26(4): 636–646. https://doi.org/10.1175/1520-0469(1969)26<636:APARBN>2.0.CO;2
- Mahalanobis, P. C. (1936). On the generalised distance in statistics. *Proceedings of the National Institute of Sciences of India* 2: 49–55.
- Murphy, A. H. (1988). Skill scores based on the mean square error and their relationships to the correlation coefficient. *Monthly Weather Review* 116(12): 2417–2424. https://doi.org/10.1175/1520-0493(1988)116<2417:SSBOTM>2.0.CO;2
- Savitzky, A. & Golay, M. J. E. (1964). Smoothing and differentiation of data by simplified least squares procedures. *Analytical Chemistry* 36(8): 1627–1639. https://doi.org/10.1021/ac60214a047
- Mosleh, M. K. & Hassan, Q. K. (2014). Development of a remote sensing-based "Boro" rice mapping system. *Remote Sensing* 6(3): 1938–1953. https://doi.org/10.3390/rs6031938

**Data**
- NASA POWER Daily API v2.10.2, https://power.larc.nasa.gov, accessed 2026-11-05 (citation text above).
- Didan, K. (2021). MODIS/Terra Vegetation Indices 16-Day L3 Global 250m SIN Grid V061. NASA LP DAAC. https://doi.org/10.5067/MODIS/MOD13Q1.061
- Didan, K. (2021). MODIS/Aqua Vegetation Indices 16-Day L3 Global 250m SIN Grid V061. NASA LP DAAC. https://doi.org/10.5067/MODIS/MYD13Q1.061
- Neigh, C. (2025). HLS Sentinel-2 Multi-spectral Instrument Vegetation Indices Daily Global 30m v2.0. NASA LP DAAC. https://doi.org/10.5067/HLS/HLSS30_VI.002, and HLS Operational Land Imager Vegetation Indices Daily Global 30m v2.0, https://doi.org/10.5067/HLS/HLSL30_VI.002 (both accessed 2026-11-06).
- Neigh, C., Ju, J., Roger, J.-C., Skakun, S., Vermote, E., Claverie, M., Dungan, J., Yin, Z., Freitag, B., & Justice, C. (2021). HLS Sentinel-2 MSI and OLI Surface Reflectance and TOA Brightness Daily Global 30m v2.0 (Fmask source). NASA LP DAAC. https://doi.org/10.5067/HLS/HLSS30.002 and https://doi.org/10.5067/HLS/HLSL30.002 (accessed 2026-11-06).
- AppEEARS Team (2026), Ver. 3.135 (citation text above).
- ORNL DAAC. Terrestrial Ecology Subsetting & Visualization Services (TESViS) Global Subsets Tool. https://doi.org/10.3334/ORNLDAAC/1379, accessed 2026-11-06.
- Crop rule table sources: `rules/rules.json` → `citations`.

**Software** (pinned in `engine/pyproject.toml`)
- Python 3.12.
- NumPy 2.5.4: Harris, C. R. et al. (2020). Array programming with NumPy. *Nature* 585: 357–362. https://doi.org/10.1038/s41586-020-2649-2
- pandas 3.1.1: McKinney, W. (2010). Data structures for statistical computing in Python. *Proc. 9th Python in Science Conference*: 56–61. https://doi.org/10.25080/Majora-92bf1922-00a
- scikit-learn 1.9.1 (`LedoitWolf`): Pedregosa, F. et al. (2011). Scikit-learn: machine learning in Python. *Journal of Machine Learning Research* 12: 2825–2830.
- SciPy 1.18.1 (chi-square cutoff, Savitzky-Golay filter): Virtanen, P. et al. (2020). SciPy 1.0: fundamental algorithms for scientific computing in Python. *Nature Methods* 17: 261–272. https://doi.org/10.1038/s41592-019-0686-2
- pydantic 2.14.2 (the JSON contract), https://docs.pydantic.dev
- Development only: pytest 9.2.0, jsonschema 4.26.0; scripts only: requests 2.34.2, requests-cache 1.3.3, tenacity 9.2.1.
