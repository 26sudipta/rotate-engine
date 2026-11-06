# ROTATE engine plan

Nov 3, 2026 · @sudipta das

## Your part

You build the ROTATE engine: a Python package that takes NASA data and a location, finds the look-alike years, scores how much they agree, tests itself, and returns the results as JSON. Your teammates build the website, the app, and their backend, and plug your engine in later.

Your engine never draws a screen or runs a web server. It is a set of functions plus a command-line runner, so your teammates can call it however suits their backend.

| You build (the engine) | Teammates build |
| --- | --- |
| Download and clean NASA POWER weather and MODIS vegetation data | Web and app frontend: inputs, cards, charts |
| Look-alike (analog) year matching with Mahalanobis distance | Their backend and API, which call your engine |
| Confidence score | Rule table of crops and varieties per hazard (science translator) |
| Backtest that proves the method works | Videos and project page |
| Card data: joins analogs, NDVI, and rule-table rows into three cards as JSON |  |

Agree with the team on one thing early: who turns your results into the three cards, you or the backend teammate. This plan assumes you do, because it needs the analog results.

## Data pipeline

Pull everything for the demo sites once, save it to files in the repo, and have the engine read only from those files. The demo then never waits on a NASA server.

1. **NASA POWER (weather).** One request per site for daily data from 1 Jan 1981 to the latest available date. Parameters: T2M\_MAX, T2M\_MIN, PRECTOTCORR, RH2M, ALLSKY\_SFC\_SW\_DWN. No login is needed. Save as `data/power/<site>.csv`.
2. **MODIS NDVI (vegetation).** Submit an AppEEARS point request for MOD13Q1 NDVI at each site, 2000 to now, in the first build hour. It needs an Earthdata login and can sit in a queue. Save as `data/ndvi/<site>.csv` with date, NDVI, and the quality flag.
3. **Clean NDVI.** Drop low-quality points using the quality flag, then keep the 16-day series. Mark gaps and do not fill them silently.
4. **Sites file.** `data/sites.json` lists each demo site: id, name, latitude, longitude, main hazard, and which files exist.
5. **Fallback.** If a site has no NDVI file yet, the engine still returns analogs and says "NDVI pending".

Start with Chattogram. Add a northwest drought site only once the first site works end to end.

Suggested stack: Python with requests, pandas, and numpy. Check that your teammates' backend can call Python; if it cannot, the engine can write its JSON to files they read.

## Analog algorithm

Find the past years whose weather before a planting decision looked most like this year's, using a standardised Mahalanobis distance. Then report how much those years agree and test whether the method beats a simple average.

**1. Features (one row per year).** Pick a decision date and season, for example the start of Boro. Take a 60-day window before the decision date and compute 4 values per year:

- total rainfall (PRECTOTCORR)
- mean daily maximum temperature (T2M\_MAX)
- mean relative humidity (RH2M)
- mean solar radiation (ALLSKY\_SFC\_SW\_DWN)

Use only data from before the decision date. Using later data would leak the answer.

**2. Standardise.** Turn each column into z-scores using the past years only.

**3. Distance.** Estimate the covariance matrix S from the past years, then for each past year y:

```latex
D(x, y) = \sqrt{(x - y)^\top S^{-1} (x - y)}
```

Here x is this year's row. With about 45 years and 4 variables, the plain covariance is stable enough. Skip the robust MCD version the Gemini plan suggested, because it would ignore the extreme years that matter most.

**4. Analogs.** Return the k closest years (start with k = 5), each with its distance and its weather anomalies.

**5. Confidence.** For the analog years that have NDVI (2000 onward), work out whether the season's vegetation was above or below normal. Confidence = how many of the k analogs point the same way, for example "4 of 5 analog years had below-normal vegetation".

**6. Backtest (the strongest Validity evidence).** For each year with NDVI, hide it, find its analogs from the other years, and predict its NDVI curve as the mean of the analogs' curves. Compare the error with a baseline that uses the average of all other years.

```latex
\text{skill} = 1 - \frac{\text{RMSE}_{\text{analog}}}{\text{RMSE}_{\text{baseline}}}
```

Skill above 0 means the analogs beat the average. Report the number honestly, even if it is near 0.

**7. What-if (stretch).** Shift this year's rainfall or temperature by a slider value, rerun steps 3 to 5, and tag the result as Scenario.

## Engine interface

Agree on these function names and their JSON outputs with the backend teammate on day one. Give them a sample JSON file for each, so they can build while your real code catches up. Every function also runs from the command line, for example `python -m rotate_engine analogs --site chattogram --date 2026-11-15`.

