# ROTATE docs notes

Nov 5, 2026 · Step 0.3 of `ROTATE engine build steps.md` · @sudipta das

Reading notes only: no ROTATE code and no data pulls. Quotes are from the pages as read on 5 Nov 2026. Library behaviour marked "toy run" was checked on random numbers in a scratch folder outside this project; none of that code is kept here.

## 1. Settled by the report

The docs agree with the report on these, with the caveats noted.

- **Solar starts on 1 Jan 1984.** The sources are SRB 4.0-IP from "January 1, 1984" to "December 31, 2000", then CERES SYN1deg Ed4.2 from 1 Jan 2001, then FLASHFlux v4A for the latest ~3–4 months ([POWER solar sources](https://power.larc.nasa.gov/docs/methodology/data/sources_fluxes/)).
- **NDVI layer names.** `_250m_16_days_NDVI`, `_250m_16_days_VI_Quality` and `_250m_16_days_pixel_reliability` appear in the `/quality/MOD13Q1.061` example ([AppEEARS API](https://appeears.earthdatacloud.nasa.gov/api/)). The day-of-year layer does not appear (see list 2).
- **Pixel-reliability meanings** (0 good, 1 marginal, 2 snow/ice, 3 cloudy). The report takes these from the [GEE MOD13Q1 page](https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD13Q1). The AppEEARS doc shows where to read them, `GET /quality/MOD13Q1.061/_250m_16_days_pixel_reliability` (each value has an `Acceptable` field), but doesn't list them. Step 1 reads them anyway.
- **The 0.0001 scale factor.** This also comes from GEE. AppEEARS `/product/{id}` layer entries carry `ScaleFactor`, `FillValue`, `ValidMin`, `ValidMax` and `Units`, so Step 1 reads the real value there.
- **POWER latency of about 2 days.** This holds for **weather only**: GEOS-IT has a latency of "2 Days" ([POWER weather sources](https://power.larc.nasa.gov/docs/methodology/data/sources_meteorology/)). Solar (FLASHFlux) lags by "5–7 Days" in the table and "about four days" in the text. Solar is off by default, so the 2-day rule is enough for the matching window.
- **scikit-learn's `.mahalanobis()` returns squared distances.** The report flagged this as unchecked; it is now settled. The docstring reads "Squared Mahalanobis distances of the observations", and the source ends in `** 2` ([EmpiricalCovariance](https://scikit-learn.org/stable/modules/generated/sklearn.covariance.EmpiricalCovariance.html), [source](https://github.com/scikit-learn/scikit-learn/blob/main/sklearn/covariance/_empirical_covariance.py)). A toy run matched D² and not D. It also measures distance from the fitted mean `location_`, not between two rows, so computing D from `precision_` ourselves (algorithm Step 5) is right.

## 2. To check live in Step 1–2

The five items the build steps already list:

- **The fill value.** None of the POWER pages read states it, -999 included.
- **The precipitation source.** The docs say the default `PRECTOTCORR` comes from MERRA-2. GPM IMERG (0.1°) is a separate "High-Resolution" option with "dedicated parameter aliases in the API" ([POWER methodology](https://power.larc.nasa.gov/docs/methodology/)). The header still decides the label.
- **The response shape.** No page read describes the JSON (header, messages, parameters, times). Save the raw JSON in Step 2 and read it there.
- **The day-of-year layer name.** It is absent from the AppEEARS doc. Read it from `GET /product/MOD13Q1.061`.
- **GWETROOT.** None of the POWER pages read names it.

Added by this reading:

- **T2M_MIN, T2M_MAX, RH2M and ALLSKY_SFC_SW_DWN.** The docs confirm only `PRECTOTCORR` and `T2M` as IDs. The Step 2 call confirms all six requested IDs at once.
- **The name of the near-real-time weather source.** The sources page says "GEOS-IT"; the methodology page says "GEOS FP-IT". Use whatever the header says.
- **The POWER version string.** The docs say "POWER Release 10" / "v10", while the referencing template says "2.x.x". Take the version from the header for `DATA_SOURCES.md`.
- **Whether solar values for 1981–83 are fill values.** This is already in Step 2.
- **Whether AppEEARS offers HLS.** The doc doesn't mention it. Check `GET /product`; this only matters for Step 15.
- **Which code AppEEARS returns for an expired token.** The prose says to watch for 403, but the error table defines 403 as "elevated users only" and 401 as "Your API key is wrong". Treat either as "log in again".

## 3. API notes for Steps 1, 2, 4 and 13

### NASA POWER, daily point ([API](https://power.larc.nasa.gov/docs/services/api/), [daily](https://power.larc.nasa.gov/docs/services/api/temporal/daily/))

- **Request:** `GET https://power.larc.nasa.gov/api/temporal/daily/point?parameters=A,B&community=AG&longitude=…&latitude=…&start=YYYYMMDD&end=YYYYMMDD&format=JSON`.
- **Request options:**
  - `community=AG` (Agroclimatology) is valid.
  - Requests are limited to "a maximum of 20 parameters … for a single point".
  - "Daily API defaults to providing LST". `time-standard=UTC` is the alternative.
  - The output formats are JSON, CSV, ASCII, NetCDF, and ICASA (AG only).
- **Status codes:** 200 Success, **422 Validation Error** (a bad request: never retry it) and 429 Too Many Requests. No numeric rate limit is given.
- **Blocking:** "If your application persists in requesting the same relative location, it will potentially be blocked." Cache, and fetch each site once.
- **Trend caution:** the weather sources page says "it is recommended to end the analysis 2 months behind NRT when assessing climate trends". Our window always includes GEOS-IT days, so this goes in the limits panel.
- **Citation** ([referencing](https://power.larc.nasa.gov/docs/referencing/)): give **both** the POWER Reference and the Data Reference, and include "the service name, version number, and date accessed".
  - The Reference reads: "The data was obtained from National Aeronautics and Space Administration (NASA) Langley Research Center's Prediction Of Worldwide Energy Resources (POWER) project funded through the NASA Earth Science Division."
  - The Data Reference template reads: "The data was obtained from the POWER Project's Hourly 2.x.x version on YYYY/MM/DD." For us, use Daily, the header's version and the access date.
  - POWER also asks users to email larc-power-project@mail.nasa.gov with a link to publications that use the data.

### AppEEARS ([API](https://appeears.earthdatacloud.nasa.gov/api/), [sample point request](https://appeears.earthdatacloud.nasa.gov/api/examples/sample_point_request.json))

- **Login:** `POST /login` with HTTP Basic auth (the Earthdata username and password) returns `{token_type: "Bearer", token, expiration}`. The token "will expire approximately 48 hours after being acquired".
- **Product info:**
  - `GET /product` lists the products.
  - `GET /product/MOD13Q1.061` lists the layers with their scale, fill and valid range.
- **Quality:** `GET /quality/{product}/{layer}` lists the values; `/quality/{product}/{layer}/{value}` decodes the bits.
- **Point task:** `POST /task` with this JSON:
  - `task_type: "point"`, `task_name`;
  - `params.dates: [{startDate: "01-01-2000", endDate: "MM-DD-YYYY"}]`;
  - `params.layers: [{product: "MOD13Q1.061", layer: …}]`;
  - `params.coordinates: [{latitude, longitude, id, category}]`.

  One task can hold several points; the sample has six. A successful submit returns **202** with `{task_id, status: "pending"}` and a `Location` header.
- **Status:**
  - The values are `pending`, `processing`, `done` and `error`.
  - `GET /task/{id}` gives the status; `GET /status/{id}` gives the progress.
  - The doc gives **no polling guidance**: our 30–60 s interval is our own choice.
  - The doc gives no limit on task size and no typical processing time.
- **Download:**
  - `GET /bundle/{task_id}` lists the files with their sha256.
  - `GET /bundle/{task_id}/{file_id}` gives a 302 redirect to S3, and the S3 link "is valid for 48 hours". Download and commit as soon as the task is done.
- **429:** "Please slow the rate of your requests." No number is given.

## 4. Library notes for Steps 3–6 and 0.4

Versions seen on the docs sites: pydantic 2.14.2, scikit-learn 1.9.1, requests-cache 1.3.3 (2026-07-03). The tenacity docs page shows no version.

### Step 0.4 environment (installed 5 Nov in `.venv`, Python 3.12.3)

Use the same versions on every machine, including the presenting laptop:

```sh
python3.12 -m venv .venv   # if this fails (no ensurepip on Ubuntu): uv venv --seed -p 3.12 .venv
.venv/bin/python -m pip install numpy==2.5.4 pandas==3.1.1 scikit-learn==1.9.1 pydantic==2.14.2 \
  pytest==9.2.0 jsonschema==4.26.0 requests==2.34.2 requests-cache==1.3.3 tenacity==9.2.1
.venv/bin/python -c "import numpy, pandas, sklearn, pydantic, pytest, jsonschema, requests, requests_cache, tenacity; print('OK')"
```

On Windows, use `.venv\Scripts\python` instead of `.venv/bin/python`.

### scikit-learn ([covariance guide](https://scikit-learn.org/stable/modules/covariance.html), [LedoitWolf](https://scikit-learn.org/stable/modules/generated/sklearn.covariance.LedoitWolf.html))

- **Constructor and attributes:** `LedoitWolf(*, store_precision=True, assume_centered=False, block_size=1000)`. The fitted model has `covariance_`, `location_`, `precision_` and `shrinkage_` (in [0, 1]). The data is centred by default.
- **What it shrinks toward:** the shrinkage target is `(Tr Σ̂ / p)·Id`. The guide doesn't ask for standardised input; we standardise anyway (algorithm Step 4).
- **`precision_` and our pinv rule:** `precision_` is documented as the "Estimated pseudo inverse matrix". After shrinkage the matrix is full rank, so it equals the true inverse (the toy run confirmed this). Our "don't rely on `pinv`" rule targets the raw covariance, so `precision_` is fine. Keep the finite-D assert.
- **MinCovDet:** the guide *recommends* robust estimators when the data has outliers. Avoiding MinCovDet, because it down-weights the extreme years we need, is **ROTATE's own reasoning**. Write it that way under Methods and don't cite scikit-learn for it.

### pydantic ([JSON schema](https://docs.pydantic.dev/latest/concepts/json_schema/), [config](https://docs.pydantic.dev/latest/api/config/))

- **Output format:** pydantic generates JSON Schema Draft 2020-12. Nested models go to `$defs` and are referenced with `$ref`. For one combined schema, use `pydantic.json_schema.models_json_schema([(Model, mode), …])`.
- **`extra="forbid"`** produces `"additionalProperties": false` (toy run; the docs don't state it).
- **`Literal`:** `Literal["Observed","Derived","Scenario"]` becomes `"enum": [...]`, and a single-value `Literal["1.0"]` becomes `"const": "1.0"` (toy run).
- **Trap for Step 3:** a field with a default, such as `schema_version: Literal["1.0"] = "1.0"`, is **not** in `required` in either schema mode. A fixture missing `schema_version` would therefore pass `test_fixtures_match_schema`.
  - The fix: export with `model_json_schema(mode="serialization")` and set `json_schema_serialization_defaults_required=True` in the `ConfigDict`.
  - With that change, the toy run's `required` list became `["tag", "schema_version"]`.
- **Reading and writing JSON:** `model_dump_json()` writes JSON and `model_validate_json()` reads it back.

### requests-cache ([general](https://requests-cache.readthedocs.io/en/stable/user_guide/general.html), [expiration](https://requests-cache.readthedocs.io/en/stable/user_guide/expiration.html))

- **The session:** `from requests_cache import CachedSession, NEVER_EXPIRE`, then `CachedSession("cache/power", backend="sqlite", expire_after=NEVER_EXPIRE, stale_if_error=True)`.
  - A name without an extension gets `.sqlite`, so the file should be `cache/power.sqlite` (inferred).
  - The docs don't say whether the folder is created, so create `cache/` first.
- **What gets cached:**
  - The cache key is the method + URL + parameters + body, so each site and date range gets its own entry.
  - By default only GET/HEAD responses with status **200** are cached, so error responses are never stored.
- **Offline mode:** `only_if_cached=True` (as a session setting or per request) returns "`504 Not Cached`" when the data is missing. `response.from_cache` shows whether a response was a cache hit.
- **Changing the expiry:** a new `expire_after` applies "only to new responses, **not** retroactively".

### tenacity ([docs](https://tenacity.readthedocs.io/en/latest/))

- **The decorator:** `@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10), retry=…, reraise=True)`. `reraise=True` raises the original exception instead of `RetryError`.
- **Retrying on HTTP status:** tenacity has no built-in option for it.
  - In Step 4, call `raise_for_status()`.
  - Retry only on connection errors, timeouts and 429/5xx, using `retry_if_exception(<predicate>)`.
  - Never retry 422.

## 5. Where the docs disagree with our plan documents

These are not fixed in the plan files; the team decides.

1. **The POWER data-sources link is dead.** The report cites `https://power.larc.nasa.gov/docs/methodology/data/sources/`, which now returns 404. Use the [weather](https://power.larc.nasa.gov/docs/methodology/data/sources_meteorology/), [solar](https://power.larc.nasa.gov/docs/methodology/data/sources_fluxes/) and [hydrology](https://power.larc.nasa.gov/docs/methodology/data/sources_hydrology/) pages in `DATA_SOURCES.md`.
2. **"GEOS FP-IT" is hard-coded** in `CLAUDE.md` and in the build steps (Step 9's warning example and Step 17's limits text). The current sources page says "GEOS-IT". Warning text should take the name from the header.
3. **Precipitation.** The plan's "precipitation may be GPM IMERG" is weaker than it reads: `PRECTOTCORR` defaults to MERRA-2, and IMERG is opt-in. The report says IMERG starts "from 2001", but two POWER pages say "June 1, 1998" and the hydrology page says 2001. The header rule still covers all of this.
4. **"Latency ~2 days"** is true for weather only; solar lags 4–7 days.
5. **MinCovDet.** As noted in section 4, scikit-learn doesn't back our reason for avoiding it.
6. **`schema_version` in the Step 3 schema export.** See the pydantic trap in section 4.

## 6. Unread

- **The ORNL MODIS web service docs** (https://modis.ornl.gov/data/modis_webservice.html). On 5 Nov the connection was refused from the fetch service and timed out from this machine.
  - The report's "no login stated, 10 dates per call" therefore stays unverified.
  - A teammate should read the page from another network before Step 13. Nothing before Step 13 needs it.
- **POWER's parameter dictionary** ([system API](https://power.larc.nasa.gov/docs/services/api/system/)) and the [communities page](https://power.larc.nasa.gov/docs/methodology/communities/). These were not read; the Step 2 live call covers the IDs.

## 7. Step 0.5 toy practice (5 Nov)

The script ran on 44 random "years" with 3 correlated features, outside this project (Claude's session scratchpad, so it is temporary). It is throwaway practice, not ROTATE code: ask Q8 before reusing any of it. Every check below passed as an `assert`.

- **z-score:** how many training-year standard deviations a value sits from the training-year mean, so features in mm, °C and % become comparable.
- **Ledoit-Wolf precision and Mahalanobis D:** Ledoit-Wolf shrinks the sample covariance towards a simpler target so it stays stable with few years, and D = √(dᵀ P d) is a distance that discounts features that move together. An exact copy of a row gave D = 0, and D² from `precision_` matched sklearn's `.mahalanobis()` (squared, measured from `location_`).
- **Leave-one-out MSE skill score:** hide each year in turn, refit z-scores and Ledoit-Wolf on the rest, predict it from its 5 kernel-weighted nearest years, and score `1 − MSE_analog/MSE_mean`. Above 0 beats the plain average. The plain-mean baseline scored exactly 0 against itself. Toy result: 0.50 (Ledoit-Wolf), 0.57 (Euclidean). On random data that ordering means nothing.
- **Permutation p-value:** the share of 1,000 runs that use 5 random training years instead of the nearest 5 and still score at least as well. It answers "could matching be luck?". Toy result: p ≈ 0.001, because the toy outcome was built to depend on the features.
- **Binomial chance rate:** with 5 analogs voting on a sign like coin tosses, some side has ≥4 votes 37.5% of the time and all 5 agree 6.25% of the time. Computed as `Σ 2·C(5, j) / 2⁵`, so 0.375 for j ≥ 4 and 0.0625 for j = 5.

## 8. Step 1 hour-1 checks (live, 5 Nov 2026)

Read from the public AppEEARS API, which needs no login: `GET /product/MOD13Q1.061` and `GET /quality/MOD13Q1.061/{layer}`.

**The four task layers** (scale, fill, valid range, type):

| Layer | Scale | Fill | Valid | Type |
|---|---|---|---|---|
| `_250m_16_days_NDVI` | 0.0001 | -3000 | -0.2 to 1.0 | float32 |
| `_250m_16_days_pixel_reliability` | none | -1 | 0–3 | int32 |
| `_250m_16_days_VI_Quality` | none | 65535 | 0–65534 | uint16 (bit field) |
| `_250m_16_days_composite_day_of_the_year` | none | -1 | 1–366 | int16 |

This settles two list-2 items: the day-of-year layer is `_250m_16_days_composite_day_of_the_year`, and the 0.0001 scale factor is confirmed.

**Pixel reliability** (AppEEARS `Acceptable` flag in brackets): 0 = "Good data, use with confidence" (true); 1 = "Marginal data, Useful, but look at other QA information" (**false**); 2 = "Snow/Ice Target covered with snow/ice" (false); 3 = "Cloudy data, Target not visible, covered with cloud" (false).
- **Open decision:** the plan keeps 0 or 1, but AppEEARS marks 1 as not acceptable. Keep the plan, but flag reliability-1 points. Decide this in Step 13.

**VI_Quality bit fields:**
- MODLAND: 0 good, 1 check other QA, 2 probably cloudy, 3 not produced.
- VI Usefulness: 0 highest to 15 not useful.
- Aerosol Quantity.
- Adjacent cloud.
- Atmosphere BRDF correction.
- Mixed Clouds.
- Land/Water Mask: 1 = land; 2 = coastline or shoreline; 3 = shallow inland water; 4 = ephemeral water. This is useful for the coastal site.
- Possible snow/ice.
- Possible shadow.

**Latest MOD13Q1 composite** (CMR, tiles h25v06, h26v06 and h26v07, which cover Bangladesh): A2026289, which covers 16–31 Oct 2026. It was published 3 Nov 2026, so the next composite (from 1 Nov) should appear around 19 Nov.

**Still open in Step 1:**
- The cropland check of both demo points in imagery.
- The AppEEARS task submission and its `task_id` (this needs a login).
- The Field Shift Resources tab ([challenge page](https://www.spaceappschallenge.org/2026/challenges/adapting-farms-with-nasa-data/?tab=resources), read in Chrome on 5 Nov) says only "Resources will be available on Friday, November 13." No products are listed yet, so re-read it on 13 Nov. This also suggests that the global event starts on 13 Nov, which fits the plan's Day 1 date.

### Field Shift challenge text, checked against the plan (Details tab, pasted 5 Nov)

- **Matches the plan:**
  - Compare at least three rotation strategies, including the existing one.
  - Each strategy shows why it was suggested, the evidence, the benefits, the information gaps, and the risks for local review. These are our card fields.
  - Show bare-field windows and the seasons when crops are vulnerable. These come from the NDVI low-vegetation windows.
  - Explain terms (glossary), how satellite data differs from ground data (limits panel), and uncertainty.
  - Take the farmer's priorities and constraints: water availability, equipment, market.
  - Say that the tool supports, and does not replace, local expertise.
  - Scenario sliders are optional, which matches our stretch item.
- **Gaps for Step 3 and Step 7. Decide them, don't silently add them:**
  - The challenge's priority examples include **forage value**, **market suitability** and **supplemental income**. Our four priorities don't cover these, and neither does the rules.json benefit list (water use, N fixation, erosion, organic matter, pest-cycle disruption). Decide whether to add a `market_or_income` benefit column, and whether forage gets one. The science translator owns `rules/`.
  - The challenge also names deep-rooting crops and cover crops. Add them as rule-table crop traits if the science translator agrees.
- **Dataset list:** SMAP, ECOSTRESS, GPM, Landsat, MODIS, NASA POWER, GRACE/GRACE-FO, SRTM, and GEDI (in the data-fusion paragraph). The challenge says we "may" use them; none is required. Our POWER + MODIS core is within the list, so the roadmap/stretch split in CLAUDE.md stands.
- **Start date:** "More resources may be added before the hackathon begins" fits the Resources tab's 13 Nov date. The hackathon has probably not begun globally yet.

### Demo points (Step 1 imagery check: Google Maps satellite, Airbus/Maxar imagery dated 2026, checked 5 Nov)

| Site | Point | Verdict |
|---|---|---|
| Anwara (user's pick) | 22.219273, 91.857839 | **Rejected.** A small paddy patch with a road junction, homesteads and cleared China EPZ land within ~150 m. The wider area (CUFL, KAFCO, Korean EPZ, Karnaphuli tunnel approach) is industrialising, so a 2000–2026 NDVI series would track land-use change, not crops. |
| Anwara, `ctg_anwara` | **22.1753, 91.8846** | **Accepted.** Open paddy block (Dhaila beel area, Burumchhara union), ~1 km across. A ±125 m box (one 250 m MODIS pixel) holds only fields. The canal 250 m south is outside the pixel. |
| Godagari, `barind_godagari` | **24.5248, 88.4246** | **Accepted.** Terraced paddy block (Dewan Para area, Godagari upazila, ~6 km NE of Godagari town, high Barind) about 400 m across. A ±125 m box is mostly paddy, with a small pond and a fallow patch on its western edge. |
| Godagari (rejected areas) | around 24.475, 88.395 and 24.522, 88.421 | **Rejected.** The dark blocks are mango orchards. Barind paddy is being converted to mango, which would turn a crop NDVI series into a tree NDVI series. |

A 250 m MODIS pixel is about 5–6 ha, so the point needs ≥125 m of uniform cropland on every side, not just a field under the pin.

**Risks to check when the NDVI arrives (Step 13):**
- **Godagari:** mango expansion. AgrowDesh Mango Orchard is ~500 m NE. If the 2000–2024 NDVI loses its two-crop seasonal dip in later years, the pixel has turned to orchard. Move the point, or cut the NDVI pool's years.
- **Anwara:** beel flooding in the monsoon. Low NDVI there is "flooded or newly planted", not bare.

### AppEEARS task (submitted 5 Nov 2026, 19:04 Asia/Dhaka)

- **Name:** `rotate_ndvi_2sites`
- **task_id:** `dfdede24-460a-454b-bdcf-b4c52f397bf8`
- **Product:** MOD13Q1.061. The four layers are confirmed in the receipt email: NDVI, pixel_reliability, VI_Quality and composite_day_of_the_year.
- **Dates:** 01-01-2000 to 11-05-2026.
- **Points:** `ctg_anwara` 22.1753, 91.8846; `barind_godagari` 24.5248, 88.4246.
- **When done:** download the results CSV, the README and the request JSON into `data/ndvi/` (Phase 2). Outputs are kept only for a limited time (AppEEARS sample-retention), so download them promptly.

### AppEEARS results (downloaded 5 Nov 2026, checked)

- **Location:** the bundle is unzipped into `data/ndvi/`: the results CSV, the granule list, the request JSON, the metadata XML and the README. The original zip is in `cache/`, which is git-ignored.
- **IDs:** AppEEARS **stripped the underscores** from the IDs. The CSV says `ctganwara` and `barindgodagari`, so the NDVI loader must map them to `ctg_anwara` and `barind_godagari`.
- **Coverage:** 614 composites per site, from 2000-02-18 to 2026-10-16. There are no missing 16-day steps and no duplicate dates. Tile h26v06.
- **Values:** NDVI is already scaled (0.04–0.92), but the fill value stays **-3000**. Anwara has one fill row, with pixel reliability -1, so treat it as NaN before anything else.
- **Pixel reliability:**

  | Site | 0 | 1 | 3 | -1 |
  |---|---|---|---|---|
  | Anwara | 368 | 110 | 135 | 1 |
  | Godagari | 187 | 273 | 154 | 0 |

  Godagari leans heavily on "marginal" (1), so the §8 open decision about reliability 1 matters most there.
- **Seasonality looks real:**
  - Godagari peaks Aug–Oct (Aman, about 0.8) and is lowest in Dec (0.32).
  - Anwara peaks Oct–Nov (0.8), and again in Mar–Apr (0.6–0.7, likely Boro). It is lowest in Jan (0.33).
- **Godagari trend (check in Step 13):** the yearly mean NDVI rose from about 0.41–0.47 (2000–2010) to about 0.56–0.60 (2015 onward). The seasonal spread (std about 0.16–0.23) did not collapse, so a crop cycle is still present. The rise fits either more irrigated Boro or orchard creep into the pixel. Don't treat the early and late years as alike without checking.
- **Privacy:** `rotate-ndvi-2sites-request.json` holds the submitter's email as `user_id`. Redact it before pushing to the public repo, or leave the file out.
