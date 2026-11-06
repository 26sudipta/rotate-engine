"""Decision windows and Boro season labels (a season is labelled by its harvest year)."""
from dataclasses import dataclass
from datetime import date, timedelta

import pandas as pd

from .config import BORO_NEW_SEASON_MONTH, MATCH_PARAMS, MIN_VALID_DAYS, STALE_WINDOW_DAYS, WINDOW_DAYS


class InsufficientWindowError(ValueError):
    """The matching window has too few valid days; never fill, stop instead."""


@dataclass(frozen=True)
class SeasonWindow:
    season_year: int  # Boro harvest year
    start: date
    end: date


def boro_season_year(d: date) -> int:
    return d.year + 1 if d.month >= BORO_NEW_SEASON_MONTH else d.year


def shift_years(d: date, years: int) -> date:
    return (pd.Timestamp(d) + pd.DateOffset(years=years)).date()  # 29 Feb -> 28 Feb


def valid_days(power: pd.DataFrame) -> pd.Series:
    """True on days where every matching parameter is present."""
    return power[list(MATCH_PARAMS)].notna().all(axis=1)


def current_window(power: pd.DataFrame, decision_date: date) -> tuple[SeasonWindow, list[str]]:
    """The WINDOW_DAYS ending at the last valid day strictly before the decision date."""
    ok = valid_days(power)
    before = ok[(ok.index < pd.Timestamp(decision_date)) & ok]
    if before.empty:
        raise InsufficientWindowError(f"no valid POWER day before {decision_date}")
    end = before.index[-1].date()
    start = end - timedelta(days=WINDOW_DAYS - 1)
    warnings = []
    lag = (decision_date - end).days
    if lag > STALE_WINDOW_DAYS:
        warnings.append(f"The matching window ends {lag} days before the decision date ({end}); "
                        "refetch POWER data closer to the decision.")
    n = int(ok[pd.Timestamp(start):pd.Timestamp(end)].sum())
    if n < MIN_VALID_DAYS:
        raise InsufficientWindowError(f"only {n} valid days in {start}..{end} (need {MIN_VALID_DAYS})")
    return SeasonWindow(boro_season_year(decision_date), start, end), warnings


def past_windows(current: SeasonWindow, first_data_day: date) -> list[SeasonWindow]:
    """The same calendar window in every earlier season whose window lies inside the data."""
    out = []
    for back in range(1, 200):
        start = shift_years(current.start, -back)
        if start < first_data_day:
            break
        out.append(SeasonWindow(current.season_year - back, start, shift_years(current.end, -back)))
    return sorted(out, key=lambda w: w.season_year)
