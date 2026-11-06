"""Three strategy cards: the current rotation plus two alternatives that differ in kind (a fourth on request).

The selection rule is written in docs/ENGINE.md ("How the three cards are chosen").
"""
from dataclasses import dataclass, field

from .models import AnalogResult, Benefit, Card, Evidence, Request, Risk, Strategy
from .rules import Crop, Pattern, RuleTable, is_saline_class, salinity_fit, water_rel_boro

SOIL_N_FULL_KG_HA = 40.0   # top of the only sourced N-fixation range (emran2022)
SALINITY_FULL_DS_M = 8.0   # upper bound of the SRDI "slight" class
HIGH_SALINITY_DS_M = 8.0   # from here card 3 is "fallow, short oilseed, or local review"
LOW_WATER_PENALTY = 0.5
FIXED_GAPS = ["Field-level salinity is not measured by any NASA product",
              "Local market prices", "Pest pressure", "Equipment needed"]
NO_COLUMN_GAPS = {"yield_stability": "No sourced yield-stability data in the rule table",
                  "income": "No sourced income data in the rule table",
                  "forage": "No sourced forage data in the rule table"}
PRIORITY_WORDS = {"water": "saving irrigation water", "soil_n": "soil nitrogen",
                  "salinity": "salinity resilience", "yield_stability": "yield stability",
                  "income": "income", "forage": "forage"}
REVIEW_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Scored:
    pattern: Pattern
    total: float
    breakdown: dict[str, float]
    gaps: list[str] = field(default_factory=list)
    risks: list[Risk] = field(default_factory=list)


def dry_crops(pattern: Pattern, table: RuleTable) -> list[Crop]:
    """Crops in the pattern's dry-season slots (Rabi and Kharif-1)."""
    return [c for _, c in table.dry_slots(pattern)]


def has_legume(pattern: Pattern, table: RuleTable) -> bool:
    return any(table.crop(s).kind == "legume" for s in pattern.slots)


def class_lower_bound(request: Request, table: RuleTable) -> float:
    bounds = table.salinity_classes.classes.get(request.salinity_class)
    return bounds[0] if bounds else 0.0


def class_upper_bound(request: Request, table: RuleTable) -> float | None:
    bounds = table.salinity_classes.classes.get(request.salinity_class)
    return bounds[1] if bounds else None


def _water_rel(crops: list[Crop], table: RuleTable) -> float | None:
    rels = [water_rel_boro(c, table) for c in crops]
    return None if not crops or None in rels else sum(rels)


def _min_threshold(crops: list[Crop]) -> float | None:
    planted = [c.salinity_whole_season_max_dS_m for c in crops if c.kind != "fallow"]
    return None if not planted or None in planted else min(planted)


def score(pattern: Pattern, request: Request, table: RuleTable) -> Scored:
    """Attribute scores in [0, 1]; None = no sourced value (shown as a gap, counted as 0)."""
    crops = dry_crops(pattern, table)
    weights = request.priorities.model_dump()
    attr: dict[str, float | None] = {}
    gaps, risks = [], []

    water_rel = _water_rel(crops, table)
    attr["water"] = max(0.0, 1 - water_rel) if water_rel is not None else None
    if crops and water_rel is None:
        gaps.append("No sourced irrigation figure for " + ", ".join(
            c.crop for c in crops if water_rel_boro(c, table) is None))

    fixes = [sum(c.n_fix_kg_ha) / 2 for c in crops if c.n_fix_kg_ha]
    attr["soil_n"] = min(1.0, max(fixes) / SOIL_N_FULL_KG_HA) if fixes else None
    legumes_without = [c.crop for c in crops if c.kind == "legume" and not c.n_fix_kg_ha]
    if legumes_without:
        gaps.append("No sourced nitrogen-fixation figure for " + ", ".join(legumes_without))

    planted = [c for c in crops if c.kind != "fallow"]
    threshold = _min_threshold(crops)
    attr["salinity"] = min(1.0, threshold / SALINITY_FULL_DS_M) if threshold is not None else None
    if planted and threshold is None:
        gaps.append("No sourced whole-season salinity tolerance for " + ", ".join(
            c.crop for c in planted if c.salinity_whole_season_max_dS_m is None))
    for name, gap in NO_COLUMN_GAPS.items():
        attr[name] = None
        gaps.append(gap)

    breakdown = {k: (round(weights[k] * v, 4) if v is not None else None) for k, v in attr.items()}
    if request.constraints.water_availability == "low" and water_rel:
        breakdown["constraint_water"] = round(-LOW_WATER_PENALTY * water_rel, 4)
        risks.append(Risk(text="Needs dry-season irrigation, and you reported low water availability.",
                          review_need="high", citation_id=None))

    lower, upper = class_lower_bound(request, table), class_upper_bound(request, table)
    for c in planted:
        t = c.salinity_whole_season_max_dS_m
        cite = c.source_for("salinity_whole_season_max_dS_m")
        fit = salinity_fit(c, request.salinity_class, table)
        if fit == "exceeds":
            risks.append(Risk(text=(f"Your salinity class starts at {lower:g} dS/m, above the whole-season "
                                    f"full-yield value for {c.crop} ({t:g} dS/m)."),
                              review_need="high", citation_id=cite))
        elif (fit == "ok" and t is not None and is_saline_class(request.salinity_class, table)
              and (upper is None or upper > t)):
            reach = f"{upper:g} dS/m" if upper is not None else f"above {lower:g} dS/m"
            risks.append(Risk(text=(f"{c.crop}: sourced whole-season value is {t:g} dS/m; your salinity "
                                    f"class reaches {reach}, so yield may fall in the saltier part of it."),
                              review_need="high", citation_id=cite))
    total = round(sum(v for v in breakdown.values() if v is not None), 4)
    return Scored(pattern, total, breakdown, gaps, risks)


