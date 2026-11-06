"""Step 15.2: tercile scenario. Analogs only from past seasons whose later rain fell in one third."""
from datetime import date

import pandas as pd
import pytest

from rotate_engine import cards_for_site, find_analogs
from rotate_engine.features import in_season_rain, terciles
from rotate_engine.io import load_imerg
from rotate_engine.pipeline import tercile_years

DATE = date(2026, 11, 13)


def test_in_season_rain_counts_after_the_decision_and_never_fills():
    days = pd.date_range("2009-11-01", "2010-05-31")
    rain = pd.Series(1.0, index=days)
    totals = in_season_rain(rain, DATE, 2027, [2010])
    assert totals[2010] == (date(2010, 4, 30) - date(2009, 11, 13)).days  # 14 Nov .. 30 Apr
    assert in_season_rain(rain.drop(pd.Timestamp("2010-01-05")), DATE, 2027, [2010]).empty


def test_terciles_split_into_thirds():
    labels, (lo, hi) = terciles(pd.Series({y: float(y) for y in range(9)}))
    assert list(labels.value_counts().sort_index()) == [3, 3, 3] and lo < hi


@pytest.mark.parametrize("site_id", ["ctg_anwara", "barind_godagari"])
@pytest.mark.parametrize("tercile", ["dry", "normal", "wet"])
def test_analogs_come_only_from_the_chosen_third(site_id, tercile):
    r = find_analogs(site_id, DATE, tercile=tercile)
    train = list(range(1999, 2027))
    allowed, _ = tercile_years(site_id, DATE, 2027, train, tercile)
    assert {a.year for a in r.analogs.weather_pool} <= allowed
    assert {a.year for a in r.analogs.ndvi_pool} <= allowed
    assert r.confidence.tag == "Scenario" and r.confidence.sentence.startswith(f"What-if ({tercile} season)")
    assert r.warnings[0].startswith(f"Tercile scenario ({tercile} season)")
    assert "not a forecast" in r.warnings[0]


def test_tercile_cards_carry_only_scenario_tags():
    cs = cards_for_site("ctg_anwara", DATE, mode="scenario", tercile="dry")
    js = cs.model_dump_json()
    assert '"Observed"' not in js and '"Derived"' not in js
    assert all(e.source.startswith("What-if (dry season)") for c in cs.cards for e in c.evidence)


def test_tercile_and_shift_combine():
    cs = cards_for_site("barind_godagari", DATE, mode="scenario", tercile="wet", shift={"temp_c": 1})
    assert cs.confidence.sentence.startswith("What-if (temperature +1 °C; wet season)")


def test_tercile_needs_scenario_mode():
    with pytest.raises(ValueError):
        cards_for_site("ctg_anwara", DATE, tercile="dry")


def test_imerg_is_read_with_its_fill_as_nan():
    rain = load_imerg("ctg_anwara")
    assert rain.dropna().ge(0).all() and rain.loc["1998-01-01":"2026-09-14"].notna().all()
