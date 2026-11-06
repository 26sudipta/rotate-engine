import json
import re
from datetime import date

import jsonschema
import pytest

from rotate_engine import build_cards, default_request
from rotate_engine.__main__ import main
from rotate_engine.io import root
from rotate_engine.models import CardSet, NotCached
from rotate_engine.rules import load_rules

DECISION = date(2026, 11, 13)
BANNED = re.compile(r"\bbest\b|should plant|you should", re.IGNORECASE)


def cards_for(site_id: str, **overrides) -> CardSet:
    res = build_cards(default_request(site_id, DECISION, **overrides))
    assert isinstance(res, CardSet)
    return res


CASES = [("ctg_anwara", {"salinity_class": "slight_4_8"}),
         ("barind_godagari", {"constraints": {"water_availability": "low"}}),
         ("ctg_anwara", {"salinity_class": "moderate_8_12"}),
         ("ctg_anwara", {"current_rotation": "fallow-fallow-t_aman"})]


@pytest.mark.parametrize("site_id,overrides", CASES)
def test_three_cards_first_is_existing(site_id, overrides):
    cs = cards_for(site_id, **overrides)
    assert len(cs.cards) == 3 and cs.cards[0].is_existing
    assert [c.is_existing for c in cs.cards[1:]] == [False, False]
    assert cs.cards[0].strategy.slots == list(load_rules().pattern(cs.request.current_rotation).slots)
    assert len({tuple(c.strategy.slots) for c in cs.cards}) == 3


@pytest.mark.parametrize("site_id,overrides", CASES)
def test_every_evidence_has_tag_and_source(site_id, overrides):
    for card in cards_for(site_id, **overrides).cards:
        assert card.evidence
        assert all(e.tag in ("Observed", "Derived", "Scenario") and e.source for e in card.evidence)


@pytest.mark.parametrize("site_id,overrides", CASES)
def test_every_benefit_has_citation(site_id, overrides):
    ids = {c.citation_id for c in load_rules().citations}
    for card in cards_for(site_id, **overrides).cards:
        assert all(b.citation_id in ids for b in card.benefits)
        assert all(r.citation_id is None or r.citation_id in ids for r in card.risks)
        assert card.needs_local_review is True


@pytest.mark.parametrize("site_id,overrides", CASES)
def test_no_prescriptive_wording(site_id, overrides):
    text = cards_for(site_id, **overrides).model_dump_json()
    assert not BANNED.search(text)


def test_high_salinity_shows_fallow_or_local_review_card():
    cs = cards_for("ctg_anwara", salinity_class="moderate_8_12")
    assert cs.cards[-1].strategy.name == "Fallow, short oilseed, or local review"


def test_salinity_filter_drops_crops_above_threshold():
    cs = cards_for("ctg_anwara", salinity_class="slight_4_8")
    alt_slots = {s for c in cs.cards[1:] for s in c.strategy.slots}
    assert not alt_slots & {"maize", "groundnut"}  # whole-season thresholds 1.7 and 3.2 dS/m < 4


def test_risks_ranked_high_first():
    order = {"high": 0, "medium": 1, "low": 2}
    for card in cards_for("ctg_anwara", salinity_class="slight_4_8").cards:
        needs = [order[r.review_need] for r in card.risks]
        assert needs == sorted(needs)


def test_priorities_change_ranking():
    water = cards_for("barind_godagari", priorities={"water": 1.0})
    nitrogen = cards_for("barind_godagari", priorities={"soil_n": 1.0})
    assert [c.strategy.name for c in water.cards] != [c.strategy.name for c in nitrogen.cards]
    assert water.cards[2].score_breakdown["water"] > 0


def test_unreviewed_rules_warned():
    assert any("unreviewed draft" in w for w in cards_for("ctg_anwara").warnings)


def test_unknown_site_is_not_cached():
    request = default_request("ctg_anwara", DECISION).model_copy(update={"site_id": "nowhere"})
    assert isinstance(build_cards(request), NotCached)


def test_cli_cards_validates_against_schema(tmp_path):
    out = tmp_path / "cards.json"
    assert main(["cards", "--site", "ctg_anwara", "--date", "2026-11-13", "--out", str(out)]) == 0
    schema = json.loads((root() / "schemas" / "card_set.schema.json").read_text())
    jsonschema.validate(json.loads(out.read_text()), schema)


