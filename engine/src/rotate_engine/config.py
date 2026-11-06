"""Engine constants. Values follow the research report's "Improved engine implementation plan"."""

SCHEMA_VERSION = "1.0"
ENGINE_VERSION = "0.1.0"

K = 5                      # analogs per pool, fixed before looking at results
WINDOW_DAYS = 60           # matching window length
MIN_VALID_DAYS = 55        # fewer valid days in the window -> warning and stop
STALE_WINDOW_DAYS = 7      # window ending further back than this before the decision -> warning

# POWER parameter -> window feature. Matching uses these three only (no solar, never Tmax with Tmin).
RAIN, TMIN, RH = "PRECTOTCORR", "T2M_MIN", "RH2M"
MATCH_PARAMS = (RAIN, TMIN, RH)
FEATURES = ("rain_log1p", "tmin_c", "rh_pct")
DETREND_FEATURES = ("tmin_c",)  # temperature only; rainfall is not detrended by default

SOIL = "GWETROOT"          # root-zone soil wetness (0-1), model output, display evidence only

SOLAR = "ALLSKY_SFC_SW_DWN"
SOLAR_FIRST_YEAR = 1984    # POWER solar starts 1 Jan 1984

# Display-only extreme-day thresholds (confirm with the science translator before showing them)
HOT_DAY_TMAX_C = 35.0
HEAVY_RAIN_MM = 50.0

CLOSE_MATCH_QUANTILE = 0.95  # close_match when D <= sqrt(chi2(p, 0.95))

# Boro: a decision from July onward belongs to the season harvested the next calendar year.
BORO_NEW_SEASON_MONTH = 7


# POWER RH2M, T2M_MAX and PRECTOTCORR step in 1997 at both sites (DATA_SOURCES.md), so only
# seasons whose window starts in Sep 1998 or later are comparable: Boro harvest year 1999 on.
POOL_FIRST_SEASON = 1999

NDVI_YEARS = (2001, 2024)   # Boro harvest years with NDVI in the pool; 2025 onward flagged
NDVI_FILL = -3000           # AppEEARS CSV NDVI is already scaled; the fill stays -3000
NDVI_OK_RELIABILITY = (0, 1)  # keep good and marginal; AppEEARS marks 1 not acceptable (Step 13 decides)
NDVI_DEFAULT_PEAK_DOY = (81, 112)  # Boro peak, mid-March to mid-April (Mosleh & Hassan 2014)
NDVI_GAP_DAYS = 32          # more than two 16-day composites apart: break the line, never fill
NDVI_LOW_VEG = 0.3          # report's working threshold, to calibrate on our own curves
NDVI_FLAG_FROM_YEAR = 2025  # Terra orbit drift: flag composites from 2025 on
HLS_FILL = -19999           # HLS VI NDVI fill (the AppEEARS CSV is already scaled)
HLS_MASK_BITS = 0b11110     # Fmask bits 1-4: cloud, adjacent to cloud/shadow, cloud shadow, snow/ice -> drop
HLS_HIGH_AEROSOL = 3        # Fmask bits 6-7 == 0b11: kept but flagged (haze is common, ~85% of clear Barind points)
NDVI_SMOOTH_WINDOW, NDVI_SMOOTH_ORDER = 5, 2  # Savitzky-Golay on gap-free runs (report NDVI item 4)
NDVI_SEASON_START = (11, 1)  # per-year view: 1 Nov before the Boro harvest year ...
NDVI_SEASON_END = (5, 31)    # ... to 31 May of it (seedbed to harvest at both sites)
CLOUD_GAP = "cloud gap"
LOW_VEG_LABEL = "low-vegetation window (bare, flooded or newly planted)"

# Tercile scenario: past seasons ranked by rain after the decision day up to this day of the harvest year
TERCILE_SEASON_END = (4, 30)  # Boro peak and most harvests fall by then at both sites

# Backtest, fixed before the first run (docs/ENGINE.md "Backtest: rule fixed before the first run")
N_PERMUTATIONS = 1000
PERMUTATION_SEED = 20261113
SKILL_P = 0.10
VERDICT_SKILL = ("Some skill: MSE skill score {ss:.3f} against the plain average over {n} Boro seasons "
                 "({first}–{last}), permutation p = {p:.3f}.")
VERDICT_NO_SKILL = ("No demonstrable skill: MSE skill score {ss:.3f} against the plain average over {n} "
                    "Boro seasons ({first}–{last}), permutation p = {p:.3f}. The analog years are shown "
                    "as historical examples only.")

DISCLAIMER = ("ROTATE helps you compare options. It does not forecast the season "
              "and does not replace local agricultural advice.")