| Function | Input | Returns | Needed by |
| --- | --- | --- | --- |
| `list_sites()` | none | Sites with id, name, coordinates, hazard | First demo |
| `find_analogs(site, decision_date, k=5)` | site, decision date, number of years | Look-alike years with distance, weather differences, confidence sentence | First demo |
| `build_cards(site, hazard, current_rotation, priorities, constraints)` | farmer inputs plus `rules.json` | Three cards: strategy, why, evidence (tagged), benefits, gaps, risks | First demo |
| `ndvi_for_years(site, years)` | site, list of years | Vegetation series per year with gaps marked, or "pending" | Day 1 evening |
| `run_backtest(site)` | site | Skill score, the two errors, years tested | Day 2 morning |

These names are suggestions; rename them freely, but agree on the JSON shape.

One evidence item inside a card's JSON:

```json
{
  "label": "Rainfall in the 60 days before planting",
  "value": "38% below the 1981–2025 average",
  "source": "NASA POWER (MERRA-2 reanalysis)",
  "tag": "Observed",
  "analog_year": 2014
}
```

Tags: "Observed" for NASA values, "Derived" for anything Rotate computes (distance, confidence, skill), "Scenario" for what-if output. Benefits and risks come from the rule table and carry its citation, never a NASA tag.

## Handoffs

Two handoffs decide whether Day 1 works: the sample JSON to the frontend, and the rule table from the science translator.

| What | From | To | When |
| --- | --- | --- | --- |
| Sample JSON for every engine function (hand-written is fine) | You | Backend teammate | First build hour |
| Rule table as `rules.json`: per hazard and season, crops or varieties, benefits, risks, citation | Science translator | You | Before 14:00 on Day 1 |
| Chosen demo site(s) and the farmer's current rotation for each | Team | You | First build hour |
| Working engine package in the shared repo, with cached data files | You | Backend teammate | When `build_cards` works on real data |
| Backtest number and one-line meaning | You | Storyteller | Day 2 morning |
| Data-sources list and "limits of this data" text | You | Storyteller (project page) | Day 2 morning |
| README section: how to run the engine | You | Repo | Day 2 morning |

## Your schedule

The Chattogram page lists 13–14 November. Confirm the dates and the video deadline with the Local Lead, then shift these blocks to match.

**Before the event (no project code)**

- [ ] Create an Earthdata login and test that you can sign in to AppEEARS.
- [ ] Read the NASA POWER API docs and the AppEEARS API docs.
- [ ] Install Python with requests, pandas, and numpy. The ROTATE code itself waits for the opening.
- [ ] Learn the two ideas on a toy example of your own: z-scores with Mahalanobis distance, and leave-one-out testing.
- [ ] Ask the backend teammate what language their backend uses, and whether they can import Python.

**Day 1**

- [ ] First hour: submit the AppEEARS NDVI request, pull POWER for the demo site, and send sample JSON to the backend teammate.
- [ ] Next 2–3 hours: features, distance, analogs, and confidence working in a script on real data.
- [ ] Wrap them as `list_sites`, `find_analogs`, and `build_cards` (using `rules.json`).
- [ ] Before the demo is recorded: hand over the working engine and check the demo path end to end with the backend teammate.
- [ ] Evening: clean NDVI and add `ndvi_for_years`. Add the second site if everything else works.

**Day 2 morning**

- [ ] Run the backtest and add `run_backtest`.
- [ ] Hand the numbers, data-sources list, and limits text to the storyteller.
- [ ] Write the README section and check the repo opens cleanly in a private window.

## Check in the docs first

These details are from memory or from the fact-check notes, not from a test run. Confirm each in the official docs before you rely on it.

- [ ] POWER request format: the daily point endpoint, the `community=AG` setting, and the exact parameter names (T2M\_MAX, T2M\_MIN, PRECTOTCORR, RH2M, ALLSKY\_SFC\_SW\_DWN). Some solar data may start after 1981.
- [ ] AppEEARS: login gives a bearer token; point tasks return CSV; task status values are pending, processing, done, and error.
- [ ] MOD13Q1 layer names for NDVI and its quality flag in AppEEARS.
- [ ] numpy's matrix inverse (`numpy.linalg.inv`) or `pinv` for the covariance; use `pinv` if the matrix is close to singular.
- [ ] Whether HLS 30 m vegetation data is offered in AppEEARS, if you try the 30 m stretch goal.

Sources: [NASA POWER docs](https://power.larc.nasa.gov/docs/) · [AppEEARS API](https://appeears.earthdatacloud.nasa.gov/api/) · the fact-check report in the project files (research/ROTATE plan fact check.md).
