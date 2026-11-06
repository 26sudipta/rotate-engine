"""The JSON contract v1.0. Field names follow the report's "Data contract (JSON), version 1.0".

Adding an optional field -> 1.1. Renaming or removing a field -> 2.0 (announce it).
"""
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Tag = Literal["Observed", "Derived", "Scenario"]
SchemaVersion = Literal["1.0"]
SalinityClass = Literal["non_saline_lt2", "very_slight_2_4", "slight_4_8",
                        "moderate_8_12", "strong_12_16", "very_strong_gt16", "unknown"]
Hazard = Literal["salinity", "drought"]


class Strict(BaseModel):
    # forbid typos; defaults (schema_version) still count as required in the serialization schema
    model_config = ConfigDict(extra="forbid", json_schema_serialization_defaults_required=True)


# ---- request and site -------------------------------------------------------------------------

class Priorities(Strict):
    water: float = Field(0.0, ge=0, le=1)
    soil_n: float = Field(0.0, ge=0, le=1)
    salinity: float = Field(0.0, ge=0, le=1)
    yield_stability: float = Field(0.0, ge=0, le=1)
    income: float = Field(0.0, ge=0, le=1)
    forage: float = Field(0.0, ge=0, le=1)


class Constraints(Strict):
    water_availability: Literal["low", "medium", "high"] = "medium"
    equipment: str = "none"
    market: str = "local"


class Shift(Strict):
    """What-if change to this season's 60-day window weather (raw daily values, then re-matched)."""
    rain_pct: float = Field(0.0, ge=-100, le=200)  # each day's rain × (1 + rain_pct/100)
    temp_c: float = Field(0.0, ge=-5, le=5)  # added to daily Tmin and Tmax
    rh_points: float = Field(0.0, ge=-30, le=30)  # added to daily RH, kept within 0–100


class Request(Strict):
    site_id: str
    decision_date: date
    season: Literal["boro"] = "boro"
    mode: Literal["season_to_date", "scenario"] = "season_to_date"
    current_rotation: str
    hazard: Hazard
    salinity_class: SalinityClass = "unknown"
    priorities: Priorities = Priorities()
    constraints: Constraints = Constraints()
    shift: Shift | None = None  # what-if slider; scenario mode only
    tercile: Literal["dry", "normal", "wet"] | None = None  # past seasons whose later rain fell in this third
    extra_card: bool = False  # True asks for a 4th card (stretch)

    @model_validator(mode="after")
    def _scenario_matches_mode(self) -> "Request":
        if (self.mode == "scenario") != (self.shift is not None or self.tercile is not None):
            raise ValueError("mode 'scenario' needs a 'shift' or a 'tercile', and either needs mode 'scenario'")
        return self


class Site(Strict):
    id: str
    name: str
    lat: float
    lon: float
    hazard: Hazard


class Window(Strict):
    start: date
    end: date
    days_available: int


# ---- analogs and confidence -------------------------------------------------------------------

class AnalogFeatures(Strict):
    rain_mm: float | None  # None where the site's POWER rain is unusable
    tmin_c: float
    rh_pct: float


class WeatherAnalog(Strict):
    year: int  # Boro harvest year
    rank: int
    distance: float
    weight: float
    close_match: bool
    features: AnalogFeatures


class NdviAnalog(Strict):
    year: int
    rank: int
    distance: float
    weight: float
    ndvi_anomaly: float | None
    ndvi_status: Literal["ok", "flagged", "missing"]


class Analogs(Strict):
    method: Literal["ledoit_wolf", "euclidean"]
    weather_pool: list[WeatherAnalog]
    ndvi_pool: list[NdviAnalog]
    euclid_overlap: str
    shrinkage: float | None


class Confidence(Strict):
    k: int
    agree_count: int
    direction: Literal["below_normal", "above_normal"]
    weighted_agreement: float
    chance_rate: float
    label: Literal["high", "moderate", "split"]
    sentence: str
    basis: Literal["ndvi", "rainfall"]
    tag: Literal["Derived", "Scenario"] = "Derived"  # Scenario for what-if output


# ---- cards ------------------------------------------------------------------------------------

class Strategy(Strict):
    name: str
    slots: list[str]  # crop ids, in season order
    seasons: list[Literal["rabi", "kharif1", "kharif2"]]  # one per slot


class Evidence(Strict):
    label: str
    value: str
    unit: str | None
    source: str
    tag: Tag
    analog_year: int | None


class Benefit(Strict):
    attribute: str
    text: str
    citation_id: str  # rule-table citation, never a NASA tag


class Risk(Strict):
    text: str
    review_need: Literal["high", "medium", "low"]
    citation_id: str | None  # rule-table citation; None for a stated information gap


class Card(Strict):
    card_id: str
    is_existing: bool
    strategy: Strategy
    why: str
    evidence: list[Evidence]
    benefits: list[Benefit]
    gaps: list[str]
    risks: list[Risk]
    score_breakdown: dict[str, float | None]  # None = no sourced value (counted as 0)
    needs_local_review: Literal[True] = True


# ---- provenance -------------------------------------------------------------------------------

