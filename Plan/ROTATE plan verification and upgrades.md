# Fix ROTATE's method before adding features

**Short answer: ROTATE's plan is mostly correct and closely matches the challenge, but it is not yet complete, and it is not yet safe to build exactly as written.** The core idea holds up against the official Field Shift statement: it compares at least three rotation strategies, one of them the farmer's existing rotation, and each card gives why it was suggested, the evidence, benefits, information gaps and risks for local review. The data choice also holds up: NASA POWER plus MODIS NDVI. The plan and the two Claude Docs have four kinds of problem. First, **three method errors that a judge could catch.** The tool implies it knows the coming season when it can only match the weeks *before* the decision. The "4 of 5 analogs agree" confidence happens about 37.5% of the time by pure chance. Warming trends can inflate the backtest score. Second, **several data facts are wrong or unconfirmed.** POWER's solar data starts in 1984, not 1981. POWER's rainfall source label is unconfirmed. Terra and Aqua MODIS are ending, and NASA's own pages give conflicting dates. Third, **the plan misses several cheap Relevance items** that the statement names: heat stress, extreme rain, soil moisture, water balance, forage value, income, infiltration, a map, and a comparison of methods. Fourth, **some compliance details would be wrong as written.** The plan says "no AI used" although the team used Gemini and Claude to plan. It has no licence file, and it does not say "not endorsed by NASA". All of these can be fixed inside the existing schedule. The biggest change is to the engine: use Ledoit-Wolf covariance, season-to-date matching with detrended temperature, a confidence score that states its chance rate, and an MSE skill-score backtest run on Day 1 evening rather than "if time". Several official pages could not be read live by the researchers (details below), so dates, the project-page submission window and the POWER response format must be confirmed by the team on the day.

## The verdict in five sentences

