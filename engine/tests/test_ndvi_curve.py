"""Step 11: the NDVI curve (QA filter, cloud gaps, low-vegetation windows, flags)."""
import json
from datetime import date

import pandas as pd

from rotate_engine import ndvi, ndvi_series
from rotate_engine.__main__ import main
from rotate_engine.config import CLOUD_GAP, LOW_VEG_LABEL
from rotate_engine.models import NotCached


def pts(rows):
    return pd.DataFrame({"date": pd.to_datetime([r[0] for r in rows]), "ndvi": [r[1] for r in rows],
                         "reliability": [r[2] if len(r) > 2 else 0 for r in rows]})


def test_gap_stays_a_marked_gap():
    p = pts([("2020-01-01", 0.5), ("2020-01-17", 0.5), ("2020-03-20", 0.6), ("2020-04-05", 0.6)])
    assert ndvi.gap_spans(p) == [(date(2020, 1, 17), date(2020, 3, 20), CLOUD_GAP)]
    assert len(ndvi.runs(p)) == 2  # the line breaks; nothing is filled in between


def test_low_veg_needs_two_points_and_never_crosses_a_gap():
    p = pts([("2020-01-01", 0.2), ("2020-01-17", 0.25), ("2020-02-02", 0.6),
             ("2020-02-18", 0.2), ("2020-04-01", 0.2)])  # last two are split by a 43-day gap
    assert ndvi.low_veg_spans(p) == [(date(2020, 1, 1), date(2020, 1, 17), LOW_VEG_LABEL)]


def test_flags_marginal_and_2025_points():
    p = pts([("2024-06-01", 0.5, 0), ("2024-06-17", 0.5, 1), ("2025-01-01", 0.5, 0)])
    assert list(ndvi.flagged(p)) == [False, True, True]


def test_series_for_demo_site():
    s = ndvi_series("ctg_anwara", date(2024, 11, 1), date(2026, 10, 31))
    assert s.status == "ok" and s.points and s.tag == "Observed"
    assert all(date(2024, 11, 1) <= pt.date <= date(2026, 10, 31) for pt in s.points)
    assert all(pt.reliability in (0, 1) for pt in s.points)
    assert all(0 <= v <= 1 for v in s.qa_pass_share_by_month.values())
    assert s.gaps and all(g.label == CLOUD_GAP for g in s.gaps)


def test_unknown_site_and_empty_range():
    assert isinstance(ndvi_series("nowhere"), NotCached)
    assert ndvi_series("ctg_anwara", date(1990, 1, 1), date(1990, 12, 31)).status == "pending"


def test_cli_ndvi(tmp_path):
    out = tmp_path / "n.json"
    assert main(["ndvi", "--site", "barind_godagari", "--from", "2025-11-01", "--out", str(out)]) == 0
    assert json.loads(out.read_text())["status"] == "ok"