def role(scored: Scored, table: RuleTable) -> str:
    """Card role words, built only from sourced attributes."""
    crops = dry_crops(scored.pattern, table)
    words = []
    water_rel = _water_rel(crops, table)
    if water_rel is not None and water_rel < 1:
        words.append("lower-water")
    threshold = _min_threshold(crops)
    boro = table.crop("boro").salinity_whole_season_max_dS_m
    if threshold is not None and boro is not None and threshold > boro:
        words.append("salt-tolerant")
    if any(c.n_fix_kg_ha for c in crops):
        tail = " with a nitrogen-fixing crop"
    elif any(c.kind == "legume" for c in crops):
        tail = " with a legume crop"
    else:
        tail = "" if words else " without a legume"
    return (", ".join(words) + " option" if words else "option") + tail


def candidates(existing: Pattern, request: Request, table: RuleTable) -> list[Scored]:
    existing_dry = [(se, c.crop_id) for se, c in table.dry_slots(existing)]
    out = []
    for p in table.patterns:
        dry = dry_crops(p, table)
        if p.pattern_id == existing.pattern_id or [(se, c.crop_id) for se, c in table.dry_slots(p)] == existing_dry:
            continue
        if not any(c.kind != "fallow" for c in dry):
            continue
        if any(salinity_fit(c, request.salinity_class, table) == "exceeds" for c in dry):
            continue
        out.append(score(p, request, table))
    return sorted(out, key=lambda s: (-s.total, -(s.pattern.nca_pct or 0), s.pattern.pattern_id))


def _sourced_tolerance_reaches(pattern: Pattern, request: Request, table: RuleTable) -> bool:
    """Every planted dry-season crop has a sourced whole-season value at or above the class's lower edge."""
    planted = [c for c in dry_crops(pattern, table) if c.kind != "fallow"]
    return bool(planted) and all(salinity_fit(c, request.salinity_class, table) == "ok"
                                 and c.salinity_whole_season_max_dS_m is not None for c in planted)


def pick_two(ranked: list[Scored], table: RuleTable) -> list[Scored]:
    legume = next((s for s in ranked if has_legume(s.pattern, table)), None)
    other = next((s for s in ranked if not has_legume(s.pattern, table)), None)
    chosen = [s for s in (legume, other) if s is not None]
    for s in ranked:
        if len(chosen) == 2:
            break
        if s not in chosen:
            chosen.append(s)
    return chosen


def _benefits(pattern: Pattern, table: RuleTable) -> list[Benefit]:
    seen, out = set(), []
    for slot in pattern.slots:
        for b in table.crop(slot).benefits:
            if b.text not in seen:
                seen.add(b.text)
                out.append(Benefit(attribute=b.attribute, text=b.text, citation_id=b.citation_id))
    return out


def _risks(pattern: Pattern, table: RuleTable, extra: list[Risk]) -> list[Risk]:
    seen, out = set(), []
    rule_risks = [Risk(text=r.text, review_need=r.review_need, citation_id=r.citation_id)
                  for s in dict.fromkeys(pattern.slots) for r in table.crop(s).risks]
    for r in extra + rule_risks:
        if r.text not in seen:
            seen.add(r.text)
            out.append(r)
    return sorted(out, key=lambda r: REVIEW_ORDER[r.review_need])


def _top_priority(request: Request) -> str:
    weights = request.priorities.model_dump()
    return max(weights, key=lambda k: (weights[k], k == "water"))


HIGH_SALINITY_BODY = ("your salinity class starts at 8 dS/m or more: the most salt-tolerant sourced Boro "
                      "lines yield up to 8–10 dS/m (Debsharma et al. 2024), and in tidal saline land "
                      "salinity restricts dry-season crops (Nasim et al. 2017). Leaving the dry season "
                      "fallow, a short oilseed, or a local expert's advice are the options to compare.")


