"""Load and validate rules/rules.json: the cited crop rule table and the cropping-pattern catalogue.

Rotation benefits and risks come only from here, each with its citation; never from NASA data.
"""
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator

from .io import read_json, root

Range = tuple[float, float]
Season = Literal["rabi", "kharif1", "kharif2"]


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Citation(Strict):
    citation_id: str
    ref: str
    url: str
    accessed: str


class CitedValue(Strict):
    citation_id: str
    columns: list[str]
    quote: str


class RuleBenefit(Strict):
    attribute: Literal["water", "soil_n", "salinity", "yield_stability", "income", "forage"]
    text: str
    citation_id: str


class RuleRisk(Strict):
    text: str
    review_need: Literal["high", "medium", "low"]
    citation_id: str | None  # None = a stated information gap, not a claim


class Crop(Strict):
    crop_id: str
    crop: str
    kind: Literal["rice", "cereal", "legume", "oilseed", "fibre", "tuber", "vegetable", "fallow"]
    hazards_fit: list[Literal["salinity", "drought"]]
    salinity_whole_season_max_dS_m: float | None
    salinity_seedling_dS_m: float | None  # display only; never used to filter
    irrigation_mm: Range | None
    n_fix_kg_ha: Range | None
    n_fert_extra_kg_ha: Range | None
    organic_matter: str | None
    pest_break: str | None
    forage: str | None
    income_note: str | None
    infiltration: str | None
    duration_days: Range | None
    varieties: str | None
    evidence_strength: Literal["strong", "weak", "principle-only"]
    benefits: list[RuleBenefit]
    risks: list[RuleRisk]
    citations: list[CitedValue]

    def source_for(self, column: str) -> str | None:
        return next((c.citation_id for c in self.citations if column in c.columns), None)


class Pattern(Strict):
    pattern_id: str
    name: str
    slots: list[str]
    seasons: list[Season]  # one per slot: Rabi, then Kharif-1, then Kharif-2 (nasim2017)
    nca_pct: float | None
    citation_id: str
    quote: str


class SeasonDef(Strict):
    label: str
    months: str
    dry: bool  # dry-season slots get the salinity filter and the water score


class Seasons(Strict):
    citation_id: str
    quote: str
    order_citation_id: str
    order_quote: str
    dry_season_quote: str
    defs: dict[Season, SeasonDef]


class SalinityClasses(Strict):
    citation_id: str
    quote: str
    note: str
    classes: dict[str, tuple[float, float | None]]


VALUE_COLUMNS = ("hazards_fit", "salinity_whole_season_max_dS_m", "salinity_seedling_dS_m",
                 "irrigation_mm", "n_fix_kg_ha", "n_fert_extra_kg_ha", "organic_matter",
                 "pest_break", "forage", "income_note", "infiltration", "duration_days")


class RuleTable(Strict):
    review_status: str
    drafted: str
    drafted_by: str
    citations: list[Citation]
    seasons: Seasons
    salinity_classes: SalinityClasses
    crops: list[Crop]
    patterns: list[Pattern]

    @model_validator(mode="after")
    def _cross_check(self) -> "RuleTable":
        ids = {c.citation_id for c in self.citations}
        crops = {c.crop_id for c in self.crops}
        problems = []
        for crop in self.crops:
            refs = [b.citation_id for b in crop.benefits] + [c.citation_id for c in crop.citations]
            refs += [r.citation_id for r in crop.risks if r.citation_id]
            problems += [f"{crop.crop_id}: unknown citation '{r}'" for r in refs if r not in ids]
            for col in VALUE_COLUMNS:
                value = getattr(crop, col)
                if value not in (None, []) and crop.source_for(col) is None:
                    problems.append(f"{crop.crop_id}: '{col}' has a value but no citation covers it")
        for p in self.patterns:
            problems += [f"{p.pattern_id}: unknown crop '{s}'" for s in p.slots if s not in crops]
            if len(p.seasons) != len(p.slots):
                problems.append(f"{p.pattern_id}: {len(p.slots)} slots but {len(p.seasons)} seasons")
            if p.citation_id not in ids:
                problems.append(f"{p.pattern_id}: unknown citation '{p.citation_id}'")
        if {self.seasons.citation_id, self.seasons.order_citation_id} - ids:
            problems.append("seasons: unknown citation")
        if self.salinity_classes.citation_id not in ids:
            problems.append("salinity_classes: unknown citation")
        if problems:
            raise ValueError("rules.json invalid:\n" + "\n".join(problems))
        return self

    def crop(self, crop_id: str) -> Crop:
        return next(c for c in self.crops if c.crop_id == crop_id)

    def pattern(self, pattern_id: str) -> Pattern:
        return next(p for p in self.patterns if p.pattern_id == pattern_id)

    def citation(self, citation_id: str) -> Citation:
        return next(c for c in self.citations if c.citation_id == citation_id)

    def dry_slots(self, pattern: Pattern) -> list[tuple[Season, "Crop"]]:
        """(season, crop) for the pattern's dry-season slots (Rabi and Kharif-1)."""
        return [(se, self.crop(sl)) for se, sl in zip(pattern.seasons, pattern.slots)
                if self.seasons.defs[se].dry]

    @property
    def reviewed(self) -> bool:
        return self.review_status == "reviewed"


def load_rules() -> RuleTable:
    """Validated rule table; re-read when rules.json changes on disk."""
    return RuleTable.model_validate(read_json(root() / "rules" / "rules.json"))


def is_saline_class(salinity_class: str, table: RuleTable) -> bool:
    """False for 'unknown' and for the non-saline class (upper bound 2 dS/m or less)."""
    bounds = table.salinity_classes.classes.get(salinity_class)
    return bounds is not None and (bounds[1] is None or bounds[1] > 2)


def salinity_fit(crop: Crop, salinity_class: str, table: RuleTable) -> Literal["ok", "unsourced", "exceeds"]:
    """Whole-season tolerance only (seedling figures are never read here).

    Callers apply it to dry-season slots only (RuleTable.dry_slots), when soil salinity builds up.

    'exceeds': the class's lower bound is above the crop's sourced whole-season threshold.
    'unsourced': no whole-season figure; the crop stays in, with a high-review risk.
    """
    if not is_saline_class(salinity_class, table) or crop.kind == "fallow":
        return "ok"
    threshold = crop.salinity_whole_season_max_dS_m
    if threshold is None:
        return "unsourced"
    lower = table.salinity_classes.classes[salinity_class][0]
    return "exceeds" if lower > threshold else "ok"


def water_rel_boro(crop: Crop, table: RuleTable) -> float | None:
    """Midpoint irrigation relative to Boro, only when both figures come from the same source."""
    if crop.kind == "fallow":
        return 0.0  # by definition: no crop, no irrigation
    boro = table.crop("boro")
    if crop.irrigation_mm is None or boro.irrigation_mm is None:
        return None
    if crop.source_for("irrigation_mm") != boro.source_for("irrigation_mm"):
        return None
    return round(sum(crop.irrigation_mm) / sum(boro.irrigation_mm), 3)
