"""Daily POWER -> one row of window features per Boro season."""
from datetime import date, timedelta

import numpy as np
import pandas as pd

from .config import (HEAVY_RAIN_MM, HOT_DAY_TMAX_C, MIN_VALID_DAYS, RAIN, RH, SOIL,
                     SOLAR, SOLAR_FIRST_YEAR, TERCILE_SEASON_END, TMIN)
from .seasons import SeasonWindow, shift_years, valid_days

COLUMNS = ["start", "end", "days_available", "rain_mm", "rain_log1p", "tmin_c", "rh_pct",
           "hot_days", "heavy_rain_days", "soil_wetness", "solar_mj"]


def window_row(power: pd.DataFrame, w: SeasonWindow) -> dict:
    sl = power.loc[pd.Timestamp(w.start):pd.Timestamp(w.end)]
    ok = valid_days(sl)
    days = sl[ok]  # never fill a gap: features use valid days only
    rain = float(days[RAIN].sum())
    solar = np.nan
    if SOLAR in days and w.start.year >= SOLAR_FIRST_YEAR:  # solar is off by default; pre-1984 excluded
        solar = float(days[SOLAR].mean())
    return {
        "start": w.start, "end": w.end, "days_available": int(ok.sum()),
        "rain_mm": rain, "rain_log1p": float(np.log1p(rain)),
        "tmin_c": float(days[TMIN].mean()), "rh_pct": float(days[RH].mean()),
        # display evidence only, never matching features
        "hot_days": int((days["T2M_MAX"] >= HOT_DAY_TMAX_C).sum()) if "T2M_MAX" in days else 0,
        "heavy_rain_days": int((days[RAIN] >= HEAVY_RAIN_MM).sum()),
        "soil_wetness": float(days[SOIL].mean()) if SOIL in days else np.nan,
        "solar_mj": solar,
    }


def shifted(power: pd.DataFrame, w: SeasonWindow, rain_pct: float, temp_c: float,
            rh_points: float) -> pd.DataFrame:
    """A what-if copy of the daily table: only the days of window `w` change."""
    out = power.copy()
    rows = (out.index >= pd.Timestamp(w.start)) & (out.index <= pd.Timestamp(w.end))
    out.loc[rows, RAIN] = out.loc[rows, RAIN] * (1 + rain_pct / 100)
    temps = [c for c in (TMIN, "T2M_MAX") if c in out]
    out.loc[rows, temps] = out.loc[rows, temps] + temp_c
    out.loc[rows, RH] = (out.loc[rows, RH] + rh_points).clip(0, 100)
    if SOIL in out:  # model soil wetness can't be changed consistently by hand: unknown in a what-if
        out.loc[rows, SOIL] = np.nan
    return out


def in_season_rain(rain: pd.Series, decision_date: date, target: int, years: list[int]) -> pd.Series:
    """Total rain from the day after the decision's calendar day to TERCILE_SEASON_END, per season.

    Seasons with any missing day are left out (never filled).
    """
    out = {}
    for y in years:
        start = shift_years(decision_date, y - target) + timedelta(days=1)
        end = date(y, *TERCILE_SEASON_END)
        days = rain.loc[pd.Timestamp(start):pd.Timestamp(end)]
        if start <= end and len(days) == (end - start).days + 1 and days.notna().all():
            out[y] = float(days.sum())
    return pd.Series(out, dtype=float)


def terciles(totals: pd.Series) -> tuple[pd.Series, tuple[float, float]]:
    """("dry" / "normal" / "wet" per season, (upper edge of dry, lower edge of wet))."""
    lo, hi = np.quantile(totals.to_numpy(), [1 / 3, 2 / 3])
    labels = totals.map(lambda v: "dry" if v <= lo else "wet" if v > hi else "normal")
    return labels, (float(lo), float(hi))


def feature_table(power: pd.DataFrame, windows: list[SeasonWindow]) -> tuple[pd.DataFrame, list[int]]:
    """Rows indexed by season year. Seasons with < MIN_VALID_DAYS valid days are dropped and returned."""
    rows, skipped = {}, []
    for w in windows:
        row = window_row(power, w)
        if row["days_available"] < MIN_VALID_DAYS:
            skipped.append(w.season_year)
            continue
        rows[w.season_year] = row
    table = pd.DataFrame.from_dict(rows, orient="index", columns=COLUMNS)
    table.index.name = "season_year"
    return table, skipped

