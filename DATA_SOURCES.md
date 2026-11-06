# Data sources (draft)

Draft from the engine, started in Step 2 (5 Nov 2026) and updated through Step 15 (6 Nov 2026). The storyteller owns the final version. Every value below comes from the saved responses in `data/`, not from memory. What each source feeds in the engine is summarised in `docs/ENGINE.md` → "Data sources".

## NASA POWER, daily point (Agroclimatology)

- **Service:** POWER Daily API, version **v2.10.2** (from the response header). Endpoint `https://power.larc.nasa.gov/api/temporal/daily/point`, `community=AG`.
- **Accessed:** 2026-11-05.
- **Sites:** `ctg_anwara` (22.1753, 91.8846) and `barind_godagari` (24.5248, 88.4246). The exact request URLs are in `data/raw/power/<site>.json`.
- **Used for:** the weather in the 60-day matching window (rain, minimum temperature, humidity) and the weather and soil-wetness evidence on the cards.

### Request 1: PRECTOTCORR, T2M_MIN, T2M_MAX, RH2M, ALLSKY_SFC_SW_DWN, GWETROOT

- **Header:**
  - `title`: "NASA/POWER Source Native Resolution Daily Data"
  - `sources`: MERRA2, GEOSIT, SRB, SYN1DEG, FLASHFLUX, POWER
  - `fill_value`: −999.0
  - `time_standard`: LST
  - `start`/`end`: 19810101 to 20261105
- **Which source feeds which parameter:** the header lists sources for the whole response, not per parameter. POWER's parameter metadata defines `PRECTOTCORR` as "The average MERRA-2 bias corrected total precipitation".
- **GWETROOT:** it exists ("Root Zone Soil Wetness", unit 1).
- **Last valid day:** 2026-11-02 for weather and 2026-10-31 for solar. Later days in the response are the fill value.
- **Solar:** values for 1981–1983 are fill values; the first valid year is 1984 at both sites (1,100 missing days).
- **Time standard:** values are in local solar time.

### Request 2: IMERG_PRECTOT (separate request)

- **Header:** `sources`: IMERG; `time_standard`: UTC. POWER refuses LST for this parameter ("The IMERG Source Data is not available at the Local Solar Time (LST) standard").
- **Valid range:** 1998-01-01 to 2026-09-14. IMERG lags about 7 weeks, so it cannot cover the current matching window.
- **Used for (since 6 Nov 2026):** only the tercile scenario mode, at both sites. It ranks past Boro seasons by their rain after the decision day up to 30 Apr. It is never used for matching, and it is labelled "GPM IMERG as served by NASA POWER", as the header reports it.

## Known problem: breaks in the POWER series at both sites (found 5 Nov 2026)

This affects the matching method. It goes in the limits panel and in `docs/ENGINE.md`.

- **Anwara `PRECTOTCORR` is not credible.**
  
  - Annual totals are 600–1,200 mm before 1997, 1,300–3,400 mm for 1997–2014, and 4,600–11,200 mm from 2015 on. Single days reach 663 mm.
  - IMERG at the same point gives 2,400–4,000 mm a year with no jump.
  - The ratio of `PRECTOTCORR` to IMERG over the 60-day Sep–Nov window is 0.3–0.9 for seasons 1999–2015, then 1.6–4.0 from season 2016.

- **Godagari `PRECTOTCORR` steps up in 1997** (360–1,000 mm a year before it, 1,000–1,650 mm after). After 1997 it tracks IMERG reasonably (Spearman 0.64 over the Sep–Nov window), with a mild upward drift.

- **RH2M and T2M_MAX also step in 1997 at both sites:**
  
  |          | RH2M, 1981–96 | RH2M, 1997–2014 | T2M_MAX change |
  | -------- | ------------- | --------------- | -------------- |
  | Anwara   | 73%           | 79%             | −0.9 °C        |
  | Godagari | 54%           | 66%             | −2.1 °C        |
  
  T2M_MIN shows no step.

- **GWETROOT (root-zone soil wetness) follows the same breaks** (Sep–Nov mean, found 6 Nov 2026):

  |          | 1981–96 | 1997–2014 | 2015 on |
  | -------- | ------- | --------- | ------- |
  | Anwara   | 0.56    | 0.84      | 0.94    |
  | Godagari | 0.48    | 0.71      | 0.75    |

  It is model output driven by the model's rain, so Anwara's 2015 rain jump carries into it.