@pytest.mark.parametrize("site_id,overrides", CASES + [
    ("barind_godagari", {"priorities": {"soil_n": 1.0}}),
    ("barind_godagari", {"priorities": {"water": 1.0}})])
def test_role_words_match_sourced_attributes(site_id, overrides):
    rules = load_rules()
    for card in cards_for(site_id, **overrides).cards[1:]:
        crops = [rules.crop(sl) for se, sl in zip(card.strategy.seasons, card.strategy.slots)
                 if rules.seasons.defs[se].dry]
        if "nitrogen-fixing" in card.why:
            assert any(c.n_fix_kg_ha for c in crops)
        if "lower-water" in card.why:
            assert card.score_breakdown["water"] is not None
            assert all(c.irrigation_mm or c.kind == "fallow" for c in crops)
        if "salt-tolerant" in card.why.split("(")[0]:
            assert all(c.salinity_whole_season_max_dS_m and c.salinity_whole_season_max_dS_m > 3.0
                       for c in crops if c.kind != "fallow")


def test_unsourced_scores_are_null_not_zero():
    cs = cards_for("ctg_anwara", salinity_class="slight_4_8")
    mung = next(c for c in cs.cards if "mungbean" in c.strategy.slots)
    assert mung.score_breakdown["water"] is None and mung.score_breakdown["yield_stability"] is None


def test_class_upper_bound_risk_for_wheat():
    cs = cards_for("ctg_anwara", salinity_class="slight_4_8")
    wheat = next(c for c in cs.cards if "wheat" in c.strategy.slots)
    assert any("reaches 8 dS/m" in r.text and r.review_need == "high" for r in wheat.risks)


def test_every_card_labels_season_per_slot():
    rules = load_rules()
    for card in cards_for("barind_godagari").cards:
        assert len(card.strategy.seasons) == len(card.strategy.slots)
        assert all(se in rules.seasons.defs for se in card.strategy.seasons)


def test_same_crop_can_sit_in_different_seasons():
    rules = load_rules()
    seasons_of_mungbean = {se for p in rules.patterns for se, sl in zip(p.seasons, p.slots) if sl == "mungbean"}
    assert seasons_of_mungbean == {"rabi", "kharif1"}


def test_monsoon_slot_not_salinity_filtered():
    rules = load_rules()
    for p in rules.patterns:
        assert all(se != "kharif2" for se, _ in rules.dry_slots(p))


def test_cli_cards_unknown_site_returns_not_cached(tmp_path):
    out = tmp_path / "nc.json"
    assert main(["cards", "--site", "nowhere", "--date", "2026-11-13", "--out", str(out)]) == 0
    assert json.loads(out.read_text())["status"] == "not_cached"


def test_cli_cards_bad_input_is_a_clear_error(tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text('{"salinity_class": "very_salty"}')
    assert main(["cards", "--site", "ctg_anwara", "--date", "2026-11-13", "--input", str(bad)]) == 2
    assert "invalid input" in capsys.readouterr().err


def test_python_unknown_site_returns_not_cached():
    from rotate_engine import cards_for_site
    assert isinstance(cards_for_site("nowhere", DECISION), NotCached)


def test_priority_dial_alone_changes_cards_at_salinity_site():
    common = {"salinity_class": "slight_4_8"}
    water = cards_for("ctg_anwara", **common, priorities={"water": 0.6, "soil_n": 0.1, "salinity": 0.1,
                                                          "yield_stability": 0.2},
                      constraints={"water_availability": "low"})
    salt = cards_for("ctg_anwara", **common, priorities={"salinity": 0.7, "soil_n": 0.1, "yield_stability": 0.2},
                     constraints={"water_availability": "high"})
    names = lambda cs: {c.strategy.name for c in cs.cards[1:]}
    assert not names(water) & names(salt)


def test_extreme_day_counts_shown_as_observed_evidence():
    labels = lambda cs: [e.label for e in cs.cards[0].evidence if e.unit == "days"]
    barind = cards_for("barind_godagari")
    assert any("35 °C" in l for l in labels(barind)) and any("50 mm" in l for l in labels(barind))
    assert all(e.tag == "Observed" for e in barind.cards[0].evidence if e.unit == "days")
    anwara = cards_for("ctg_anwara")
    assert any("35 °C" in l for l in labels(anwara))
    assert not any("mm of rain" in l for l in labels(anwara))  # Anwara's POWER rain is not shown
    assert any("extreme-day thresholds" in w for w in barind.warnings)