def _card(card_id: str, scored: Scored, role_text: str, request: Request, table: RuleTable,
          evidence: list[Evidence], confidence_sentence: str, name: str | None = None) -> Card:
    p = scored.pattern
    if card_id == "existing":
        why = "This is your current rotation, shown for comparison."
        if role_text:  # extra note for the current rotation, e.g. the high-salinity note
            why = f"{why} {role_text}"
    elif role_text.startswith("Shown"):
        why = f"{role_text} {confidence_sentence}"
    elif scored.total <= 0:
        why = (f"Shown as the most widespread {role_text} in the national cropping-pattern survey "
               "(Nasim et al. 2017): no sourced value in the rule table separates the options on "
               f"your priorities. {confidence_sentence}")
    else:
        why = (f"Shown as the {role_text} that scores highest on your priorities "
               f"(top priority: {PRIORITY_WORDS[_top_priority(request)]}). {confidence_sentence}")
    return Card(card_id=card_id, is_existing=card_id == "existing",
                strategy=Strategy(name=name or p.name, slots=list(p.slots), seasons=list(p.seasons)),
                why=why,
                evidence=evidence, benefits=_benefits(p, table),
                gaps=FIXED_GAPS + [g for g in scored.gaps if g not in FIXED_GAPS],
                risks=_risks(p, table, scored.risks), score_breakdown=scored.breakdown,
                needs_local_review=True)


def _dry_key(slots: list[str], seasons: list[str]) -> tuple:
    return tuple((se, s) for s, se in zip(slots, seasons) if se != "kharif2")


def fourth(cards: list[Card], request: Request, table: RuleTable, evidence: list[Evidence],
           sentence: str) -> Card | None:
    """The next-ranked candidate not shown, preferring dry-season crops no card has yet."""
    shown_slots = [c.strategy.slots for c in cards]
    shown_dry = {_dry_key(c.strategy.slots, c.strategy.seasons) for c in cards}
    rest = [s for s in candidates(table.pattern(request.current_rotation), request, table)
            if list(s.pattern.slots) not in shown_slots]
    pick = next((s for s in rest if _dry_key(list(s.pattern.slots), list(s.pattern.seasons)) not in shown_dry),
                rest[0] if rest else None)
    if pick is None:
        return None
    why = (f"Shown as a fourth option to compare: the {role(pick, table)} ranked next on your priorities "
           "(ties broken by national area share).")
    return _card(f"alt_{len(cards)}", pick, why, request, table, evidence, sentence)


def build_cards_for(request: Request, table: RuleTable, analogs: AnalogResult,
                    evidence: list[Evidence]) -> list[Card]:
    """Three cards, plus an optional fourth when the request asks for it."""
    cards = build_three(request, table, analogs, evidence)
    extra = request.extra_card and fourth(cards, request, table, evidence,
                                          analogs.confidence.sentence if analogs.confidence else "")
    return cards + [extra] if extra else cards


def build_three(request: Request, table: RuleTable, analogs: AnalogResult,
                evidence: list[Evidence]) -> list[Card]:
    existing = table.pattern(request.current_rotation)
    sentence = analogs.confidence.sentence if analogs.confidence else ""
    ranked = candidates(existing, request, table)
    high_salinity = class_lower_bound(request, table) >= HIGH_SALINITY_DS_M
    fallow = table.pattern("fallow-fallow-t_aman")
    # already fallow in the dry season: the high-salinity note goes on card 1, not a repeat card 3
    already_fallow = high_salinity and existing.pattern_id == fallow.pattern_id
    note = f"Note: {HIGH_SALINITY_BODY}" if already_fallow else ""
    cards = [_card("existing", score(existing, request, table), note, request, table, evidence, sentence)]
    if high_salinity:
        lower = class_lower_bound(request, table)
        tolerant = next((s for s in ranked if _sourced_tolerance_reaches(s.pattern, request, table)), None)
        first = tolerant or next((s for s in ranked if has_legume(s.pattern, table)), None) \
            or (ranked[0] if ranked else None)
        if first is not None:
            why = (f"Shown because it is the option whose sourced whole-season salt tolerance "
                   f"({_min_threshold(dry_crops(first.pattern, table)):g} dS/m) reaches the lower edge "
                   f"of your salinity class ({lower:g} dS/m).") if first is tolerant else role(first, table)
            cards.append(_card("alt_1", first, why, request, table, evidence, sentence))
        if not already_fallow:
            cards.append(_card(f"alt_{len(cards)}", score(fallow, request, table),
                               f"Shown because {HIGH_SALINITY_BODY}", request, table, evidence, sentence,
                               name="Fallow, short oilseed, or local review"))
            return cards
        # already fallow: the last card is the top remaining option of the other kind
        rest = [s for s in ranked if s is not first]
        other = next((s for s in rest if has_legume(s.pattern, table) != has_legume(first.pattern, table)),
                     rest[0] if rest else None)
        if other is not None:
            cards.append(_card("alt_2", other, role(other, table), request, table, evidence, sentence))
        return cards
    for i, s in enumerate(pick_two(ranked, table)):
        cards.append(_card(f"alt_{i + 1}", s, role(s, table), request, table, evidence, sentence))
    return cards
