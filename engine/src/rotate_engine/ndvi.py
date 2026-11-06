"""MOD13Q1 NDVI: QA filter, acquisition-day placement, the peak-window predictand and the curve.

Smoothing is optional display help: the raw points are always kept next to it.
"""
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

from .config import (CLOUD_GAP, HLS_FILL, HLS_HIGH_AEROSOL, HLS_MASK_BITS, LOW_VEG_LABEL, NDVI_FILL,
                     NDVI_FLAG_FROM_YEAR, NDVI_GAP_DAYS, NDVI_LOW_VEG, NDVI_OK_RELIABILITY,
                     NDVI_SMOOTH_ORDER, NDVI_SMOOTH_WINDOW)

P = "MOD13Q1_061__250m_16_days_"


def _acquired(start: pd.Series, doy: pd.Series) -> pd.Series:
    """Acquisition day from the composite start date and the pixel's day of year."""
    doy = doy.astype(int)
    # a composite starting in late December can hold a pixel acquired in early January
    year = start.dt.year + ((doy < start.dt.day_of_year - 200)).astype(int)
    return pd.to_datetime(year.astype(str) + doy.astype(str).str.zfill(3), format="%Y%j")


def clean_points(raw: pd.DataFrame, ndvi_id: str) -> pd.DataFrame:
    """QA-passed points for one AppEEARS point id, placed on their actual acquisition day."""
    g = raw[raw["ID"] == ndvi_id]
    g = g[(g[P + "NDVI"] != NDVI_FILL) & g[P + "pixel_reliability"].isin(NDVI_OK_RELIABILITY)]
    acquired = _acquired(pd.to_datetime(g["Date"]), g[P + "composite_day_of_the_year"])
    return pd.DataFrame({"date": acquired.to_numpy(), "ndvi": g[P + "NDVI"].to_numpy(float),
                         "reliability": g[P + "pixel_reliability"].to_numpy(int)}
                        ).sort_values("date").reset_index(drop=True)


ORNL_SCALE = 0.0001  # ORNL serves raw integers, fill -3000 (the AppEEARS CSV is already scaled)
B = "250m_16_days_"


def _ornl_band(table: pd.DataFrame, band: str, cols: list[str]) -> pd.DataFrame:
    return table[table["band"] == B + band].set_index("calendar_date")[cols]


def ornl_points(table: pd.DataFrame) -> pd.DataFrame:
    """QA-passed centre-pixel points from an ORNL single-pixel file, on their acquisition day."""
    ndvi = _ornl_band(table, "NDVI", ["p0"])["p0"]
    rel = _ornl_band(table, "pixel_reliability", ["p0"])["p0"].reindex(ndvi.index)
    doy = _ornl_band(table, "composite_day_of_the_year", ["p0"])["p0"].reindex(ndvi.index)
    keep = ((ndvi != NDVI_FILL) & rel.isin(NDVI_OK_RELIABILITY) & (doy > 0)).to_numpy()
    start = pd.Series(pd.to_datetime(ndvi.index[keep]))
    return pd.DataFrame({"date": _acquired(start, pd.Series(doy.to_numpy()[keep])).to_numpy(),
                         "ndvi": ndvi.to_numpy(float)[keep] * ORNL_SCALE,
                         "reliability": rel.to_numpy()[keep].astype(int)}
                        ).sort_values("date").reset_index(drop=True)


def window_stats(table: pd.DataFrame) -> pd.DataFrame:
    """Per composite (start date): mean, min and max NDVI of the QA-passed pixels in the central 3x3."""
    pcols = [c for c in table.columns if c.startswith("p")]
    side = int(round(len(pcols) ** 0.5))
    mid = side // 2
    idx = [f"p{(mid + dr) * side + mid + dc}" for dr in (-1, 0, 1) for dc in (-1, 0, 1)]
    ndvi = _ornl_band(table, "NDVI", idx)
    rel = _ornl_band(table, "pixel_reliability", idx).reindex(ndvi.index)
    good = ndvi.where((ndvi != NDVI_FILL) & rel.isin(NDVI_OK_RELIABILITY)) * ORNL_SCALE
    out = pd.DataFrame({"date": pd.to_datetime(ndvi.index), "mean": good.mean(axis=1),
                        "min": good.min(axis=1), "max": good.max(axis=1), "n_ok": good.notna().sum(axis=1)})
    return out[out["n_ok"] > 0].sort_values("date").reset_index(drop=True)


HLS_SATELLITE = {"HLSS30": "hls_s30", "HLSL30": "hls_l30"}


def hls_merged(vi: pd.DataFrame, fmask: pd.DataFrame, sensor: str) -> pd.DataFrame:
    """One HLS sensor's NDVI rows joined to their Fmask (NaN where no mask row): ID, date, ndvi, fmask, satellite."""
    keys = ["ID", "Date", "HLS_Tile"]
    m = vi[keys + [f"{sensor}_VI_020_NDVI"]].merge(fmask[keys + [f"{sensor}_020_Fmask"]], on=keys, how="left")
    return pd.DataFrame({"ID": m["ID"], "date": pd.to_datetime(m["Date"]), "ndvi": m[f"{sensor}_VI_020_NDVI"],
                         "fmask": m[f"{sensor}_020_Fmask"], "satellite": HLS_SATELLITE[sensor]})