- **Consequence:** years before about 1998 are not comparable with later years, and Anwara rain and soil wetness are not comparable across 2015.

- **Engine decision (5 Nov 2026, with the engine owner):**
  
  - The analog pool starts at Boro season 1999, whose window starts in Sep 1998 (`POOL_FIRST_SEASON`). The NDVI years 2001–2024 sit inside it.
  - Anwara matches on Tmin and RH only, and its POWER rain is neither used nor shown (`match_features` in `data/sites.json`).
  - Soil wetness is display evidence only, never a matching feature. It is shown, labelled "model output", only where the site's rain is usable (today Godagari), compared with the Boro seasons from 1999. It is not shown in a what-if.
  - Both rules appear as warnings in the engine output.

## NASA MODIS NDVI, MOD13Q1.061 via AppEEARS

- **Task:** `rotate_ndvi_2sites`, task_id `dfdede24-460a-454b-bdcf-b4c52f397bf8`, submitted 2026-11-05 and downloaded the same day into `data/ndvi/`. File hashes are in `bundle_manifest.json`.
- **Contents:** 614 composites per site, 2000-02-18 to 2026-10-16. AppEEARS renamed the point IDs to `ctganwara` and `barindgodagari`.
- **Values:** NDVI is already scaled in the CSV. One fill value (−3000) is present.
- **Pixel reliability:** 555 rows are 0, 383 are 1 and 289 are 3. A reliability of 0 or 1 passes for 75% of Godagari rows and 78% of Anwara rows; Jun–Aug pass only 6–46%.
- **Land/water mask at Anwara:** 425 of 614 composites are flagged "Ocean coastlines and lake shorelines".
- **Layers:**
  - `_250m_16_days_NDVI` (scale 0.0001, fill −3000)
  - `_250m_16_days_pixel_reliability`
  - `_250m_16_days_VI_Quality`
  - `_250m_16_days_composite_day_of_the_year`
- **Used for:** vegetation in the area around each field (250 m).

## NASA MODIS NDVI extras via the ORNL DAAC web service (display only)

- **Service:** ORNL DAAC MODIS/VIIRS fixed-site subsetting web service, `https://modis.ornl.gov/rst/api/v1`. No login. Accessed 2026-11-06 by `scripts/fetch_ndvi_ornl.py`; file hashes are in `data/ndvi/ornl/manifest.json`.
- **MYD13Q1.061 (Aqua):**
  - **What:** centre pixel; NDVI, pixel reliability and composite day of year; 557 composites, 2002-07-04 to 2026-09-06, at both sites.
  - **QA:** 484 pass at Anwara and 400 at Godagari.
  - **Agreement:** Aqua points within 8 days of a Terra point agree closely (r = 0.90 at Anwara and 0.95 at Godagari; mean difference +0.01 and −0.01).
- **MOD13Q1.061 window:**
  - **What:** 9×9 pixels (1 km each way); NDVI and pixel reliability; 66 composites, 2023-11-01 to 2026-08-29.
  - **Same pixel:** its centre pixel equals the AppEEARS value on all 66 dates at both sites.
  - **Spread:** across the central 3×3 block (about 700 m), QA-passed NDVI typically ranges 0.15 (Anwara) and 0.13 (Godagari) from lowest to highest pixel. This belongs in the limits panel next to the mixed-pixel note.
- **Values:** raw integers, scale 0.0001, fill −3000.
- **Used for:** display only: Aqua points beside the Terra curve, and the 3×3 spread. The matching, confidence and backtest use the AppEEARS Terra data alone.

## HLS 30 m NDVI via AppEEARS (display only)

