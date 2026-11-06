"""Seasons, features and analogs on synthetic data (no dependence on the cached POWER files)."""
from datetime import date

import numpy as np
import pandas as pd
import pytest

from rotate_engine import analogs as core
from rotate_engine import io
from rotate_engine.config import DETREND_FEATURES, FEATURES, WINDOW_DAYS
from rotate_engine.features import feature_table
from rotate_engine.seasons import InsufficientWindowError, current_window, past_windows

UNDETRENDED = tuple(f for f in FEATURES if f not in DETREND_FEATURES)


def synthetic_power(start="1981-01-01", end="2026-11-02", seed=0) -> pd.DataFrame:
    idx = pd.date_range(start, end, freq="D", name="date")
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "PRECTOTCORR": rng.gamma(0.5, 6.0, len(idx)),
        "T2M_MIN": 22 + rng.normal(0, 1, len(idx)),
        "T2M_MAX": 30 + rng.normal(0, 1, len(idx)),
        "RH2M": 80 + rng.normal(0, 3, len(idx)),
        "ALLSKY_SFC_SW_DWN": 17 + rng.normal(0, 1, len(idx)),
    }, index=idx)


def synthetic_table(n=30, seed=1) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    years = range(1990, 1990 + n)
    return pd.DataFrame({"rain_log1p": rng.normal(5.5, 0.5, n), "tmin_c": rng.normal(25, 0.4, n),
                         "rh_pct": rng.normal(82, 3, n)}, index=pd.Index(years, name="season_year"))


# ---- Step 5 -------------------------------------------------------------------------------------

def test_no_future_data():
    power = synthetic_power()
    decision = date(2026, 11, 13)
    window, _ = current_window(power, decision)
    assert window.end < decision
    assert (window.end - window.start).days == WINDOW_DAYS - 1
    for w in past_windows(window, power.index[0].date()):
        assert w.season_year < window.season_year
        assert w.end.month == window.end.month and w.end.day == window.end.day


def test_window_stops_when_too_few_valid_days():
    power = synthetic_power()
    power.loc["2026-09-20":"2026-10-01", "RH2M"] = np.nan  # 12 gap days inside the window
    with pytest.raises(InsufficientWindowError):
        current_window(power, date(2026, 11, 13))


def test_fill_value_becomes_nan(tmp_path, monkeypatch):
    (tmp_path / "data" / "power").mkdir(parents=True)
    (tmp_path / "data" / "raw" / "power").mkdir(parents=True)
    (tmp_path / "data" / "power" / "x.csv").write_text("date,PRECTOTCORR\n2020-01-01,-999.0\n2020-01-02,1.5\n")
    (tmp_path / "data" / "raw" / "power" / "x.json").write_text(
        '{"request_url": "u", "accessed": "2026-11-05", "response": {"header": {"fill_value": -999.0}}}')
    monkeypatch.setenv("ROTATE_ROOT", str(tmp_path))
    df = io.load_power("x")
    assert np.isnan(df.iloc[0, 0]) and df.iloc[1, 0] == 1.5


def test_solar_pre1984_excluded():
    power = synthetic_power()
    window, _ = current_window(power, date(2026, 11, 13))
    table, _ = feature_table(power, past_windows(window, power.index[0].date()))
    assert table.loc[table["start"].map(lambda d: d.year) < 1984, "solar_mj"].isna().all()
    assert table.loc[table["start"].map(lambda d: d.year) >= 1984, "solar_mj"].notna().all()
    assert "solar_mj" not in FEATURES


def test_gappy_season_is_dropped_not_filled():
    power = synthetic_power()
    power.loc["2000-09-20":"2000-10-05", "PRECTOTCORR"] = np.nan
    window, _ = current_window(power, date(2026, 11, 13))
    table, skipped = feature_table(power, past_windows(window, power.index[0].date()))
    assert skipped == [2001] and 2001 not in table.index


# ---- Step 6 -------------------------------------------------------------------------------------

def test_distances_finite_with_near_duplicate_column():
    t = synthetic_table()
    t["rh_pct"] = t["rain_log1p"] * 3 + 1e-9 * np.arange(len(t))  # near-collinear feature
    train = list(t.index[:-1])
    res = core.find_analogs(t, t.index[-1], train)
    assert all(np.isfinite(m.distance) for m in res.matches)


def test_duplicate_row_has_zero_distance_and_ranks_first():
    t = synthetic_table()
    target = t.index[-1]
    t.loc[2000] = t.loc[target]
    # tmin is detrended by year, so a raw copy under another year is only a copy on undetrended features
    res = core.find_analogs(t, target, [y for y in t.index if y != target], features=UNDETRENDED)
    assert res.matches[0].year == 2000 and res.matches[0].distance == pytest.approx(0, abs=1e-9)


def test_identity_precision_is_euclidean_on_z_scores():
    t = synthetic_table()
    target, train = t.index[-1], list(t.index[:-1])
    z_train, z_target = core.standardise(t, target, train)
    d = core.distances(z_train, z_target, np.eye(z_train.shape[1]))
    assert np.allclose(d, np.linalg.norm(z_train - z_target, axis=1))
    res = core.find_analogs(t, target, train, method="euclidean")
    assert [m.year for m in res.matches] == [train[i] for i in np.argsort(d, kind="stable")[:5]]


def test_target_never_in_training_set():
    t = synthetic_table()
    with pytest.raises(ValueError):
        core.find_analogs(t, t.index[-1], list(t.index))


def test_fit_uses_training_years_only():
    t = synthetic_table()
    target, train = t.index[-1], list(t.index[:-1])
    before = core.standardise(t, target, train)[0]
    t.loc[target, list(FEATURES)] = [99.0, 99.0, 99.0]  # changing the target cannot move training z-scores
    assert np.allclose(before, core.standardise(t, target, train)[0])


def test_weights_sum_to_one_and_ties_sort_by_year():
    t = synthetic_table()
    target = t.index[-1]
    t.loc[1985] = t.loc[target]
    t.loc[1986] = t.loc[target]
    res = core.find_analogs(t, target, [y for y in t.index if y != target], features=UNDETRENDED)
    assert [m.year for m in res.matches[:2]] == [1985, 1986]
    assert sum(m.weight for m in res.matches) == pytest.approx(1.0)
