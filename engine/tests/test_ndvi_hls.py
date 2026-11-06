"""Step 15.5: the separate 30 m HLS curve (HLSS30_VI + HLSL30_VI, Fmask-filtered), display only."""
from datetime import date

import pandas as pd
import pytest

from rotate_engine import ndvi, ndvi_series
from rotate_engine.__main__ import main
from rotate_engine.models import NotCached


def hls(rows, sensor="HLSS30"):
    """rows: (date, ndvi, fmask or None) -> the VI and Fmask tables AppEEARS returns."""
    vi = pd.DataFrame([{"ID": "s", "Date": d, "HLS_Tile": "T", f"{sensor}_VI_020_NDVI": v} for d, v, _ in rows])
    fm = pd.DataFrame([{"ID": "s", "Date": d, "HLS_Tile": "T", f"{sensor}_020_Fmask": f}
                       for d, _, f in rows if f is not None])
    return ndvi.hls_merged(vi, fm, sensor)


def test_fmask_drops_cloud_shadow_snow_fill_and_unmasked_keeps_haze_flagged():
    m = hls([("2020-01-01", 0.6, 0),          # clear
             ("2020-01-02", 0.6, 0b10),       # cloud
             ("2020-01-03", 0.6, 0b100),      # adjacent to cloud/shadow
             ("2020-01-04", 0.6, 0b1000),     # cloud shadow
             ("2020-01-05", 0.6, 0b10000),    # snow/ice
             ("2020-01-06", 0.2, 0b100000),   # water: a real flooded-field look, kept
             ("2020-01-07", 0.7, 0b11000000),  # high aerosol: kept, flagged
             ("2020-01-08", -19999, 0),       # fill
             ("2020-01-09", 0.6, None)])      # no Fmask row: not trusted
    p = ndvi.hls_points(m)
    assert [d.day for d in p["date"]] == [1, 6, 7]
    assert list(p["reliability"]) == [0, 0, 1] and list(ndvi.flagged(p)) == [False, False, True]
    assert ndvi.hls_share_by_month(m) == {"01": round(3 / 9, 3)}


def test_hls_is_not_flagged_for_modis_orbit_drift():
    p = ndvi.hls_points(hls([("2025-03-01", 0.6, 0)]))
    modis = p.assign(satellite="terra")
    assert list(ndvi.flagged(p)) == [False] and list(ndvi.flagged(modis)) == [True]


@pytest.mark.parametrize("site_id", ["ctg_anwara", "barind_godagari"])
def test_hls_curve_is_separate_from_modis(site_id):
    s = ndvi_series(site_id, hls=True)
    assert s.status == "ok" and s.tag == "Observed" and "30 m" in s.product
    assert {p.satellite for p in s.points} == {"hls_s30", "hls_l30"}
    dates = [p.date for p in s.points]
    assert dates == sorted(dates) and dates[0] >= date(2015, 11, 1)
    assert all(p.satellite == "terra" for p in ndvi_series(site_id).points)  # MODIS curve untouched


def test_hls_date_range_and_unknown_site():
    s = ndvi_series("ctg_anwara", date(2024, 11, 1), date(2025, 5, 31), hls=True)
    assert all(date(2024, 11, 1) <= p.date <= date(2025, 5, 31) for p in s.points)
    assert isinstance(ndvi_series("nowhere", hls=True), NotCached)


def test_missing_hls_files_is_pending(monkeypatch):
    from rotate_engine import pipeline
    from rotate_engine.io import NotCachedError

    def missing(product):
        raise NotCachedError(f"HLS pending: no {product} results CSV in data/ndvi/hls/")
    monkeypatch.setattr(pipeline, "load_hls", missing)
    s = ndvi_series("ctg_anwara", hls=True)
    assert s.status == "pending" and s.points == []


def test_hls_cannot_mix_with_aqua_or_window():
    with pytest.raises(ValueError):
        ndvi_series("ctg_anwara", aqua=True, hls=True)
    assert main(["ndvi", "--site", "ctg_anwara", "--hls", "--window"]) == 2