- **Task:** `rotate_hls_2sites`, task_id `1a7fe273-b13a-4d94-a0de-3c4f7565a469`, submitted and downloaded 2026-11-06 by `scripts/submit_ndvi_hls.py` and `scripts/fetch_ndvi_appeears.py <task_id> hls`. Files are in `data/ndvi/hls/`, with hashes in its `bundle_manifest.json`. No user id is in the files.
- **Layers:** `NDVI` from `HLSS30_VI.020` and `HLSL30_VI.020`, and `Fmask` from `HLSS30.020` and `HLSL30.020` (the VI products carry no QA layer of their own). Requested 2015-11-01 to 2026-11-06 (the last row is 2026-11-01), one acquisition per row; each site sits on one tile (Godagari 45RXH, Anwara 46QCK).
- **Values:** already scaled; fill −19999.
- **QA:** a point is kept when it is not fill, has an Fmask row, and has none of the cloud, adjacent-to-cloud/shadow, cloud-shadow or snow/ice bits. Water passes, because a flooded field is a real observation. High aerosol (Fmask bits 6–7 = 11) passes but is flagged: it marks about 85% of the otherwise clear points at Godagari and about half at Anwara, so dropping it would leave almost no curve.
- **Kept:** Anwara 421 points (266 HLSS30, 155 HLSL30), 204 flagged; Godagari 580 (309 and 271), 486 flagged. June–August pass rates are about 8–21% (monsoon cloud).
- **Agreement:** HLS points within 8 days of a Terra MOD13Q1 point give r = 0.91 at Anwara and 0.90 at Godagari; mean NDVI 0.563 vs 0.563 and 0.570 vs 0.551.
- **Used for:** display only, as a separate 30 m curve (`ndvi --hls`). Never mixed into the 250 m curve, and never used for matching, confidence or the backtest. Per the project rules, HLS through AppEEARS is the only Landsat or Sentinel-2 use; never name them as separate sources.
- **Citations** (from the bundle README):
  - Neigh, C. (2025). HLS Operational Land Imager Vegetation Indices Daily Global 30m v2.0. NASA LP DAAC. https://doi.org/10.5067/HLS/HLSL30_VI.002. Accessed 2026-11-06.
  - Neigh, C. (2025). HLS Sentinel-2 Multi-spectral Instrument Vegetation Indices Daily Global 30m v2.0. NASA LP DAAC. https://doi.org/10.5067/HLS/HLSS30_VI.002. Accessed 2026-11-06.
  - Neigh, C., Ju, J., Roger, J.-C., Skakun, S., Vermote, E., Claverie, M., Dungan, J., Yin, Z., Freitag, B., & Justice, C. (2021). HLS Operational Land Imager Surface Reflectance and TOA Brightness Daily Global 30m v2.0. NASA LP DAAC. https://doi.org/10.5067/HLS/HLSL30.002. Accessed 2026-11-06.
  - Neigh, C., Ju, J., Roger, J.-C., Skakun, S., Vermote, E., Claverie, M., Dungan, J., Yin, Z., Freitag, B., & Justice, C. (2021). HLS Sentinel-2 Multi-spectral Instrument Surface Reflectance Daily Global 30m v2.0. NASA LP DAAC. https://doi.org/10.5067/HLS/HLSS30.002. Accessed 2026-11-06.

## Citation (POWER asks for both)

- **POWER reference:** "The data was obtained from National Aeronautics and Space Administration (NASA) Langley Research Center's Prediction Of Worldwide Energy Resources (POWER) project funded through the NASA Earth Science Division."
- **Data reference:** "The data was obtained from the POWER Project's Daily v2.10.2 version on 2026/11/05."

## Crop rule table (`rules/rules.json`), not NASA data

- **Status:** an engine draft (5 Nov 2026), **not yet reviewed** by the science translator.
- **Use of AI:** drafted with AI assistance (Claude). Each value was checked against the text of the cited source, fetched on the drafting date.
- **Sources:**
  - Nasim et al. 2017, *Bangladesh Rice Journal* 21(2) (cropping patterns);
  - FAO Irrigation and Drainage Paper 29, Tables 4 and 5 (crop salt tolerance);
  - Debsharma et al. 2024, *PLoS ONE* (salt-tolerant Boro, and the SRDI 2010 salinity classes as reproduced there);
  - Emran et al. 2022, *Agronomy for Sustainable Development* (legume nitrogen, fertilizer use, coastal constraints);
  - Hoque et al. 2023, *Field Crops Research* (irrigation applied to Boro, wheat and maize at Jamalpur).
- **Contents (5 Nov):** 19 crop rows and 28 cropping patterns, each pattern with a season per slot (Rabi, Kharif-1, Kharif-2).
- **Not used, because they could not be read (paywall or blocked):** Mainuddin et al. 2015 and Herridge et al. 2008.