class PowerProvenance(Strict):
    endpoint: str
    parameters: list[str]
    community: str
    accessed: date
    api_version: str
    header_sources: list[str]
    fill_value: float


class NdviProvenance(Strict):
    product: str
    layers: list[str]
    route: Literal["appeears", "ornl"]
    task_id: str | None
    accessed: date
    sha256: str | None


class Provenance(Strict):
    power: PowerProvenance
    ndvi: NdviProvenance | None


# ---- responses --------------------------------------------------------------------------------

class CardSet(Strict):
    schema_version: SchemaVersion = "1.0"
    engine_version: str
    generated_at: datetime
    request: Request
    site: Site
    window: Window
    analogs: Analogs
    confidence: Confidence
    cards: list[Card] = Field(min_length=3, max_length=4)  # 4 only when request.extra_card
    ndvi_status: Literal["ok", "partial", "pending"]
    warnings: list[str]
    provenance: Provenance
    disclaimer: str


class AnalogResult(Strict):
    schema_version: SchemaVersion = "1.0"
    engine_version: str
    generated_at: datetime
    site: Site
    decision_date: date
    season_year: int  # Boro harvest year of the decision
    window: Window
    analogs: Analogs
    confidence: Confidence | None  # None until confidence.py is wired in (Step 8)
    ndvi_status: Literal["ok", "partial", "pending"]
    warnings: list[str]
    provenance: Provenance
    disclaimer: str


class NotCached(Strict):
    schema_version: SchemaVersion = "1.0"
    status: Literal["not_cached"] = "not_cached"
    site_id: str
    message: str


class NdviPoint(Strict):
    date: date  # actual acquisition day
    ndvi: float  # raw, always drawn
    ndvi_smooth: float | None  # Savitzky-Golay line; None where the gap-free run is too short
    reliability: int  # MODIS pixel reliability; HLS: 0 clear, 1 high aerosol
    flagged: bool  # reliability 1, or MODIS composites from 2025 onward
    # aqua (MYD13Q1 via ORNL) only when asked for; hls_s30 / hls_l30 only in the separate 30 m HLS curve
    satellite: Literal["terra", "aqua", "hls_s30", "hls_l30"] = "terra"


class NdviWindow(Strict):
    date: date  # composite start date
    mean: float  # of the QA-passed pixels in the 3x3 (about 700 m) around the point
    min: float
    max: float
    n_ok: int  # how many of the 9 pixels passed QA


class DateSpan(Strict):
    start: date
    end: date
    label: str


class NdviSeries(Strict):
    schema_version: SchemaVersion = "1.0"
    site_id: str
    product: str
    status: Literal["ok", "pending"]
    points: list[NdviPoint]
    gaps: list[DateSpan]
    low_veg_windows: list[DateSpan]
    qa_pass_share_by_month: dict[str, float]  # Terra composites; HLS acquisitions in the HLS curve
    window_3x3: list[NdviWindow] = []  # filled only when asked for, from Nov 2023 on
    tag: Literal["Observed"] = "Observed"


class NdviYear(Strict):
    year: int  # Boro harvest year
    start: date
    end: date
    status: Literal["ok", "flagged", "missing"]  # flagged = season reaches into 2025 or later
    points: list[NdviPoint]
    gaps: list[DateSpan]
    low_veg_windows: list[DateSpan]


class NdviYears(Strict):
    schema_version: SchemaVersion = "1.0"
    site_id: str
    product: str
    status: Literal["ok", "pending"]
    years: list[NdviYear]
    tag: Literal["Observed"] = "Observed"


class CalibrationBin(Strict):
    agree_count: int
    n: int
    hit_rate: float | None


class BacktestYear(Strict):
    year: int  # Boro harvest year held out
    ndvi_anomaly: float  # its peak-window NDVI minus the training-year trend
    predicted: float  # kernel-weighted mean of its analogs' anomalies; climatology predicts 0
    analog_years: list[int]
    agree_count: int
    beat_clim: bool


class BacktestResult(Strict):
    schema_version: SchemaVersion = "1.0"
    site_id: str
    season: Literal["boro"] = "boro"
    decision_date: date  # its calendar window is matched in every year
    years_tested: list[int]
    k: int
    predictand: str
    ss_mse: float
    mse_analog: float
    mse_clim: float
    ss_mse_euclid: float
    anomaly_corr: float | None
    tercile_hit_rate: float | None
    beat_clim_count: int
    sign_test_p: float
    permutation_p: float
    n_permutations: int
    calibration_bins: list[CalibrationBin]
    verdict_text: str
    excluded_years: list[int]
    years: list[BacktestYear]  # one row per tested year
    flagged_years: list[BacktestYear]  # 2025 onward, reported separately, never scored
    tag: Literal["Derived"] = "Derived"


EXPORTED = {"card_set": CardSet, "analog_result": AnalogResult, "ndvi_series": NdviSeries,
            "ndvi_years": NdviYears, "backtest_result": BacktestResult, "not_cached": NotCached}


def json_schemas() -> dict[str, dict]:
    return {name: model.model_json_schema(mode="serialization") for name, model in EXPORTED.items()}
