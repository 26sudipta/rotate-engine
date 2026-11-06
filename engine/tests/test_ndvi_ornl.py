"""Step 15.5: Aqua (MYD13Q1) interleaving and the 3x3-pixel spread, from ORNL files."""
from datetime import date

import pandas as pd

from rotate_engine import ndvi, ndvi_for_years, ndvi_series
from rotate_engine.models import NotCached

B = "250m_16_days_"


def ornl(rows, n=1):
    """rows: (calendar_date, band suffix, [pixel values])."""
    return pd.DataFrame([{"calendar_date": d, "band": B + b, **{f"p{i}": v for i, v in enumerate(vals)}}
                         for d, b, vals in rows])


def test_ornl_points_scale_filter_and_acquisition_day():
    t = ornl([("2010-03-06", "NDVI", [6000]), ("2010-03-06", "pixel_reliability", [0]),
              ("2010-03-06", "composite_day_of_the_year", [70]),
              ("2010-03-22", "NDVI", [-3000]), ("2010-03-22", "pixel_reliability", [-1]),
              ("2010-03-22", "composite_day_of_the_year", [-1]),
              ("2010-04-07", "NDVI", [5000]), ("2010-04-07", "pixel_reliability", [3]),
              ("2010-04-07", "composite_day_of_the_year", [100])])
    p = ndvi.ornl_points(t)
    assert list(p["ndvi"]) == [0.6] and list(p["date"].dt.date) == [date(2010, 3, 11)]


def test_window_uses_the_central_3x3_and_only_qa_passed_pixels():
    grid = [1000] * 81
    for i in (30, 31, 32, 39, 40, 41, 48, 49, 50):  # central 3x3 of a 9x9 grid
        grid[i] = 5000
    grid[40], rel = 9000, [0] * 81
    rel[41] = 3  # cloudy: left out
    w = ndvi.window_stats(ornl([("2024-01-01", "NDVI", grid), ("2024-01-01", "pixel_reliability", rel)]))
    assert w.loc[0, "n_ok"] == 8 and w.loc[0, "max"] == 0.9 and w.loc[0, "min"] == 0.5


def test_aqua_interleaves_for_display_only():
    terra = ndvi_series("barind_godagari", date(2020, 11, 1), date(2021, 5, 31))
    both = ndvi_series("barind_godagari", date(2020, 11, 1), date(2021, 5, 31), aqua=True)
    sats = {p.satellite for p in both.points}
    assert sats == {"terra", "aqua"} and len(both.points) > len(terra.points)
    raw = lambda pts: [(p.date, p.ndvi, p.reliability, p.flagged) for p in pts]
    # raw Terra points are untouched; only the smoothed line runs through the extra Aqua points
    assert raw(p for p in both.points if p.satellite == "terra") == raw(terra.points)
    assert "MYD13Q1" in both.product and all(p.satellite == "terra" for p in terra.points)
    dates = [p.date for p in both.points]
    assert dates == sorted(dates)


def test_window_spread_for_recent_seasons():
    s = ndvi_series("ctg_anwara", date(2023, 11, 1), date(2026, 10, 31), window=True)
    assert s.window_3x3 and all(1 <= w.n_ok <= 9 and w.min <= w.mean <= w.max for w in s.window_3x3)
    assert not ndvi_series("ctg_anwara", date(2023, 11, 1), date(2026, 10, 31)).window_3x3


def test_years_with_aqua():
    y = ndvi_for_years("ctg_anwara", [2022], aqua=True).years[0]
    assert {p.satellite for p in y.points} == {"terra", "aqua"}


def test_missing_ornl_file_is_not_cached(monkeypatch):
    from rotate_engine import pipeline
    from rotate_engine.io import NotCachedError

    def missing(*_):
        raise NotCachedError("no ORNL file")
    monkeypatch.setattr(pipeline, "load_ornl", missing)
    assert isinstance(ndvi_series("ctg_anwara", aqua=True), NotCached)
