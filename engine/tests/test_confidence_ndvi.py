from datetime import date

import pandas as pd
import pytest

from rotate_engine import find_analogs, ndvi
from rotate_engine.confidence import chance_rate, confidence

P = ndvi.P


def test_chance_rate_k5():
    assert chance_rate(5, 4) == pytest.approx(0.375)
    assert chance_rate(5, 5) == pytest.approx(0.0625)
    assert chance_rate(5, 3) == 1.0


def test_confidence_labels_and_tag():
    c = confidence([-0.1, -0.2, -0.05, -0.3, 0.1], [0.3, 0.2, 0.2, 0.2, 0.1], "Boro greenness")
    assert (c.agree_count, c.direction, c.label, c.tag) == (4, "below_normal", "moderate", "Derived")
    assert c.weighted_agreement == pytest.approx(0.9)
    assert "38%" in c.sentence and "In 4 of the 5 past seasons" in c.sentence
    assert "not a prediction" in c.sentence
    assert confidence([0.1] * 5, [0.2] * 5, "x").label == "high"
    assert confidence([0.1, 0.1, 0.1, -0.1, -0.1], [0.2] * 5, "x").label == "split"


def raw_rows(rows):
    return pd.DataFrame([{"ID": "s", "Date": d, P + "NDVI": v, P + "pixel_reliability": r,
                          P + "composite_day_of_the_year": doy} for d, v, r, doy in rows])


def test_ndvi_filters_fill_and_bad_reliability_and_places_acquisition_day():
    raw = raw_rows([("2010-03-06", 0.6, 0, 70), ("2010-03-22", -3000, -1, -1),
                    ("2010-04-07", 0.4, 3, 100), ("2010-12-19", 0.3, 1, 2)])
    pts = ndvi.clean_points(raw, "s")
    assert list(pts["ndvi"]) == [0.6, 0.3]
    assert list(pts["date"].dt.date) == [date(2010, 3, 11), date(2011, 1, 2)]  # Dec composite, Jan pixel


def test_ndvi_anomaly_trend_uses_training_years_only():
    peaks = pd.Series({2001: 0.5, 2002: 0.6, 2003: 0.7, 2004: 0.9})
    a = ndvi.anomalies(peaks, [2001, 2002, 2003])
    assert a[[2001, 2002, 2003]].abs().max() == pytest.approx(0, abs=1e-12)
    assert a[2004] == pytest.approx(0.1)


@pytest.mark.parametrize("site_id", ["ctg_anwara", "barind_godagari"])
def test_analog_output_has_ndvi_confidence(site_id):
    res = find_analogs(site_id, date(2026, 11, 13))
    assert res.ndvi_status == "ok" and res.confidence.basis == "ndvi"
    assert res.confidence.tag == "Derived" and len(res.analogs.ndvi_pool) == 5
    assert all(2001 <= a.year <= 2024 for a in res.analogs.ndvi_pool)
    assert res.provenance.ndvi is not None
