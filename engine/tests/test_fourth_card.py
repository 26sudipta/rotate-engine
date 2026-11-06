"""Step 15.4: an optional 4th card, only on request, never a repeat."""
from datetime import date

import pytest

from rotate_engine import cards_for_site

DATE = date(2026, 11, 13)


def dry(card):
    return [(se, s) for s, se in zip(card.strategy.slots, card.strategy.seasons) if se != "kharif2"]


def test_three_cards_unless_asked():
    assert len(cards_for_site("barind_godagari", DATE).cards) == 3


@pytest.mark.parametrize("site_id, extra", [
    ("barind_godagari", {}),
    ("ctg_anwara", {"salinity_class": "slight_4_8"}),
    ("ctg_anwara", {"salinity_class": "moderate_8_12"}),
    ("barind_godagari", {"mode": "scenario", "shift": {"rain_pct": -50}}),
])
def test_fourth_card_is_new_and_honest(site_id, extra):
    cs = cards_for_site(site_id, DATE, extra_card=True, **extra)
    *first, four = cs.cards
    assert len(cs.cards) == 4 and four.card_id == "alt_3" and not four.is_existing
    assert four.needs_local_review and four.why.startswith("Shown as a fourth option to compare")
    assert four.strategy.slots not in [c.strategy.slots for c in first]
    assert dry(four) not in [dry(c) for c in first]
    assert four.evidence == first[0].evidence  # same tagged evidence, Scenario in a what-if
    assert all(b.citation_id for b in four.benefits)
