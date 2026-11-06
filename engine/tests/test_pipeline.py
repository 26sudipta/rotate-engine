"""The engine on the cached POWER files in data/ (offline)."""
from datetime import date

import pandas as pd
import pytest

from rotate_engine import find_analogs
from rotate_engine.config import POOL_FIRST_SEASON
from rotate_engine.models import AnalogResult, NotCached
from rotate_engine.pipeline import training_seasons

DECISION = date(2026, 11, 13)


def test_no_season_before_cutoff_enters_training():
    table = pd.DataFrame(index=pd.Index(range(1982, 2028), name="season_year"))
    train = training_seasons(table, 2027)
    assert min(train) == POOL_FIRST_SEASON and max(train) == 2026


@pytest.mark.parametrize("site_id", ["ctg_anwara", "barind_godagari"])
def test_real_analogs_respect_cutoff(site_id):
    res = find_analogs(site_id, DECISION)
    assert isinstance(res, AnalogResult)
    years = [a.year for a in res.analogs.weather_pool]
    assert len(years) == 5 and all(POOL_FIRST_SEASON <= y < res.season_year for y in years)
    assert res.window.end < DECISION


def test_anwara_rain_not_used_or_shown():
    res = find_analogs("ctg_anwara", DECISION)
    assert all(a.features.rain_mm is None for a in res.analogs.weather_pool)
    assert any("Rainfall is not used" in w for w in res.warnings)


def test_unknown_site_is_not_cached_not_an_error():
    assert isinstance(find_analogs("nowhere", DECISION), NotCached)
