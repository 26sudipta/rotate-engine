"""Step 15.3: GWETROOT root-zone soil wetness as display evidence, labelled model output."""
from datetime import date

from rotate_engine import cards_for_site
from rotate_engine.config import FEATURES

DATE = date(2026, 11, 13)


def soil_items(cs):
    return [e for e in cs.cards[0].evidence if "soil wetness" in e.label]


def test_soil_wetness_shown_where_rain_is_usable():
    (item,) = soil_items(cards_for_site("barind_godagari", DATE))
    assert item.tag == "Observed" and "model output" in item.label
    assert "GWETROOT" in item.source and "not field measurement" in item.source
    assert 0 <= float(item.value.split()[0]) <= 1


def test_soil_wetness_hidden_where_rain_has_the_2015_jump():
    cs = cards_for_site("ctg_anwara", DATE)
    assert not soil_items(cs)
    assert any("soil wetness here follows the same jump" in w for w in cs.warnings)


def test_soil_wetness_hidden_in_a_whatif():
    cs = cards_for_site("barind_godagari", DATE, mode="scenario", shift={"rain_pct": -50})
    assert not soil_items(cs)
    assert any("Soil wetness is not shown in a what-if" in w for w in cs.warnings)


def test_soil_wetness_never_matches():
    assert not any("soil" in f for f in FEATURES)
