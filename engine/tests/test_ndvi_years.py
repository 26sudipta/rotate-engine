"""Step 13: smoothing beside the raw points, and one Boro-season curve per year."""
import json
from datetime import date

import pandas as pd

from rotate_engine import find_analogs, ndvi, ndvi_for_years
from rotate_engine.__main__ import main
from rotate_engine.config import CLOUD_GAP
from rotate_engine.models import NdviYears, NotCached


def test_smoothing_keeps_raw_and_never_crosses_a_gap():
    days = ["2020-01-01", "2020-01-17", "2020-02-02", "2020-02-18", "2020-03-05", "2020-03-21",
            "2020-06-01", "2020-06-17"]  # 6-point run, 72-day gap, 2-point run
    raw = [0.30, 0.45, 0.62, 0.70, 0.55, 0.40, 0.20, 0.25]
    p = ndvi.with_smooth(pd.DataFrame({"date": pd.to_datetime(days), "ndvi": raw, "reliability": 0}))
    assert list(p["ndvi"]) == raw
    assert p["smooth"].iloc[:6].notna().all() and p["smooth"].iloc[6:].isna().all()


def test_years_mark_gaps_flag_2025_and_report_missing():
    out = ndvi_for_years("ctg_anwara", [2025, 1990, 2010, 2010])
    assert isinstance(out, NdviYears) and out.status == "ok" and out.tag == "Observed"
    by_year = {y.year: y for y in out.years}
    assert list(by_year) == [1990, 2010, 2025]
    assert by_year[1990].status == "missing" and not by_year[1990].points
    assert by_year[2025].status == "flagged"
    y = by_year[2010]
    assert y.status == "ok" and (y.start, y.end) == (date(2009, 11, 1), date(2010, 5, 31))
    assert all(y.start <= pt.date <= y.end for pt in y.points)
    assert all(g.label == CLOUD_GAP for yr in out.years for g in yr.gaps)
    for g in (g for yr in out.years for g in yr.gaps):  # a gap stays a gap: no point inside it
        assert not [pt for yr in out.years for pt in yr.points if g.start < pt.date < g.end]


def test_years_for_the_ndvi_look_alike_years():
    pool = find_analogs("barind_godagari", date(2026, 11, 13)).analogs.ndvi_pool
    out = ndvi_for_years("barind_godagari", [a.year for a in pool])
    assert [y.year for y in out.years] == sorted(a.year for a in pool)
    assert all(y.points for y in out.years)


def test_unknown_site():
    assert isinstance(ndvi_for_years("nowhere", [2010]), NotCached)


def test_cli_ndvi_years(tmp_path):
    out = tmp_path / "y.json"
    assert main(["ndvi-years", "--site", "ctg_anwara", "--years", "2014", "2019", "--out", str(out)]) == 0
    assert [y["year"] for y in json.loads(out.read_text())["years"]] == [2014, 2019]