def hls_passed(m: pd.DataFrame) -> pd.Series:
    """Not fill, has a mask, and no cloud, cloud-adjacent, shadow or snow bit. Water and haze pass."""
    bits = m["fmask"].fillna(0).astype(int)
    return (m["ndvi"] != HLS_FILL) & m["fmask"].notna() & ((bits & HLS_MASK_BITS) == 0)


def hls_points(m: pd.DataFrame) -> pd.DataFrame:
    """QA-passed HLS points; reliability 1 marks high aerosol (flagged), 0 otherwise."""
    g = m[hls_passed(m)]
    haze = (g["fmask"].astype(int) // 64 % 4) == HLS_HIGH_AEROSOL  # bits 6-7 (pandas has no >>)
    return (pd.DataFrame({"date": g["date"], "ndvi": g["ndvi"].astype(float), "reliability": haze.astype(int),
                          "satellite": g["satellite"]})
            .drop_duplicates(["date", "satellite"])  # a field on a tile overlap is seen twice the same day
            .sort_values(["date", "satellite"]).reset_index(drop=True))


def hls_share_by_month(m: pd.DataFrame, start=None, end=None) -> dict[str, float]:
    """Share of HLS acquisitions per calendar month that pass the Fmask filter."""
    keep = m["date"].notna()
    if start:
        keep &= m["date"] >= pd.Timestamp(start)
    if end:
        keep &= m["date"] <= pd.Timestamp(end)
    share = hls_passed(m)[keep].groupby(m["date"][keep].dt.month).mean()
    return {f"{mo:02d}": round(float(v), 3) for mo, v in share.items()}


def peak_values(points: pd.DataFrame, doy_window: tuple[int, int]) -> pd.Series:
    """Mean NDVI of points acquired inside the day-of-year window, per calendar (= harvest) year."""
    doy = points["date"].dt.day_of_year
    inside = points[(doy >= doy_window[0]) & (doy <= doy_window[1])]
    return inside.groupby(inside["date"].dt.year)["ndvi"].mean().rename("peak_ndvi")


def anomalies(peaks: pd.Series, train_years: list[int]) -> pd.Series:
    """Peak NDVI minus its linear trend, the trend fitted on the training years only."""
    train = peaks.loc[[y for y in train_years if y in peaks.index]]
    b, a = np.polyfit(train.index.to_numpy(float), train.to_numpy(), 1)
    return (peaks - (a + b * peaks.index.to_numpy(float))).rename("ndvi_anomaly")


def flagged(points: pd.DataFrame) -> pd.Series:
    """Reliability 1 (MODIS: marginal; HLS: high aerosol) or a MODIS composite from 2025 on (orbit drift)."""
    modis = ~points["satellite"].str.startswith("hls") if "satellite" in points else True
    return (points["reliability"] == 1) | ((points["date"].dt.year >= NDVI_FLAG_FROM_YEAR) & modis)


def runs(points: pd.DataFrame) -> list[pd.DataFrame]:
    """Split the curve wherever two points are more than NDVI_GAP_DAYS apart."""
    if points.empty:
        return []
    breaks = (points["date"].diff().dt.days > NDVI_GAP_DAYS).cumsum()
    return [run for _, run in points.groupby(breaks)]


def gap_spans(points: pd.DataFrame) -> list[tuple]:
    """(last day before, first day after, label) for every break in the curve."""
    parts = runs(points)
    return [(a["date"].iloc[-1].date(), b["date"].iloc[0].date(), CLOUD_GAP) for a, b in zip(parts, parts[1:])]


def with_smooth(points: pd.DataFrame) -> pd.DataFrame:
    """Add a "smooth" column: Savitzky-Golay within each gap-free run, NaN where a run is too short.

    shortcut: treats the ~16-day acquisition spacing as even; switch to a weighted Whittaker if the
    team wants an exact-time smoother.
    """
    smooth = pd.Series(np.nan, index=points.index)
    for run in runs(points):
        if len(run) >= NDVI_SMOOTH_WINDOW:
            smooth.loc[run.index] = savgol_filter(run["ndvi"].to_numpy(), NDVI_SMOOTH_WINDOW,
                                                  NDVI_SMOOTH_ORDER)
    return points.assign(smooth=smooth)


def low_veg_spans(points: pd.DataFrame) -> list[tuple]:
    """At least two consecutive points below NDVI_LOW_VEG, never across a gap.

    Uses the smoothed line where there is one (report NDVI item 6), else the raw value.
    """
    out = []
    for run in runs(points):
        level = run["smooth"].fillna(run["ndvi"]) if "smooth" in run else run["ndvi"]
        low = level < NDVI_LOW_VEG
        for _, block in run[low].groupby((~low).cumsum()[low]):
            if len(block) >= 2:
                out.append((block["date"].iloc[0].date(), block["date"].iloc[-1].date(), LOW_VEG_LABEL))
    return out


def qa_share_by_month(raw: pd.DataFrame, ndvi_id: str, start=None, end=None) -> dict[str, float]:
    """Share of composites per calendar month that pass the QA filter."""
    g = raw[raw["ID"] == ndvi_id]
    when = pd.to_datetime(g["Date"])
    keep = (when >= pd.Timestamp(start)) if start else when.notna()
    if end:
        keep &= when <= pd.Timestamp(end)
    g, when = g[keep], when[keep]
    ok = (g[P + "NDVI"] != NDVI_FILL) & g[P + "pixel_reliability"].isin(NDVI_OK_RELIABILITY)
    share = ok.groupby(when.dt.month).mean()
    return {f"{m:02d}": round(float(v), 3) for m, v in share.items()}
