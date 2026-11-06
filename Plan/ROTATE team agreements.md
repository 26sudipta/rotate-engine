# ROTATE team agreements

Nov 5, 2026 · Step 0.6 of `ROTATE engine build steps.md` · drafted by @sudipta das for the team to confirm

These are defaults. Each one stands until the team changes it in writing, here. Q7 to the Local Lead is still unanswered, so the `rules.json` columns and the JSON field names are **not** agreed here: both freeze in Step 3, after the opening.

## 1. Roles

From the report's "Roles, with owners for the new items". Fill in a name per row at the first team meeting. One person may hold two roles; the engine role stays with one person.

| Role | Person | Owns |
|---|---|---|
| Engine | Sudipta | `rotate_engine` package, fetch scripts, cached data, analogs, confidence, NDVI cleaning, backtest (Day 1 evening must-have), schema and fixtures in hour 1, provenance block, limits-panel facts, `DATA_SOURCES.md` draft |
| Backend | _name_ | Calls the engine (see §4); a thin web wrapper only if needed; runs the demo on the presenting laptop with Wi-Fi off |
| Frontend | _name_ | Inputs, map, cards, NDVI chart (raw points plus smoothed line, gaps shown), chance-rate text, glossary, Bangla labels |
| Science translator | _name_ | `rules.json` with citations, whole-season salinity tolerance, explainers, ranked review flags, wording check ("compare", never "best") |
| Storyteller / designer | _name_ | 240 s and 30 s videos, project page, AI disclosure, `LICENSE` and the "Uses NASA data. Not endorsed by NASA." footer, under-18 and subtitle checks, private-window link test |

## 2. Git conventions

- **Folder ownership.** Only the owner edits a folder; anyone else asks the owner or opens a pull request.

  | Folder | Owner |
  |---|---|
  | `engine/`, `scripts/`, `data/`, `schemas/`, `fixtures/` | Engine |
  | `rules/` | Science translator |
  | `backend/` | Backend |
  | `frontend/` | Frontend |
  | `README.md`, `DATA_SOURCES.md`, `LICENSE`, `docs/` | Storyteller (Engine supplies the data facts) |

- **`main` always runs.** Work on short branches named `<role>/<topic>` (e.g. `engine/analogs`). Merge to `main` only when the engine tests pass and the demo still opens from the fixture. Pull `main` at least every hour.
- **Commit messages:** `<type>: <description>`, where type is one of feat, fix, refactor, docs, test, chore, perf, ci.
- **Tag before recording.** Tag `demo-v1` before the 240 s video and `final` before the project page is submitted. Stretch work starts only after `demo-v1` exists.
- **Never commit:** `.env` (Earthdata credentials, AppEEARS token), BMD station data, or the four PDF/DOCX planning files (listed by name in `.gitignore` in Step 2).

## 3. Cut order (report risk 18)

When Day 1 runs late, cut in this order, first to last:

1. Bangla narrative (Bangla labels stay)
2. What-if slider
3. Second site
4. NDVI curve (show "NDVI pending" instead)
5. Live priority dial (replace with fixed presets)

Never cut: the analog engine with honest confidence, the three cards with the existing rotation first, the limits panel and the "needs local review" flags. When time runs short, protect Validity, then Relevance, then the demo.

## 4. How the backend gets cards

Default, by the backend teammate's stack:

1. **Python backend:** import `rotate_engine` and call its functions.
2. **Any other stack:** run the CLI, e.g. `python -m rotate_engine cards --site ctg_anwara --date 2026-11-13 --out cards.json`, and serve the file.
3. **Fallback for both:** the frontend reads the pre-generated JSON in `fixtures/`. No server needed.

The backend teammate confirms which one in the first build hour (report "Verify in the first build hour", item 6). A hosted link is a bonus, never the demo path.

## 5. Who builds the cards

The engine builds the cards, including ranking by priorities and constraints. Backend and frontend only display them. An LLM, if one is used, only narrates computed evidence and never decides.

## 6. Candidate demo points

Names only. Choosing coordinates and checking them in imagery is Step 1, after the opening.

| Hazard | Primary | Backup |
|---|---|---|
| Coastal salinity, Chattogram | Anwara upazila | Banshkhali upazila |
| Drought, northwest Barind tract | Godagari upazila, Rajshahi | Tanore upazila, Rajshahi |

Each point must sit on cropland, not a pond, river or village (Step 1 check). The two points form the "two regions, two hazards" demo pair.
