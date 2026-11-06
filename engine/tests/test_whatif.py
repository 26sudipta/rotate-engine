"""Step 15.1: the what-if slider. Only this season's window changes; output carries only Scenario tags."""
from datetime import date

import pytest
from pydantic import ValidationError

from rotate_engine import cards_for_site, find_analogs
from rotate_engine.models import Shift
from rotate_engine.pipeline import season_features

DATE = date(2026, 11, 13)
DRY_HOT = {"mode": "scenario", "shift": {"rain_pct": -50, "temp_c": 1.5}}


def test_shift_changes_only_this_seasons_window():
    w, base, _, _ = season_features("barind_godagari", DATE)
    _, what_if, _, _ = season_features("barind_godagari", DATE, Shift(rain_pct=-50, temp_c=1.5, rh_points=-10))
    past = base.index[base.index < w.season_year]
    assert what_if.loc[past].equals(base.loc[past])
    now_b, now_w = base.loc[w.season_year], what_if.loc[w.season_year]
    assert now_w["rain_mm"] == pytest.approx(now_b["rain_mm"] * 0.5)
    assert now_w["tmin_c"] == pytest.approx(now_b["tmin_c"] + 1.5)
    assert now_w["rh_pct"] <= now_b["rh_pct"]


def test_zero_shift_matches_season_to_date():
    a = find_analogs("barind_godagari", DATE)
    b = find_analogs("barind_godagari", DATE, shift=Shift())
    assert a.analogs == b.analogs and b.confidence.tag == "Scenario"


@pytest.mark.parametrize("site_id", ["ctg_anwara", "barind_godagari"])
def test_whatif_cards_carry_only_scenario_tags(site_id):
    cs = cards_for_site(site_id, DATE, **DRY_HOT)
    assert cs.request.mode == "scenario" and cs.confidence.tag == "Scenario"
    assert cs.confidence.sentence.startswith("What-if (rain -50%, temperature +1.5 °C):")
    assert cs.warnings[0].startswith("What-if scenario")
    for card in cs.cards:
        assert all(e.tag == "Scenario" and e.label.startswith("What-if: ")
                   and e.source.startswith("What-if (rain -50%") for e in card.evidence)
    js = cs.model_dump_json()
    assert '"Observed"' not in js and '"Derived"' not in js


def test_rain_shift_is_flagged_where_rain_is_not_matched():
    cs = cards_for_site("ctg_anwara", DATE, mode="scenario", shift={"rain_pct": -30})
    assert any("rain change has no effect" in w for w in cs.warnings)


@pytest.mark.parametrize("bad", [{"mode": "scenario"}, {"shift": {"rain_pct": -20}},
                                 {"mode": "scenario", "shift": {"temp_c": 9}}])
def test_shift_and_mode_validated(bad):
    with pytest.raises(ValidationError):
        cards_for_site("ctg_anwara", DATE, **bad)