The **challenge fit is strong**. The strategy-card structure copies the statement's most specific ask almost word for word, and that is ROTATE's best Relevance asset ([challenge Details tab, third-party transcription](https://github.com/hendrixxD/FieldDynamics-Lab/blob/main/docs/first-principle-validative-measure.md)). The **science is sound in shape but weak in its claims**: analog matching with Mahalanobis distance is an established method, but the plan has not yet stated what it can and cannot know, has not tested confidence against chance, and has not separated trend from signal. The **NASA data plan is right**, with five fixes: start the solar data at 1984, read the rainfall source from the POWER response header, flag MODIS data from 2025 onward, treat NDVI as landscape-scale, and keep an NDVI fallback route ready. The **Bangladesh agronomy is mostly right**, with three fixes: use whole-season salinity tolerance (not seedling figures) for varieties, take rotation options from the BRRI national pattern table, and label pest and organic-matter benefits as weakly evidenced. The **delivery plan is good** (pre-cached data, fixtures, fallbacks). It needs one firm data contract with a `schema_version`, an offline engine, and a check on whether the NASA project page can even be submitted before 09:00 on Day 2.

## Terms used in this report

| Term | Plain meaning |
|---|---|
| Analog year | A past year whose weather looked like this year's. ROTATE shows what happened next in those years. |
| Feature | One number per year that the matching uses, such as "total rain in the 60 days before the decision". |
| z-score | A number rescaled so that 0 = the average year and 1 = one standard deviation above it. |
| Covariance matrix | A table of how features move together (for example, rainy periods are also humid). |
| Mahalanobis distance | A "how different are these two years" score that accounts for features moving together, so that it does not double-count them. |
| Ledoit-Wolf shrinkage | A safer way to estimate the covariance when you have few years. It pulls noisy values toward a simple average. |
| NDVI | Normalized Difference Vegetation Index: a satellite greenness number from about −0.2 to 0.9. Higher means more green vegetation. |
| MOD13Q1 | NASA's MODIS (Terra satellite) 250 m, 16-day NDVI product. MYD13Q1 is the Aqua twin. |
| Reanalysis | A weather model run that absorbs past observations. It is not a direct measurement at your field. |
| Backtest / LOYO | Leave-one-year-out testing: hide one year, predict it from the others, repeat for every year. |
| MSE skill score | 1 − (error of the method ÷ error of the plain average). Above 0 means the method beats the average. |
| Climatology | The "plain average of other years" baseline. |
| SAAO | Sub-Assistant Agriculture Officer: the government extension officer at block level in Bangladesh. |
| dS/m | Unit of soil salinity (electrical conductivity). Higher means saltier. |

## What the researchers could and could not check

The researchers could not reach some sources directly, so **parts of this report rest on secondary copies**, and these are marked. The challenge-rules researcher could not fetch any spaceappschallenge.org page: robots rules blocked automated fetching, the proxy refused the domain, and the web archive was blocked too. The 2026 Field Shift statement used here therefore comes from **a verbatim transcription of the official Details tab, captured 30 October 2026, which another team published on GitHub** ([FieldDynamics-Lab transcription](https://github.com/hendrixxD/FieldDynamics-Lab/blob/main/docs/first-principle-validative-measure.md)). A second researcher did reach some official pages through a summarising fetcher. These were the 2026 landing page, the Participant Terms (still the **2025** version), the Project Submission Guide (**2025** edition) and the Judging & Awards Guide (**2024** edition) ([Space Apps 2026](https://www.spaceappschallenge.org/2026/); [Participant Terms](https://spaceappschallenge.org/legal); [Project Submission Guide](https://www.spaceappschallenge.org/resources/project-submission-guide/); [Judging guide](https://spaceappschallenge.org/resources/judging-awards-guide)). **No live NASA POWER request succeeded**: the proxy refused `power.larc.nasa.gov`. POWER endpoint paths, parameter IDs, the fill value and the response shape therefore come from documentation and background knowledge, not from a test call. The Bangladesh local sites render with JavaScript and returned no content. The Chattogram local page was read only in the earlier fact check, and it is **user-generated and contradicts itself**.

So the team must confirm these items themselves, ideally from official pages or the Local Lead: the local event dates (13–14 Nov), the venue, every local deadline, the "do not begin work" rule and its exact source, the Field Shift **Resources tab** (which opens on the event day and may list specific NASA products), the AI-disclosure field on the 2026 project page, the 2026 licence and NASA-branding rules, the team-size cap, and the live POWER and AppEEARS response formats. Section "Questions for the Local Lead" below turns this into a checklist.

## Gap table: what is OK, partial, missing or wrong

Priority key: **P0** = must be done before the 240-second video (Day 1, 18:30). **P1** = must be done before the NASA project page is submitted. **P2** = stretch or roadmap; name it but do not build it unless P0 and P1 are done. "Plan" means team plan v2 plus the two Claude Docs (engine plan, rev 14; implementation plan, rev 9).

### Challenge statement and rules

| Requirement or issue | Status | Fix | Priority |
|---|---|---|---|
| Compare ≥3 strategies including the existing rotation; each with why, evidence, benefits, gaps, risks ([transcription](https://github.com/hendrixxD/FieldDynamics-Lab/blob/main/docs/first-principle-validative-measure.md)) | OK | Keep. The statement says "at least", so a 4th card is allowed but optional | P0 |
| Support, not replace, farmer judgment; "highlight where human judgment is particularly important" | Partial | Keep the reminder on every screen, and **rank** the review flags (high/medium/low need for SAAO review) instead of flagging everything equally | P1 |
| Patterns named: temperature, rainfall, vegetation stress | OK | — | — |
| Heat stress, extreme precipitation | Missing | Add two "Derived" counts from POWER daily data: days with Tmax ≥ 35 °C and days with rain ≥ 50 mm in the season. Both thresholds are suggestions to confirm before they go on screen | P1 |
| Soil moisture, evaporation / water balance | Missing | Cheapest: add POWER's soil-wetness parameter (GWETROOT, name **unverified**; check the POWER parameter list) labelled "model output". Optional: rainfall minus a Hargreaves reference ET, labelled "Derived". SMAP stays stretch | P2 (P1 if POWER has it) |
| Long-term water trends | Missing | Show a 1981–present seasonal rainfall trend with a significance test. Name GRACE/GRACE-FO groundwater as roadmap | P2 |
| Frost risk | N/A | One line in the limits panel: frost is not a main lowland hazard in Bangladesh, so it was left out on purpose (general knowledge; check cold injury to Boro seedlings in the northwest before saying "never") | P1 |
| Farmer priorities: water use, N-fixing, erosion, organic matter | Partial | Make these selectable on the priority dial, not only listed as benefits | P0 |
| Forage value, market suitability / supplemental income, improve infiltration | Missing | Add three rule-table columns (forage, income note, infiltration/soil structure). Prices go under "information gaps", never as claims | P1 |
| Bare-field times, vulnerable seasons | Partial | The NDVI timeline exists in the plan but is scheduled **after** the video. Show it in the video if NDVI has arrived by 16:30; otherwise label it "planned". Tie each stress season to a hazard (for example, late-Boro salinity) | P0/P1 |
| Explain terms: ET, soil-moisture anomaly, NDVI, frost risk, water balance | Partial | Five-entry glossary (English, with Bangla labels if possible) | P1 |
| Satellite vs ground data, **and how combining both may improve accuracy** | Partial | Add one sentence on combination: a farmer's or SAAO's measured salinity (EC) plus a station rainfall check would ground-truth the NASA layers (roadmap) | P1 |
| "Compare different SI or statistical approaches" | Partial | Make the backtest a 3-way comparison: Mahalanobis analogs vs standardised Euclidean analogs vs climatology | P1 |
| Explain uncertainty | Partial | Analog agreement **plus its chance rate**, plus the backtest skill as a second uncertainty measure | P0 (wording), P1 (skill) |
| Harmonise datasets of different resolution | Partial (implicit) | Show the harmonisation step in one diagram line: POWER cell about 55 × 65 km, MODIS pixel 250 m, both summarised to the same season calendar | P1 |
| Interactive map | Missing | Leaflet click-to-select map of Bangladesh with the cached sites marked. It also proves the national scope | P1 |
| Field-level vulnerability zones (erosion, flooding) | Missing | Roadmap: SRTM elevation for low-lying zones | P2 |
| Explain N-fixing, cover, deep-rooting, drought-tolerant crops | Partial | Four one-line explainers from the science translator | P1 |
| "Do not begin work before the hackathon" | Partial (source wrong) | The plan attributes it to the challenge page. The transcription of the Details tab does not contain it. The FAQ does ("not allowed to begin working on the challenges prior to the hackathon", per the earlier fact check) ([Participant FAQs](https://www.spaceappschallenge.org/resources/participant-faqs/)). Cite the FAQ and keep the strict reading | Before event |
| Use of AI disclosure | **Wrong** | The plan says "if none, say rule-based". The team used Gemini and Claude for planning and research, so that statement would be false. AI tools are allowed, but teams must "clearly indicate where and how AI tools were utilized" ([nasa/spaceapps Discussion #1273, 2025](https://github.com/nasa/spaceapps/discussions/1273)). The implementation plan's line "The Use of AI section names [Mahalanobis]" is a category error: Mahalanobis is statistics, so describe it under Methods | P1 |
| Open-source licence | Missing | Add a LICENSE file (MIT or Apache-2.0). The 2025 terms say content must be open source or freely available, that NASA defaults to Apache 2.0, and that awards can be removed from teams that do not cite resources ([Participant Terms](https://spaceappschallenge.org/legal), 2025 version) | P1 |
| NASA branding / endorsement | Missing | No NASA "meatball", "worm" or Space Apps logo used as if the tool were NASA's. Footer: "Uses NASA data. Not endorsed by NASA." NASA data policy forbids implying endorsement ([Earthdata Data Use Policy](https://www.earthdata.nasa.gov/earth-observation-data/data-use-policy)) | P1 |
| Global demo ≤30 s video (or ≤7 slides), English subtitles, public links, all form fields in English | OK | Keep. Exceeding the limits makes a project ineligible for Global Judging ([Project Submission Guide](https://www.spaceappschallenge.org/resources/project-submission-guide/), 2025 edition). Keep a 7-slide PDF as backup | P1 |
| Judging rubric "1–20 per criterion + Teamwork/UX/NASA data 0–5 + three 0/1 checks" | Unverified | The five criterion names are confirmed ([Isa Town 2026 page](https://www.spaceappschallenge.org/2026/local-events/isa-town/)). No source was found for the scale or weights. Treat the rubric as the local Bangladesh sheet only | — |
| Competitor count ("at least four other repos") | Out of date | Different searches found **10 to roughly 40** public 2026 Field Shift repos, including Bangladeshi ones. RotaShift already runs Mann-Kendall/Levene trend tests ([RotaShift](https://github.com/XtremeseOISHEE/RotaShift)). The backtest skill score remains the clearest differentiator | — |

### Science and method

| Requirement or issue | Status | Fix | Priority |
|---|---|---|---|
| "Past seasons that most resemble current conditions" implies a forecast | **Wrong (wording and logic)** | At the decision date, the coming season has not happened. Match only the **60 days before the decision**, then show what happened *afterwards* in the analog years. Say plainly: "This tool does not forecast the coming season" | P0 |
| Confidence = "how many of k=5 analogs agree" | **Wrong as stated** | With random years, ≥4 of 5 agreeing happens 12/32 = **37.5%** of the time; 5 of 5 happens 6.25%. Show the chance rate next to the score, use distance weights, and check calibration in the backtest | P0 |
| Covariance estimator | Conflict between docs | Use Ledoit-Wolf (see "Conflicts resolved") | P0 |
| Warming trend | Missing | Detrend temperature features inside each fold. Without this, recent years look alike for trend reasons and the skill looks better than it is ([Wulff et al. 2022](https://consensus.app/papers/details/25eea75d76445e9dbda9cf4d09bfa082/), abstract only) | P0 |
| Skill formula `1 − RMSE_a/RMSE_b` | Partial | Use the standard **MSE skill score** `1 − MSE_a/MSE_clim`, plus a random-year permutation p-value and a tercile hit rate | P1 |
| Backtest scheduled "Day 2, if time" | **Wrong priority** | It is the Validity proof. Move it to Day 1 evening as a must-have | P1 |
| "Is this analog actually close?" | Missing | Flag analogs whose distance exceeds the 95% chi-square cutoff (for 3 features, √7.81 ≈ 2.80) | P1 |
| NDVI predictand = whole curve | Partial | Predict one number per year (Boro peak-season NDVI anomaly). A curve error can be a secondary check | P1 |
| "Bare-field" from low NDVI | Partial | Low NDVI also means **flooded or newly transplanted** fields ([Gumma et al. 2014](https://oar.icrisat.org/7640/7/Mapping%20seasonal%20rice%20cropland%20extent%20and%20area%20in%20the%20high%20cropping.pdf)). Label it "low-vegetation window (bare, flooded or newly planted)" | P1 |
| NDVI as salinity evidence | Risk of overclaim | Evidence linking NDVI to salinity in coastal Bangladesh is weak (one Barguna study found R² ≤ 0.022 for salinity indices) ([Hossen et al. 2022](https://consensus.app/papers/details/d27659c6f6a25b70a6da0fba7512d2cc/), abstract only). Wording: "NDVI is consistent with, but cannot diagnose, salinity stress" | P0 |

### NASA data

| Requirement or issue | Status | Fix | Priority |
|---|---|---|---|
| POWER "from 1981" for all four features | **Wrong for solar** | Solar fluxes start **1 Jan 1984** (GEWEX SRB, then CERES) ([POWER data sources](https://power.larc.nasa.gov/docs/methodology/data/sources/)). Drop solar from the default features, or start the pool at 1984 | P0 |
| "POWER rainfall = MERRA-2" (the engine plan's evidence JSON hard-codes this) | Unverified | The POWER sources page now also lists GPM IMERG precipitation (0.1°, from 2001) ([POWER data sources](https://power.larc.nasa.gov/docs/methodology/data/sources/)). Read the source from the live response header and label it from that | P0 |
| Latest POWER days | Missing caveat | The newest ~month of weather comes from GEOS FP-IT, and the last 3–4 months of solar from FLASHFlux ([POWER data sources](https://power.larc.nasa.gov/docs/methodology/data/sources/)). This year's row is built from a different model than the history: say so in the limits panel | P1 |
| POWER fill value | Unverified | Read it from the response header (historically −999; **unverified**). Convert it to NaN before anything else | P0 |
| MODIS continuity | Missing | Terra/Aqua drift and end of mission affect data from 2025 onward. Backtest on 2001–2024, flag 2025+, and name VIIRS VNP13A1 (500 m, from 2012) as the successor | P1 |
| AppEEARS may sit "pending" | Partial (fallback exists) | Add the ORNL DAAC subset service as a second route (no login stated in its docs, 10 dates per call) ([ORNL MODIS web service](https://modis.ornl.gov/data/modis_webservice.html)) | P0 (submit) / P1 (fallback) |
| Pixel vs farm size | OK (limits panel planned) | One 250 m pixel ≈ 5–6 ha ≈ about 10 average holdings of about 0.52 ha ([BBS Agriculture Census 2019](https://bbs.portal.gov.bd/sites/default/files/files/bbs.portal.gov.bd/page/c645bd51_3cb5_4f53_86f9_7d29244caa4e/2022-12-26-08-36-394361bc904a7651ef763a4ff8033b67.pdf)). Check that the demo point sits on cropland, not a shrimp pond or a village | P0 |
| Monsoon cloud | Partial | Filter by quality flag. Feature Boro (dry season), where NDVI is most reliable ([Mosleh & Hassan 2014](https://www.ucalgary.ca/sites/default/files/teams/40/025.Mosleh_et_al_RS_14.pdf)) | P1 |
| Dataset citations | Partial | Use POWER's referencing text with the real version and access date ([POWER Referencing](https://power.larc.nasa.gov/docs/referencing/)), and the MOD13Q1.061 citation from the AppEEARS bundle README | P1 |

### Bangladesh agronomy and local data

| Requirement or issue | Status | Fix | Priority |
|---|---|---|---|
| "Current rotation" input | Partial | Use the BRRI national top-15 pattern list (about 70% of net cropped area; Boro–Fallow–T.Aman alone 26.9%) as the dropdown ([Nasim et al. 2017](https://banglajol.info/index.php/BRJ/article/view/38195/25980)) | P0 |
| Salt-tolerant variety thresholds | Partial | Drive filters by **whole-season or reproductive-stage** tolerance (about 8–10 dS/m for the best Boro lines), never the seedling figures of 12–15 dS/m ([Daily Star, 20 June 2026](https://epfs.thedailystar.net/TDS/2026/06/20/Bangladesh/MAI/5_16/7900c92455a208d5_16.pdf); [Debsharma et al. 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC10810675/)) | P0 |
| National scope: drought and flood hazards | Partial | The implementation plan's hazard list is "general knowledge". Add sourced variety rows: drought BRRI dhan56, 57, 66, 71, 83; submergence BRRI dhan51, 52, 79 ([Rahman et al. 2021, BRJ](https://www.banglajol.info/index.php/BRJ/article/view/53450)). No numeric thresholds were found for the drought lines | P1 |
| Water-use benefit | OK, now sourced | Boro net irrigation need ≈ 676 mm, about 2× wheat, maize, potato and sunflower, about 3× pulses ([Mainuddin et al. 2015](https://link.springer.com/doi/10.1007/s00271-014-0451-3)) | P0 |
| N-fixation, organic matter, pest-cycle benefits | Partial | N: lentil about 50 kg N/ha on farmers' fields in the IGP ([Saraf et al.](https://core.ac.uk/download/211014792.pdf)). Organic matter: weak and confounded with residue retention. Pest cycles: **no Bangladesh numbers found**; label "general agronomic principle" | P0 (labels) |
| Salinity data | Partial | SRDI's newest national survey is from 2009. Salinity is a user-chosen class with the SRDI 2009 class as a dated default. The class boundaries used here are **unverified**: confirm them in the SRDI 2010 PDF | P0 |
| BMD station data | Not usable | It is sold, and redistribution is restricted ([BMD data portal](https://dataportal.bmd.gov.bd/)). Do not put it in an open repo | — |
| World Bank "median +26% by 2050" | OK with fix | It is a 17 Feb 2015 feature story, likely about **river** salinity ([World Bank feature](https://www.worldbank.org/en/news/feature/2015/02/17/salinity-intrusion-in-changing-climate-scenario-will-hit-coastal-bangladesh-hard)). Cite it with its date, and never apply it to one field's soil | P0 |

## Conflicts between sources and documents, each with one recommendation

| Conflict | What each source says | Recommendation |
|---|---|---|
| Covariance: plain vs Ledoit-Wolf vs MinCovDet | Engine plan: plain covariance, skip MCD. Implementation plan: "try MinCovDet if it works in one try". Method research: Ledoit-Wolf. scikit-learn says the empirical covariance gives an inaccurate precision matrix, Ledoit-Wolf minimises MSE, and MinCovDet fits on a subset of "good" observations ([scikit-learn covariance guide](https://scikit-learn.org/stable/modules/covariance.html)) | **Use `sklearn.covariance.LedoitWolf` as the default**, refit inside every backtest fold, and log `shrinkage_`. **Drop MinCovDet**: it down-weights the extreme years ROTATE cares about. Keep **standardised Euclidean** (covariance = identity) as the robustness check and emergency fallback, and report the overlap ("4 of 5 analogs are the same under both"). Do not rely on `pinv`: it stops the crash but does not reduce the noise |
| Skill formula | Engine plan: `1 − RMSE_analog/RMSE_baseline`. Fact check and method research: `1 − MSE_analog/MSE_clim` | **Use the MSE skill score, `SS = 1 − MSE_analog/MSE_clim`**, everywhere, by that name. The two differ: an RMSE ratio of 0.9 gives 0.10 on the RMSE form but 0.19 on the MSE form |
| 240-second video deadline | Memory/summary: 1 Nov. Chattogram page: 1 Oct and 1 Nov **pre-event** 240 s rounds. Run of show: Day 1 **13 Nov 18:30** | **Work to 13 Nov 18:30** for the event video. 1 Nov was a pre-event round that has already passed. Ask the Local Lead **today** whether missing it affects eligibility |
| 30-second video and project page | Chattogram day plan: 09:00 Day 2. Key-dates list: 12:00 Day 2. Global (2026 landing page as fetched): submission **opens Sat 14 Nov 09:00 and closes Sun 15 Nov 23:59 local time** ([Space Apps 2026](https://www.spaceappschallenge.org/2026/)) | **Work to 09:00 Day 2 for the video and all page content.** New risk: if the NASA form only opens at 09:00 on 14 Nov, the team cannot press Submit before 09:00. Ask the Local Lead what "submitted by 09:00" means. Prepare all text in a document, then paste and submit the moment the form opens |
| Event dates | Chattogram page: 13–14 Nov (user-generated). Rajshahi page: 14–15 Nov. Global: 14–15 Nov | **Plan for 13–14 Nov** and confirm. Also ask whether "do not begin work until the hackathon begins" means the **local** start (13 Nov) or the **global** start (14 Nov) |
| Solar start year | Plan: POWER from 1981. POWER sources page: solar from 1 Jan 1984 | **Default feature set without solar** (rain, Tmin, RH), so the pool keeps 1981+. If solar is added, start the pool at 1984 |
| MODIS end dates | MODIS Land news (updated Nov 2025): Terra Dec 2025, Aqua Aug 2026 ([MODIS Land News](https://modis-land.gsfc.nasa.gov/news.html)). Earthdata alert (May 2025): shutdown begins "late 2026/early 2027" ([Earthdata](https://www.earthdata.nasa.gov/data/alerts-outages/transition-from-modis-viirs)). NASA Science (updated 20 Mar 2026): end of science Terra **Feb 2027**, Aqua **Sep 2027** ([NASA Science](https://science.nasa.gov/science-research/earth-science/terra-the-end-of-an-era/)) | **Use the NASA Science dates (most recently updated)** and say "approximately". It does not matter much for the method: history (2000–2024) is fine. Flag 2025+ composites (drift reported, "significant impacts observed in late 2024") ([LDOPE issue 1254](https://landweb.modaps.eosdis.nasa.gov/displayissue?id=1254)) and name VIIRS as continuity |
| "Do not begin work" source | Plan: challenge page. Transcription: not on the Details tab. FAQ: yes. 2025 terms: no such clause | **Cite the FAQ, follow the strict reading**, and keep a git history that begins at the opening |
| Where POWER pulls happen | Implementation plan: "anywhere in Bangladesh, POWER pulls run on demand". Engine plan: engine reads only cached files | **Engine reads only files.** A separate fetch script can add a new site on demand during development, but the judged demo uses cached sites only |
| Primary user | Statement: farmers. Research: SAAOs use phones almost universally but have low overall ICT use ([AgEcon Search 357133](https://ageconsearch.umn.edu/record/357133)) | **Keep "farmers" as the user, and show the demo as an SAAO sitting with a farmer.** That matches the statement and Bangladesh reality without changing the scope |
| Quality layer name | Engine note: `_250m_16_days_VI_Quality`. Method note: SummaryQA = "pixel reliability" | **Request both `_250m_16_days_pixel_reliability` and `_250m_16_days_VI_Quality`**, filter on pixel reliability ∈ {0, 1}, and confirm the meanings with `GET /quality/...` in hour 1 |

## Improved team plan

### Scope in one paragraph

ROTATE is **built for all of Bangladesh and demonstrated on two cached sites**: a coastal salinity site in Chattogram district (for example Anwara or Banshkhali; pick the exact point on cropland in imagery) and a northwest Barind drought site. A small map shows the sites. The demo decision is **real and timely**: the event falls in mid-November, the start of the Rabi and Boro decision window. Rabi crops "perform better when sown/planted after 1 November", and Boro seedbeds are sown in October–November ([Banglapedia "Crop"](https://en.banglapedia.org/index.php/Crop); [FEWS NET](https://help.fews.net/fde/bangladesh-data-book)). The pitch can therefore say "this is the decision farmers are making this week". Never claim the tool is validated nationwide. Out of scope, named as roadmap: multi-year projection, SMS or voice, a mobile app, crop models (DSSAT/APSIM), data fusion (ESTARFM), SMAP, ECOSTRESS, GRACE, SRTM, and an HLS 30 m field layer.

### What each pipeline stage shows

| Stage | Shows on screen | Label |
|---|---|---|
| 1. NASA observation | The 60-day pre-decision weather for this year vs the site's normal range (rain, Tmin, humidity), extreme-day counts, and the MODIS NDVI season curves of the analog years with low-vegetation windows marked. Each value names its source product, taken from the response header | "Observed (NASA)". Reanalysis is noted as such |
| 2. Local information | Current rotation (BRRI top-15 dropdown), main hazard (salinity, drought, flood), salinity class (with the SRDI 2009 default, dated) | "Local information, not NASA" |
| 3. Priorities and constraints | Priority dial: save water, soil and nitrogen, salinity resilience, yield stability, extra income, forage. Constraints: water availability, equipment, market preference | "Your choices" |
| 4. ROTATE's reasoning | Analog years with distance and a "close match?" flag; agreement with its chance rate; backtest skill for this site and season; the rule-table rows used, with citations | "Derived (ROTATE's own method)" |
| 5. Output | Three cards: existing + two alternatives (optional 4th). Each has strategy, why, evidence (tagged Observed/Derived/Scenario), benefits (cited), gaps, ranked review risks, "needs local review" | Mixed, with tags on every item |

### Roles, with owners for the new items

| Role | Owns (new items in bold) |
|---|---|
| Engine (the user) | Python package, fetch scripts, cached data, analogs, confidence, NDVI cleaning, **backtest as Day 1 evening must-have**, **schema + fixtures in hour 1**, **provenance block**, limits-panel facts, data-sources list |
| Backend | Calls the engine (library call, CLI or static JSON). A thin web wrapper if needed. Runs the demo locally on the presenting laptop |
| Frontend | Inputs, **map**, cards, NDVI chart (raw points plus smoothed line, gaps shown), **chance-rate text**, glossary, Bangla labels |
| Science translator | `rules.json` (with **whole-season tolerance**, forage, income, infiltration columns), citations, explainers, **ranked review flags**, wording check ("compare", never "best") |
| Storyteller / designer | 240 s and 30 s videos, project page, **AI disclosure (Gemini, Claude and any in-event tools)**, **LICENSE and "not endorsed by NASA" line**, minors check, final private-window link test |

### Must-have vs stretch

| Must-have (in this order) | Stretch (only after must-haves are recorded) |
|---|---|
| 1. Analog engine on POWER, season-to-date, Ledoit-Wolf, detrended, with honest confidence | What-if slider (rainfall/temperature shift → "Scenario") |
| 2. Three cards from `rules.json`, existing rotation first | Scenario mode: dry / normal / wet season terciles |
| 3. Priority dial and constraints change the card ranking live | 4th card |
| 4. NDVI timeline (or "NDVI pending" if not arrived) | GWETROOT soil wetness and water balance (if POWER has them) |
| 5. Backtest: MSE skill score vs climatology and vs Euclidean, plus permutation p-value | Bangla narrative (labels are must-have; narrative is stretch) |
| 6. Limits panel, glossary, data sources, licence, AI disclosure | Third and later sites; HLS 30 m panel; MYD13Q1 (Aqua) interleave |
| 7. Map with the two cached sites | 3×3-pixel NDVI window via ORNL |

## Improved engine implementation plan

### Contract choice: library first, CLI always, static JSON as the final fallback

The engine is **a plain Python package whose public functions return pydantic models**, plus a CLI that writes the same JSON. A web wrapper is the backend teammate's job, and only if their stack is not Python. The engineering research installed and ran the needed APIs in a clean Python 3.13 environment: pydantic model → `model_json_schema()` → `jsonschema` validation, `requests_cache.CachedSession`, `tenacity.retry`, and scikit-learn covariance classes. Current releases on 5 Nov 2026 included pydantic 2.14.2, jsonschema 4.26.0, scikit-learn 1.9.1, pandas 3.1.1, numpy 2.5.4 (needs Python ≥ 3.12), requests-cache 1.3.3, tenacity 9.2.1 and pytest 9.2.0 ([PyPI numpy](https://pypi.org/project/numpy/); [PyPI pydantic](https://pypi.org/project/pydantic/); [PyPI scikit-learn](https://pypi.org/project/scikit-learn/)). **Pin Python 3.12**, then freeze exact versions with `pip freeze` once the engine runs. Do not copy these version numbers blindly; pin whatever you actually install at the event.

### Module layout

```text
rotate/                         # one public repo, first commit after the official opening
├─ engine/
│  ├─ pyproject.toml            # package "rotate_engine", python = ">=3.12"
│  ├─ src/rotate_engine/
│  │  ├─ __init__.py            # exports list_sites, find_analogs, build_cards, ndvi_for_years, run_backtest
│  │  ├─ __main__.py            # CLI: python -m rotate_engine cards --site ctg_anwara --date 2026-11-13 --out cards.json
│  │  ├─ config.py              # constants: K=5, WINDOW_DAYS=60, FEATURES, thresholds, SCHEMA_VERSION="1.0"
│  │  ├─ models.py              # pydantic models = the contract (CardSet, AnalogResult, NdviSeries, BacktestResult)
│  │  ├─ io.py                  # read data/sites.json, data/power/*.csv, data/ndvi/*.csv, rules/rules.json (files only)
│  │  ├─ seasons.py             # decision dates, window dates, season-year labelling (Boro year = harvest year)
│  │  ├─ features.py            # daily -> one row per year; log1p rain; extreme-day counts
│  │  ├─ analogs.py             # z-score, detrend, LedoitWolf, distances, top-k, weights, Euclid overlap, close flag
│  │  ├─ ndvi.py                # QA filter, scale, day-of-year placement, gap marking, smoothing, anomalies, low-veg windows
│  │  ├─ confidence.py          # weighted agreement + exact chance rate + sentence
│  │  ├─ backtest.py            # LOYO, SS_MSE, permutation null, sign test, tercile hits, calibration bins
│  │  ├─ rules.py               # load/validate rules.json, pattern catalogue, alternative selection, scoring
│  │  ├─ cards.py               # assemble three cards with tagged evidence and ranked risks
│  │  └─ provenance.py          # build the provenance block from saved request/response metadata
│  ├─ tests/                    # see "Tests"
│  └─ schemas/                  # generated *.schema.json (committed)
├─ scripts/                     # network lives ONLY here
│  ├─ fetch_power.py            # cached session + retries, writes data/power/<site>.csv + data/raw/power/<site>.json
│  ├─ fetch_ndvi_appeears.py    # login, submit point task, poll, download, writes data/ndvi/<site>.csv + raw bundle
│  ├─ fetch_ndvi_ornl.py        # fallback route
│  └─ build_fixtures.py         # runs the engine for every cached site/date and writes fixtures/*.json
├─ data/  (sites.json, power/, ndvi/, raw/)     # committed so the demo works offline
├─ rules/rules.json             # science translator's table, validated by rules.py
├─ fixtures/                    # hand-written first, then regenerated from real output
├─ .env.example  .gitignore     # Earthdata credentials never committed
├─ LICENSE  README.md  DATA_SOURCES.md
```

The engine package **does not import `requests` at all**, so "works offline" is guaranteed by its structure. Only `scripts/` touches the network.

### Data contract (JSON), version 1.0

Freeze **field names** in hour 1. Values may be placeholders. A frontend breaks on renamed keys, not on changed numbers. Bump to 1.1 when you add an optional field and to 2.0 when you rename or remove a field. Every response carries `schema_version`.

```json
{
  "schema_version": "1.0",
  "engine_version": "0.1.0",
  "generated_at": "2026-11-13T15:40:00+06:00",
  "request": {
    "site_id": "ctg_anwara", "decision_date": "2026-11-13", "season": "boro",
    "mode": "season_to_date",
    "current_rotation": "boro-fallow-t_aman",
    "hazard": "salinity", "salinity_class": "slight_4_8",
    "priorities": {"water": 0.4, "soil_n": 0.2, "salinity": 0.3, "yield_stability": 0.1, "income": 0.0, "forage": 0.0},
    "constraints": {"water_availability": "low", "equipment": "none", "market": "local"}
  },
  "site": {"id": "ctg_anwara", "name": "Anwara, Chattogram", "lat": 22.2, "lon": 91.9, "hazard": "salinity"},
  "window": {"start": "2026-09-14", "end": "2026-11-11", "days_available": 59},
  "analogs": {
    "weather_pool": [{"year": 2014, "rank": 1, "distance": 1.12, "weight": 0.31, "close_match": true,
                      "features": {"rain_mm": 210.0, "tmin_c": 23.1, "rh_pct": 82.0}}],
    "ndvi_pool": [{"year": 2014, "rank": 1, "distance": 1.12, "weight": 0.33, "ndvi_anomaly": -0.04, "ndvi_status": "ok"}],
    "euclid_overlap": "4 of 5",
    "shrinkage": 0.07
  },
  "confidence": {
    "k": 5, "agree_count": 4, "direction": "below_normal", "weighted_agreement": 0.78,
    "chance_rate": 0.375, "label": "moderate",
    "sentence": "4 of 5 look-alike years had below-normal Boro greenness. Random years agree this much about 38% of the time.",
    "tag": "Derived"
  },
  "cards": [
    {"card_id": "existing", "is_existing": true,
     "strategy": {"name": "Boro–Fallow–T.Aman (current)", "slots": ["boro", "fallow", "t_aman"]},
     "why": "This is your current rotation, shown for comparison.",
     "evidence": [{"label": "Rainfall in the 60 days before the decision", "value": "38% below the 1981–2025 average",
                   "unit": "%", "source": "NASA POWER daily PRECTOTCORR (source per response header)",
                   "tag": "Observed", "analog_year": null}],
     "benefits": [{"attribute": "water", "text": "Highest irrigation need of the options shown",
                   "citation_id": "mainuddin2015"}],
     "gaps": ["Field-level salinity is not measured by any NASA product", "Local prices"],
     "risks": [{"text": "Late-season salinity in Apr–May", "review_need": "high"}],
     "score_breakdown": {"water": 0.0, "salinity": 0.3},
     "needs_local_review": true}
  ],
  "ndvi_status": "ok",
  "warnings": ["Current-year weather comes from near-real-time analysis (GEOS FP-IT), not MERRA-2"],
  "provenance": {
    "power": {"endpoint": "<exact URL used>", "parameters": ["PRECTOTCORR","T2M_MIN","T2M_MAX","RH2M"],
              "community": "AG", "accessed": "2026-11-13", "header_sources": ["<copied from response>"], "fill_value": "<from header>"},
    "ndvi": {"product": "MOD13Q1.061", "layers": ["_250m_16_days_NDVI","_250m_16_days_pixel_reliability","_250m_16_days_VI_Quality"],
             "route": "appeears", "task_id": "<id>", "accessed": "2026-11-13", "sha256": "<bundle file hash>"}
  },
  "disclaimer": "ROTATE helps you compare options. It does not forecast the season and does not replace local agricultural advice."
}
```

The backtest has its own model: `{schema_version, site_id, season, years_tested, k, predictand, ss_mse, mse_analog, mse_clim, ss_mse_euclid, anomaly_corr, tercile_hit_rate, beat_clim_count, sign_test_p, permutation_p, n_permutations, calibration_bins, verdict_text, excluded_years}`. `rules.json` rows carry: `crop`, `slot`, `season`, `hazards_fit`, `salinity_whole_season_max_dS_m`, `salinity_seedling_dS_m`, `water_rel_boro`, `n_fix_kg_ha`, `organic_matter`, `pest_break`, `forage`, `income_note`, `infiltration`, `duration_days`, `varieties`, `evidence_strength` (strong / weak / principle-only) and `citations`. Use pydantic `ConfigDict(extra="forbid")` and `Literal["Observed","Derived","Scenario"]` for tags, so that a typo fails loudly. The engineering research verified both in its test run.

### Algorithm, step by step, with parameters

**Step 0: Data loading.** Read `data/power/<site>.csv` (daily, local solar time by default; the R client documents `time_standard` LST as the default ([nasapower get_power](https://docs.ropensci.org/nasapower/reference/get_power.html))). Replace the header's fill value with NaN. Request PRECTOTCORR, T2M_MIN, T2M_MAX, RH2M and, optionally, ALLSKY_SFC_SW_DWN and GWETROOT (all names **unverified** until the hour-1 test). That is far below the 20-parameter limit per daily point request that the R client documents.

**Step 1: Season and window.** For the Boro demo, the decision date is the event day (13 Nov). The window is the **60 days ending at the last valid day before the decision** (POWER latency is about 2 days). For every past year y, use the same calendar window. Label Boro seasons by **harvest year**: features from Sep–Nov of year y−1 pair with Boro NDVI in Jan–May of year y. If the window has fewer than about 55 valid days, add a warning and stop. Never fill silently.

**Step 2: Features (default p = 3).** Use `rain = log1p(total PRECTOTCORR over the window)`, mean `T2M_MIN`, and mean `RH2M`. Do not use both T2M_MAX and T2M_MIN: they move together. Leave solar out by default (it starts in 1984 and tracks cloud and humidity). Keep features at 3–4: with about 44 years, research on small analog datasets stresses that "reducing feature-space dimension is a key requirement" ([Platzer et al. 2025](https://consensus.app/papers/details/0250c548f1bd51e890aa2188c2b0b6a9/), abstract only). Extreme-day counts (Tmax ≥ 35 °C, rain ≥ 50 mm) are **display evidence**, not matching features.

**Step 3: Detrend temperature.** For each temperature feature, fit `f = a + b·year` on the **training years only**, then use residuals for both training and target years. Do not detrend rainfall by default. Run it detrended once as a sensitivity check. An analog downscaling study used this pattern: detrend before selecting analogs, then add the trend back for display ([Merkenschlager et al. 2021](https://consensus.app/papers/details/e1e9e55e1117568eb4ecc18e346e2837/), abstract only).

**Step 4: Standardise.** Compute z-scores with the training-year mean and standard deviation only.

**Step 5: Covariance and distance.** `lw = LedoitWolf().fit(Z_train)`, then `P = lw.precision_` and `D = sqrt((z_x − z_y)ᵀ P (z_x − z_y))`. Compute D yourself with `P` rather than calling `.mahalanobis()`, because scikit-learn's method returns **squared** distances (from prior knowledge, not re-checked). Assert that every D is finite. Fallback: P = identity (standardised Euclidean), with a warning.

**Step 6: Two analog lists.** (a) `weather_pool`: the k = 5 nearest among all years 1981 to last year, for weather evidence. (b) `ndvi_pool`: the k = 5 nearest among Boro years that have NDVI (2001–2024; 2025 flagged), for vegetation evidence and confidence. List (b) is exactly what the backtest tests. Fix k = 5 before looking at results; 5–7 is a published optimum for seasonal analogs ([Mullan et al. 2006](https://consensus.app/papers/details/09c2fb4c1b3358a48569dc8fb9ef8ba7/), abstract only). Sort ties by (distance, year).

**Step 7: Weights and closeness.** Use kernel weights `w_i = exp(−D_i² / (2h²))`, with h = the median of the k distances, normalised to sum to 1. Weighted analog ensembles beat a single analog in published tests ([Zhao & Giannakis 2014](https://consensus.app/papers/details/3901b3d96fb3582d85538a8813179b2e/), abstract only). Mark `close_match = false` when D exceeds √χ²(p, 0.95). That is about 2.80 for p = 3 and about 3.08 for p = 4. The idea is that D² follows a chi-square distribution if the features are roughly normal ([USDA review citing Mahony et al. 2017](https://research.fs.usda.gov/download/treesearch/69387.pdf)). If even the nearest analog is not close, say "no close look-alike year this time".

**Step 8: Confidence.** Each analog in list (b) votes on the sign of its Boro NDVI anomaly. Report the count, the weighted agreement `A = Σ w_i·1[sign = majority]`, and the **exact chance rate** from a binomial with p = 0.5. For k = 5, that is 37.5% for ≥4 agreeing and 6.25% for 5 of 5. Label agreement "high" only at 5/5, "moderate" at 4/5 and "split" otherwise. If NDVI has not arrived, vote instead on the **observed post-decision season rainfall anomaly** of the analog years (POWER). That keeps a working confidence for the Day 1 video, labelled as rainfall-based.

**Step 9: Cards.** The existing rotation is always card 1. Candidate alternatives come from the BRRI pattern catalogue (patterns that change the Boro or fallow slot) plus `rules.json` rows that pass hard filters: a hazard fit, and whole-season salinity tolerance ≥ the user's class. Above about 8 dS/m, no listed rice variety has a sourced claim of reliable yield, so the card should switch to "fallow, short oilseed, or local review". Score each candidate as `Σ priority_weight × attribute_score` and show the breakdown. Pick the top two that differ in kind (one legume or N-fixing option, one lower-water or tolerant option). The "why" sentence is a template that joins the analog evidence and the user's top priority. Every benefit carries a `citation_id`. Every card has `needs_local_review: true` and ranked risks.

**Step 10: Scenario (stretch).** The what-if slider shifts this year's raw features (for example, rain −20%), then reruns steps 4–8, and every output item is tagged "Scenario". Alternatively, scenario mode selects analogs from years whose **in-season** rain fell in the dry, normal or wet tercile.

### NDVI processing

Request MOD13Q1.061 layers `_250m_16_days_NDVI`, `_250m_16_days_pixel_reliability` and `_250m_16_days_VI_Quality` (names from the [AppEEARS API](https://appeears.earthdatacloud.nasa.gov/api/) documentation), plus the composite day-of-year layer (exact layer name **unverified**; read it from `/product/MOD13Q1.061`). Submit **all sites in one point task**, dates 01-01-2000 to today. AppEEARS returns HTTP 202 and a `task_id`, and status moves through pending, processing, done or error. Its doc gives no typical processing time, and forum users report tasks stuck for a day or more ([Earthdata Forum](https://forum.earthdata.nasa.gov/viewtopic.php?p=24485)). Poll every 30–60 s at most, because HTTP 429 means "slow down". Cleaning:

1. Keep pixel reliability 0 (good) and 1 (marginal). Drop 2 (snow/ice) and 3 (cloudy). These meanings and the 0.0001 scale factor are documented for MOD13Q1 v061 in the GEE catalogue ([GEE MOD13Q1](https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD13Q1)); confirm them with AppEEARS `/quality`.
2. Place each value on its actual acquisition day, not the composite start date.
3. Break the line across gaps longer than 32 days (two composites) and label them "cloud gap".
4. Smoothing is optional. Use Savitzky-Golay (window 5, order 2) on gap-free runs, or a weighted Whittaker (λ about 10–100). A global comparison found no clear winner and warned that methods work poorly in monsoon regions ([Liu et al. 2017](https://consensus.app/papers/details/7f4f18b458d253dcb4d58228cf20303e/), abstract only). Always plot raw points with the line.
5. The predictand is the **Boro peak-window mean NDVI** over roughly DOY 81–112 (mid-March to mid-April), the Boro peak reported for MOD13Q1 in Bangladesh ([Mosleh & Hassan 2014](https://www.ucalgary.ca/sites/default/files/teams/40/025.Mosleh_et_al_RS_14.pdf)), minus its linear trend fitted on training years.
6. A low-vegetation window is smoothed NDVI < 0.3 for ≥ 2 consecutive composites. This threshold is an assumption to calibrate on your own curves.
7. Report the share of composites that passed QA, per month. That is useful evidence in itself, since no published figure for Bangladesh was found.

Fallback order: AppEEARS done → commit the CSV. Still pending at 16:30 → "NDVI pending" in the video. Errored → resubmit a smaller task, or use the ORNL subset service (about 60 calls per site per band for 2000–2026 at 10 dates per call; script it and cache) ([ORNL web service](https://modis.ornl.gov/data/modis_webservice.html)).

### Backtest protocol (the Validity proof)

For each Boro year t in 2001–2024 (n ≈ 24), refit everything on the other years: detrending, z-scores, Ledoit-Wolf and the NDVI trend. Find the k = 5 nearest among training years with NDVI, and predict t's NDVI anomaly as the weighted mean. Baseline = 0 anomaly (climatology). Report:

- `SS_MSE = 1 − MSE_analog/MSE_clim`
- the same score for standardised-Euclidean analogs (this is the "compare approaches" answer)
- the anomaly correlation
- the tercile hit rate (chance is 33%)
- "analogs beat climatology in N of 24 years", with a sign-test p-value
- a **permutation p-value**: the share of 1,000 runs using k random training years whose SS ≥ the observed SS (fixed random seed)
- hit rate by agreement bin (3/5, 4/5, 5/5), which tests whether "confidence" means anything

This mirrors standard practice: bootstrap cross-validation and Monte Carlo tests for seasonal analogs ([Mullan et al. 2006](https://consensus.app/papers/details/09c2fb4c1b3358a48569dc8fb9ef8ba7/)), and reliability and shift tests for analog-year crop forecasts ([Anwar et al. 2008](https://era.dpi.qld.gov.au/id/eprint/11480/1/Quality%20and%20potential%20utility%20of%20ENSO-based%20forecasts%20of%20spring%20rainfall%20and%20wheat%20yield%20in%20south-eastern%20Australia.pdf)). **Write the success wording before running it:** "SS > 0 and permutation p < 0.10 = some skill. Otherwise: no demonstrable skill, and the analog years are shown as historical examples only." Report 2025 separately. A weak result still helps if it is reported honestly. No published skill benchmark exists for this setup in Bangladesh, so the team cannot know in advance what number to expect.

### Offline caching

`scripts/fetch_power.py` uses `requests_cache.CachedSession("cache/power", backend="sqlite", expire_after=NEVER_EXPIRE, stale_if_error=True)`, a `tenacity` retry (3 attempts, exponential wait up to 10 s) and `timeout=(5, 30)`. The engineering research ran all three in its test. `only_if_cached=True` gives a true offline mode that returns 504 if the data is missing ([requests-cache docs](https://requests-cache.readthedocs.io/en/stable/user_guide/expiration.html)). Save the raw JSON response (with its header) next to the CSV for provenance. Keep the AppEEARS token only in `.env` and memory: it lasts about 48 h, and download links redirect to S3 links valid for 48 h ([AppEEARS API](https://appeears.earthdatacloud.nasa.gov/api/)). Commit `data/` and the fixtures. Run the demo **locally on the presenting laptop with Wi-Fi off**. A static frontend reading the pre-generated JSON is the zero-server fallback. Free hosts sleep: Render's free tier spins down after 15 idle minutes and takes about a minute to wake ([Render](https://render.com/docs/free)), and Hugging Face now requires a paid plan to create Docker/Gradio Spaces ([HF Spaces](https://huggingface.co/docs/hub/spaces-overview)). A hosted link is therefore a bonus, never the demo path.

### Tests (all offline, under a minute)

| Test | What it proves |
|---|---|
| `test_fixtures_match_schema` | Every `fixtures/*.json` validates against the exported schema, so fixtures and code cannot drift |
| `test_cards_golden` | The Chattogram card JSON equals `tests/golden/…` (floats rounded to 3 places, keys sorted, `generated_at` stripped); regenerate deliberately with `UPDATE_GOLDEN=1` |
| `test_three_cards_first_is_existing`, `test_every_evidence_has_tag_and_source`, `test_every_benefit_has_citation` | The statement's structure and the honesty rules hold |
| `test_no_future_data` | The window's last date is before the decision date |
| `test_backtest_refits_per_fold` | The held-out year never enters the mean, SD, trend or covariance |
| `test_fill_value_becomes_nan` and `test_solar_pre1984_excluded` | The two known data traps are handled |
| `test_distances_finite` (incl. a near-duplicate column) | The covariance path and fallback work |
| `test_engine_runs_offline` | Monkeypatch `socket.socket` to raise, then call `build_cards`: there are no hidden network calls |
| `test_chance_rate_k5` | 4-of-5 chance = 0.375 and 5-of-5 = 0.0625 |

### Hour-by-hour build order for the engine

Times are Asia/Dhaka and follow team plan v2. **Start nothing until the official opening.** If the opening is earlier or later, shift the blocks.

| Time (Day 1, 13 Nov unless noted) | Engine work | Done when |
|---|---|---|
| 11:30–12:00 | Create repo and folders. Run **one** POWER request for site 1 and inspect the header (sources, fill value, version). Submit the AppEEARS point task for all sites. Check `/quality` for the layer meanings | Raw POWER JSON saved; `task_id` recorded |
| 12:00–12:30 | `models.py`, export the schema, hand-write `fixtures/cards_ctg.json`, push. Frontend and backend start from the fixture | Teammates render the fixture |
| 12:30–13:30 (around the break) | `fetch_power.py` for both sites; `seasons.py`, `features.py`; leakage test | Feature table for 1981–2026 looks sane |
| 13:30–14:30 | `analogs.py`: detrend, z-score, Ledoit-Wolf, distances, both pools, weights, close flag, Euclid overlap; finite test | Real analog years for site 1 |
| 14:00 | **Handoff:** `rules.json` v0 from the science translator | File validates |
| 14:30–15:30 | `confidence.py` (rainfall-based until NDVI arrives), `rules.py`, `cards.py`, CLI | `python -m rotate_engine cards …` writes valid JSON |
| 15:30–16:30 | Golden and offline tests; `build_fixtures.py` for demo inputs (including the "two regions, two hazards" pair); hand over to backend. **Checkpoint:** end-to-end on the presenting laptop with Wi-Fi off | Demo path works offline. If late: fall back to Euclidean and fixed priority presets |
| 16:30–18:00 | Bug fixes only. If NDVI has arrived: minimal QA filter and one curve. Tag `demo-v1`. Support recording | Video recorded from the tagged build |
| 18:00–18:30 | 240-second video upload (storyteller) | Uploaded |
| Evening | Full `ndvi.py`, `ndvi_for_years`, low-vegetation windows, NDVI-based confidence; **`backtest.py` and first run**; second site if not done | Backtest numbers exist, whatever they say |
| Day 2, 07:30–08:15 | Final backtest run; freeze the engine; README run steps tested from a fresh clone; DATA_SOURCES.md; limits text; AI-use notes | Numbers and text handed to the storyteller |
| Day 2, 08:15–09:00 | Support page submission and the 30 s video; private-window link test | Submitted (see the opening-time question) |

## Risk register

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| 1 | AppEEARS task still pending at 16:30 | High | Medium | Submit in the first half hour; "NDVI pending" plus rainfall-based confidence; ORNL fallback in the evening |
| 2 | Venue internet fails during demo or judging | Medium–High | High | Committed data, offline engine, local laptop demo, static JSON fallback, recorded video |
| 3 | Judges call the tool a forecast that it is not | High (if wording is unchanged) | High (Validity) | Season-to-date wording, "does not forecast" line, scenario mode |
| 4 | "4 of 5 agree" called chance-level | Medium | High | Show the chance rate; weights; calibration bins in the backtest |
| 5 | Backtest shows no skill | Medium | Medium | Pre-registered wording; report honestly; the comparison against Euclidean still answers the "compare approaches" bullet |
| 6 | Trend or leakage inflates the skill | Medium | High | Detrend per fold; refit everything per fold; tests |
| 7 | Solar fill values for 1981–83, or an unread fill value, poison the distances | High if unhandled | High | Default features without solar; header-driven NaN; tests |
| 8 | Wrong data label (rainfall "MERRA-2") | Medium | Medium | Labels taken from the response header |
| 9 | MODIS 2025+ drift or end of mission | Medium | Low–Medium | Backtest on 2001–2024; flag 2025+; VIIRS on the roadmap |
| 10 | Demo pixel sits on a pond, river or village | Medium | Medium | Check the point in imagery before the request; landscape-scale wording |
| 11 | JSON shape mismatch at integration | High | High | Schema + fixture in hour 1, `schema_version`, contract test |
| 12 | Backend cannot import Python | Medium | High | CLI and static JSON files |
| 13 | NASA project form opens only at 09:00 on 14 Nov, colliding with the local 09:00 deadline | Unknown | High | Ask the Local Lead now; prepare all text in advance; submit at opening |
| 14 | False "no AI used" statement | High as written | High | Disclose Gemini, Claude and any in-event tools, with representative prompts |
| 15 | Rules breach (pre-event code or data pulls) | Low–Medium | High | Pre-event list below; first commit after opening; written Local Lead answers |
| 16 | Cultivar claim overstates tolerance | Medium | Medium | Whole-season values only; variety class with citation if unsure; "verify with your SAAO" |
| 17 | Secrets committed (Earthdata password, token) | Medium | Medium–High | `.env`, `.gitignore`, token only in fetch scripts |
| 18 | Scope creep on Day 1 | High | High | Stretch only after `demo-v1` is recorded; cut order: Bangla narrative → slider → second site → NDVI curve → live dial (presets) |
| 19 | Missing licence, citations or "not endorsed" line | Medium | Medium | Storyteller owns these; P1 checklist |
| 20 | Venue timing differs from the run of show | Medium | Medium | Confirm with the Local Lead; build blocks are relative to the opening |

## Questions for the Local Lead, and checks for the first build hour

**Ask the Local Lead now, in writing, and keep the answers.**

1. Are the event dates 13–14 Nov, and where is the venue? Must the team attend in person?
2. Does "do not begin work before the hackathon" start at the **local** opening on 13 Nov or the **global** start on 14 Nov? At what exact time may coding and data pulls begin?
3. The team did not submit a 1 Nov (or 1 Oct) 240-second video. Does that affect eligibility for local judging?
4. Is the 30-second video due at 09:00 or 12:00 on Day 2? Does "project page by 09:00" mean submitted on the NASA site? The 2026 landing page says submission opens at 09:00 on 14 Nov.
5. Is the 240-second video still due at 18:30 on Day 1? Where is it uploaded, and must it show a working demo?
6. Is the 1–20 score sheet with Teamwork, UX and NASA-data extras the official local rubric?
7. Before the event, may we: install Python libraries; test our Earthdata/AppEEARS login on a non-project example; read and note published sources (BRRI, SRDI, World Bank); prepare a slide template and demo script?
8. May we reuse generic personal utility code (for example, a caching helper)? Or must all code be written in-event?
9. How many projects does Chattogram nominate to global judging?
10. What is the team-size limit, and are all members correctly registered on both the BASIS (local) and NASA sites?
11. Are there extra local rules on AI tools, videos (subtitles, minors) or the language of the pitch?

**Verify in the first build hour.**

1. The Field Shift **Resources tab**: note any NASA products it lists, and whether judges will expect them.
2. One live POWER daily-point call: exact URL, parameter IDs (PRECTOTCORR, T2M_MIN, T2M_MAX, RH2M, GWETROOT), fill value, `header` source list for precipitation, version string, latest available date.
3. That solar values for 1981–1983 really are fill values.
4. AppEEARS: login works; `/product/MOD13Q1.061` lists the NDVI, pixel-reliability, VI_Quality and day-of-year layer names; `/quality` meanings; the task is accepted (202).
5. That the demo coordinates fall on cropland (check in imagery).
6. Whether the backend imports Python, uses the CLI or reads static JSON.
7. The project-page form fields, especially whether there is a dedicated "Use of AI/SI" field.
8. That the repository is public and opens in a logged-out private window.
9. That the latest MOD13Q1 composite date is available. If Terra data has stopped, note the last date.
10. That the presenting laptop runs the engine with Wi-Fi off.

## Pre-event checklist: what is allowed before coding starts

The safe line is this: **accounts, reading, learning on toy data, installing tools, and logistics are fine; ROTATE code, ROTATE-specific data pulls and the rule table are not.** The FAQ rule is the basis ([Participant FAQs](https://www.spaceappschallenge.org/resources/participant-faqs/)), and the 2025 official answer said the same: "please do not start working on your project until the Hackathon begins" ([Discussion #1273](https://github.com/nasa/spaceapps/discussions/1273)).

| Status | Item |
|---|---|
| Allowed | Every member creates an Earthdata Login; test signing in to AppEEARS (no task submission for ROTATE sites) |
| Allowed | Read the POWER docs, the AppEEARS API doc, the ORNL subset docs, the scikit-learn covariance guide and the pydantic JSON-schema docs |
| Allowed | Install Python 3.12 and the libraries; check the teammates' machines too |
| Allowed | Learn z-scores, Mahalanobis, Ledoit-Wolf and leave-one-out on a toy dataset that is not ROTATE data (for example, random numbers) |
| Allowed | Agree on roles, git conventions (folder ownership; `main` must always run; tag before recording) and the cut order |
| Allowed | Slide template, demo script outline, pitch rehearsal plan (the participants guide reportedly lists these as preparation) |
| Allowed | Collect the list of sources to cite (BRRI pattern table, SRDI 2010, Mainuddin 2015, World Bank 2015 feature) as reading notes |
| Allowed | Message the Local Lead with the questions above |
| Ask first | Typing published figures into a draft rule table; drafting the JSON schema; pre-downloading POWER or NDVI for the demo sites |
| Not allowed | Creating the ROTATE repo with code; writing engine modules, fixtures or `rules.json`; submitting AppEEARS tasks for demo sites; recording demo footage of a built tool |

## Conclusion

What changed in this check is the main risk. The earlier fact check found that the original plan **sounded more certain than its sources**. This check finds that the corrected plan still **sounds more predictive than its method**: matching the 60 days before a decision cannot tell a farmer what the coming season will bring, and "4 of 5 agree" is close to a coin toss until it is calibrated. Fixing that costs almost no build time. It is wording, a chance rate, detrending, and moving the backtest from "if time" to "must have". It also turns ROTATE's main weakness into its pitch: the tool shows what it does not know, with numbers. Most competing Field Shift repos show dashboards; very few show a skill score against a baseline with a significance test.

Two practical findings deserve immediate action because they cannot be fixed on the day. The first is the possible collision between the local 09:00 project-page deadline and a NASA form that may only open at 09:00 on 14 Nov. The second is the AI disclosure, which must name the planning tools already used. Everything else in this report fits inside the existing run of show, as long as the team freezes the JSON contract in the first hour and keeps the engine offline.
