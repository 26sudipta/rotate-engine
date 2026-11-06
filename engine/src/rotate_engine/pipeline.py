"""Public engine functions: cached site -> pydantic result. Reads files only."""
from datetime import date, datetime
from functools import lru_cache

import pandas as pd

from . import analogs as core
from . import backtest, ndvi
from .config import (DISCLAIMER, ENGINE_VERSION, FEATURES, HEAVY_RAIN_MM, HOT_DAY_TMAX_C, K, SOIL,
                     NDVI_DEFAULT_PEAK_DOY, NDVI_FLAG_FROM_YEAR, NDVI_SEASON_END, NDVI_SEASON_START,
                     NDVI_YEARS, POOL_FIRST_SEASON, TERCILE_SEASON_END)
from .confidence import confidence
from .features import feature_table, in_season_rain, shifted, terciles
from .io import (NotCachedError, get_site, load_hls, load_imerg, load_ndvi_raw, load_ornl, load_power,
                 load_sites, root)
from .cards import build_cards_for
from .models import (AnalogFeatures, AnalogResult, Analogs, BacktestResult, CardSet, Confidence, DateSpan, Evidence,
                     NdviAnalog, NdviPoint, NdviSeries, NdviWindow, NdviYear, NdviYears, NotCached, Priorities,
                     Request, Shift, Site,
                     WeatherAnalog, Window)
from .provenance import power_source_label, power_warnings, provenance
from .rules import load_rules
from .seasons import InsufficientWindowError, current_window, past_windows


def list_sites() -> list[Site]:
    return [Site(**{k: s[k] for k in Site.model_fields}) for s in load_sites()]


def season_features(site_id: str, decision_date: date, shift: Shift | None = None):
    """(current window, feature table incl. the current season, skipped seasons, warnings).

    A what-if `shift` changes only the current window's daily weather; past seasons stay observed.
    """
    power = load_power(site_id)
    window, warnings = current_window(power, decision_date)
    if shift is not None:
        power = shifted(power, window, shift.rain_pct, shift.temp_c, shift.rh_points)
    windows = past_windows(window, power.index[0].date()) + [window]
    table, skipped = feature_table(power, windows)
    return window, table, skipped, warnings


def training_seasons(table: pd.DataFrame, target: int) -> list[int]:
    """Comparable past seasons: from POOL_FIRST_SEASON up to, never including, the target."""
    return [int(y) for y in table.index if POOL_FIRST_SEASON <= y < target]


def match_features(site: dict) -> tuple[str, ...]:
    return tuple(site.get("match_features", FEATURES))


def _weather_pool(table: pd.DataFrame, result: core.MatchResult,
                  show_rain: bool) -> list[WeatherAnalog]:
    return [WeatherAnalog(year=m.year, rank=m.rank, distance=round(m.distance, 4),
                          weight=round(m.weight, 4), close_match=m.close_match,
                          features=AnalogFeatures(rain_mm=round(table.at[m.year, "rain_mm"], 1) if show_rain else None,
                                                  tmin_c=round(table.at[m.year, "tmin_c"], 2),
                                                  rh_pct=round(table.at[m.year, "rh_pct"], 1)))
            for m in result.matches]


def site_peak_ndvi(site: dict) -> pd.Series | None:
    """Per-harvest-year peak-window NDVI for the site, or None while NDVI is pending."""
    try:
        raw = load_ndvi_raw()
    except NotCachedError:
        return None
    points = ndvi.clean_points(raw, site.get("ndvi_id", site["id"]))
    return ndvi.peak_values(points, tuple(site.get("ndvi_peak_doy", NDVI_DEFAULT_PEAK_DOY)))


def ndvi_years(table: pd.DataFrame, target: int, peaks: pd.Series) -> list[int]:
    """Training seasons in NDVI_YEARS that have both window features and a peak NDVI value."""
    return [y for y in training_seasons(table, target)
            if NDVI_YEARS[0] <= y <= NDVI_YEARS[1] and y in peaks.index]


def ndvi_pool(table: pd.DataFrame, target: int, peaks: pd.Series, features: tuple[str, ...],
              k: int, eligible: set[int] | None = None) -> tuple[list[NdviAnalog], core.MatchResult]:
    """k nearest among the NDVI years (only `eligible` ones may be picked)."""
    years = ndvi_years(table, target, peaks)
    result = core.find_analogs(table, target, years, k, features=features, eligible=eligible)
    anom = ndvi.anomalies(peaks, years)
    pool = [NdviAnalog(year=m.year, rank=m.rank, distance=round(m.distance, 4),
                       weight=round(m.weight, 4), ndvi_anomaly=round(float(anom[m.year]), 4),
                       ndvi_status="ok") for m in result.matches]
    return pool, result


def ndvi_confidence(site: dict, pool: list[NdviAnalog]) -> Confidence:
    subject = (f"{site.get('ndvi_peak_label', 'Boro peak')} greenness in the area around this "
               "field (250 m)")
    return confidence([a.ndvi_anomaly for a in pool], [a.weight for a in pool], subject)


def _input_stamp(site_id: str) -> tuple[int, ...]:
    """mtimes of every data file a site's backtest reads, so the cache refreshes after a refetch."""
    data = root() / "data"
    paths = [data / "sites.json", data / "power" / f"{site_id}.csv",
             data / "raw" / "power" / f"{site_id}.json",
             *sorted((data / "ndvi").glob("*-MOD13Q1-061-results.csv"))]
    return tuple(p.stat().st_mtime_ns for p in paths if p.exists())


def _compute_backtest(site_id: str, decision_date: date, k: int) -> BacktestResult | NotCached:
    try:
        site = get_site(site_id)
        window, table, _, _ = season_features(site_id, decision_date)
    except NotCachedError as exc:
        return NotCached(site_id=site_id, message=str(exc))
    peaks = site_peak_ndvi(site)
    if peaks is None:
        return NotCached(site_id=site_id, message="NDVI pending: the backtest needs the NDVI files in data/ndvi/")
    table = table[table.index < window.season_year]  # the decision season never tests the method
    features = match_features(site)
    tested, excluded, folds, flagged = backtest.evaluate(table, peaks, features, k)
    if len(tested) < k + 2:
        return NotCached(site_id=site_id, message=f"only {len(tested)} NDVI years to test; need {k + 2}")
    doy = tuple(site.get("ndvi_peak_doy", NDVI_DEFAULT_PEAK_DOY))
    return backtest.result(site_id, decision_date, doy, tested, excluded, folds, flagged, k)


@lru_cache(maxsize=16)
def _cached_backtest(site_id: str, decision_date: date, k: int, stamp: tuple[int, ...]):
    return _compute_backtest(site_id, decision_date, k)


def run_backtest(site_id: str, decision_date: date, k: int = K) -> BacktestResult | NotCached:
    """LOYO backtest for a cached site at the decision date's calendar window (cached per data state)."""
    return _cached_backtest(site_id, decision_date, k, _input_stamp(site_id)).model_copy(deep=True)


def describe_shift(shift: Shift) -> str:
    parts = [f"rain {shift.rain_pct:+g}%" if shift.rain_pct else "",
             f"temperature {shift.temp_c:+g} °C" if shift.temp_c else "",
             f"humidity {shift.rh_points:+g} points" if shift.rh_points else ""]
    return ", ".join(p for p in parts if p) or "no change"


def scenario_label(shift: Shift | None, tercile: str | None) -> str:
    parts = ([describe_shift(shift)] if shift else []) + ([f"{tercile} season"] if tercile else [])
    return "; ".join(parts)


TERCILE_WORDS = {"dry": "driest third", "normal": "middle third", "wet": "wettest third"}


def tercile_years(site_id: str, decision_date: date, target: int, train: list[int],
                  tercile: str) -> tuple[set[int], str]:
    """Training seasons whose rain after the decision day fell in `tercile`, and the warning text."""
    totals = in_season_rain(load_imerg(site_id), decision_date, target, train)
    if len(totals) < 3:
        raise InsufficientWindowError(f"only {len(totals)} past seasons have complete IMERG rain after "
                                      f"{decision_date:%d %b}; the tercile scenario needs at least 3")
    labels, (lo, hi) = terciles(totals)
    edge = {"dry": f"{lo:.0f} mm or less", "normal": f"{lo:.0f}–{hi:.0f} mm", "wet": f"more than {hi:.0f} mm"}
    end = date(2000, *TERCILE_SEASON_END)
    text = (f"Tercile scenario ({tercile} season): look-alike years are limited to past seasons whose rain "
            f"after {decision_date:%d %b} up to {end:%d %b} fell in the {TERCILE_WORDS[tercile]} of Boro seasons "
            f"{totals.index.min()}–{totals.index.max()} ({edge[tercile]}; GPM IMERG as served by NASA POWER). "
            "It shows past seasons that turned out this way. It is not a forecast that this season will.")
    return set(labels[labels == tercile].index), text


def find_analogs(site_id: str, decision_date: date, k: int = K, shift: Shift | None = None,
                 tercile: str | None = None) -> AnalogResult | NotCached:
    """Look-alike years for the decision date. A `shift` (what-if weather) or a `tercile` (past
    seasons whose later rain fell in that third) makes it a scenario, tagged Scenario."""
    try:
        site = get_site(site_id)
        window, table, skipped, warnings = season_features(site_id, decision_date, shift)
    except NotCachedError as exc:
        return NotCached(site_id=site_id, message=str(exc))
    target = window.season_year
    train = training_seasons(table, target)
    if len(train) < k:
        raise InsufficientWindowError(
            f"only {len(train)} comparable past seasons before Boro {target} (from {POOL_FIRST_SEASON}); "
            f"need at least {k}")
    features = match_features(site)
    eligible = None
    if tercile is not None:
        try:
            eligible, tercile_text = tercile_years(site_id, decision_date, target, train, tercile)
        except NotCachedError as exc:
            return NotCached(site_id=site_id, message=str(exc))
        if len(eligible) < k:
            raise InsufficientWindowError(f"only {len(eligible)} past seasons in the {tercile} third; need {k}")
    result = core.find_analogs(table, target, train, k, features=features, eligible=eligible)
    prov = provenance(site_id)
    warnings = warnings + list(result.warnings) + power_warnings(prov.power)
    warnings.append(f"Look-alike years are drawn from Boro seasons {POOL_FIRST_SEASON}-{target - 1} only: "
                    "POWER humidity, temperature and rain series shift in 1997, so earlier years are "
                    "not comparable.")
    show_rain = "rain_log1p" in features
    if not show_rain:
        warnings.append("Rainfall is not used for matching at this site: POWER's rain series here "
                        "has an unrealistic jump from 2015, so matching uses temperature and "
                        "humidity only. POWER's soil wetness here follows the same jump, so it is "
                        "not shown either.")
    if skipped:
        warnings.append(f"Seasons skipped for too few valid days: {skipped}")
    peaks = site_peak_ndvi(site)
    pool, conf, ndvi_status = [], None, "pending"
    if peaks is not None and len(ndvi_years(table, target, peaks)) < k:
        peaks = None  # no NDVI for this site, or too few NDVI years before this date
    if peaks is not None:
        if eligible is not None and len(eligible & set(ndvi_years(table, target, peaks))) < k:
            raise InsufficientWindowError(f"fewer than {k} NDVI years in the {tercile} third")
        pool, ndvi_result = ndvi_pool(table, target, peaks, features, k, eligible)
        conf, ndvi_status = ndvi_confidence(site, pool), "ok"
        warnings += [w for w in ndvi_result.warnings if w not in warnings]
        if site.get("ndvi_peak_note"):
            warnings.append(f"NDVI peak window for this site needs local review: {site['ndvi_peak_note']}")
        bt = run_backtest(site_id, decision_date, k)
        warnings.append(f"Backtest: {bt.verdict_text}" if isinstance(bt, BacktestResult) else
                        f"The look-alike method could not be backtested for this date: {bt.message}")
    if peaks is None:
        warnings.append("NDVI pending: no greenness data for this site and date yet, so confidence "
                        "is not available.")
    if tercile is not None:
        warnings.insert(0, tercile_text)
    if shift is not None:
        warnings.insert(0, f"What-if scenario ({describe_shift(shift)}): this season's 60-day window "
                        "weather was changed by hand before matching. It is not observed data and not a forecast.")
        if shift.rain_pct and not show_rain:
            warnings.append("The rain change has no effect here: rain is not used for matching at this site.")
        if show_rain:
            warnings.append("Soil wetness is not shown in a what-if: the model value can't be changed "
                            "consistently by hand.")
    if (shift is not None or tercile is not None) and conf is not None:
        label = scenario_label(shift, tercile)
        conf = conf.model_copy(update={"tag": "Scenario", "sentence": f"What-if ({label}): {conf.sentence}"})
    return AnalogResult(
        engine_version=ENGINE_VERSION, generated_at=datetime.now().astimezone(),
        site=Site(**{f: site[f] for f in Site.model_fields}), decision_date=decision_date,
        season_year=target,
        window=Window(start=window.start, end=window.end,
                      days_available=int(table.at[target, "days_available"])),
        analogs=Analogs(method=result.method, weather_pool=_weather_pool(table, result, show_rain),
                        ndvi_pool=pool,
                        euclid_overlap=core.euclid_overlap(table, target, train, result, k, features, eligible),
                        shrinkage=result.shrinkage),
        confidence=conf, ndvi_status=ndvi_status, warnings=warnings,
        provenance=prov, disclaimer=DISCLAIMER)


DEFAULT_PRIORITIES = Priorities(water=0.25, soil_n=0.25, salinity=0.25, yield_stability=0.25)
MATCHING_SOURCE = "ROTATE analog matching on NASA POWER window weather (Ledoit-Wolf Mahalanobis distance)"
NDVI_SOURCE = ("NASA MODIS MOD13Q1.061 NDVI via AppEEARS, vegetation in the area around this field "
               "(250 m); anomaly from ROTATE's trend fit")
BACKTEST_SOURCE = ("ROTATE leave-one-year-out backtest of the NDVI look-alike years against the plain "
                   "average, rule fixed before the first run (docs/ENGINE.md)")


def default_request(site_id: str, decision_date: date, **overrides) -> Request:
    site = get_site(site_id)
    fields = {"site_id": site_id, "decision_date": decision_date, "hazard": site["hazard"],
              "current_rotation": "boro-fallow-t_aman", "priorities": DEFAULT_PRIORITIES}
    return Request(**{**fields, **overrides})


def _evidence(site: dict, res: AnalogResult, table: pd.DataFrame) -> list[Evidence]:
    power = res.provenance.power
    past = table.loc[training_seasons(table, res.season_year)]
    span = f"{past.index.min()}–{past.index.max()}"
    now = table.loc[res.season_year]
    rows = [("tmin_c", "T2M_MIN", "Mean minimum temperature in the 60 days before the decision", "°C", 1, 1),
            ("rh_pct", "RH2M", "Mean relative humidity in the 60 days before the decision", "%", 0, 0),
            ("hot_days", "T2M_MAX", f"Days with a maximum temperature of {HOT_DAY_TMAX_C:g} °C or more "
             "in the 60 days before the decision", "days", 0, 1)]
    if "rain_log1p" in match_features(site):  # soil wetness is driven by the same rain, so same gate
        rows[:0] = [("rain_mm", "PRECTOTCORR", "Rainfall in the 60 days before the decision", "mm", 0, 0),
                    ("heavy_rain_days", "PRECTOTCORR", f"Days with {HEAVY_RAIN_MM:g} mm of rain or more "
                     "in the 60 days before the decision", "days", 0, 1),
                    ("soil_wetness", SOIL, "Mean root-zone soil wetness in the 60 days before the decision "
                     "(model output; 0 = dry, 1 = saturated)", "fraction", 2, 2)]
    # display evidence only: extreme-day counts and soil wetness never enter the matching
    out = [Evidence(label=label, value=f"{now[col]:.{nd}f} (Boro seasons {span} averaged {past[col].mean():.{nd_mean}f})",
                    unit=unit, source=power_source_label(power, param), tag="Observed", analog_year=None)
           for col, param, label, unit, nd, nd_mean in rows if pd.notna(now[col])]
    years = ", ".join(str(a.year) for a in res.analogs.weather_pool)
    out.append(Evidence(label="Look-alike years (weather), closest first", value=years, unit=None,
                        source=MATCHING_SOURCE, tag="Derived", analog_year=None))
    for a in res.analogs.ndvi_pool:
        out.append(Evidence(label=f"Greenness anomaly in look-alike year {a.year}",
                            value=f"{a.ndvi_anomaly:+.3f}", unit="NDVI", source=NDVI_SOURCE,
                            tag="Derived", analog_year=a.year))
    if res.confidence:
        out.append(Evidence(label="Agreement among look-alike years", value=res.confidence.sentence,
                            unit=None, source=MATCHING_SOURCE + "; " + NDVI_SOURCE, tag="Derived",
                            analog_year=None))
    bt = run_backtest(res.site.id, res.decision_date)
    if isinstance(bt, BacktestResult):
        out.append(Evidence(label="How the look-alike method did on past seasons", value=bt.verdict_text,
                            unit=None, source=BACKTEST_SOURCE, tag="Derived", analog_year=None))
    return out


def build_cards(request: Request) -> CardSet | NotCached:
    rules = load_rules()
    known = [p.pattern_id for p in rules.patterns]
    if request.current_rotation not in known:
        raise ValueError(f"unknown current_rotation '{request.current_rotation}'; "
                         f"use a pattern_id from rules/rules.json, e.g. {known[0]}")
    res = find_analogs(request.site_id, request.decision_date, shift=request.shift, tercile=request.tercile)
    if isinstance(res, NotCached):
        return res
    if res.confidence is None:
        return NotCached(site_id=request.site_id,
                         message="NDVI pending: cards need the NDVI files in data/ndvi/")
    site = get_site(request.site_id)
    _, table, _, _ = season_features(request.site_id, request.decision_date, request.shift)
    evidence = _evidence(site, res, table)
    if request.mode == "scenario":  # what-if output carries only Scenario tags
        change = f"What-if ({scenario_label(request.shift, request.tercile)}); based on: "
        evidence = [e.model_copy(update={"tag": "Scenario", "label": f"What-if: {e.label}",
                                         "source": change + e.source}) for e in evidence]
    cards = build_cards_for(request, rules, res, evidence)
    warnings = list(res.warnings)
    warnings.append(f"The extreme-day thresholds ({HOT_DAY_TMAX_C:g} °C, {HEAVY_RAIN_MM:g} mm) are working "
                    "values, not yet confirmed by the team's science translator.")
    if not rules.reviewed:
        warnings.append("The crop rule table is an unreviewed draft (drafted with AI assistance from "
                        "cited sources) and has not yet been checked by the team's science translator.")
    return CardSet(engine_version=ENGINE_VERSION, generated_at=datetime.now().astimezone(),
                   request=request, site=res.site, window=res.window, analogs=res.analogs,
                   confidence=res.confidence, cards=cards, ndvi_status=res.ndvi_status,
                   warnings=warnings, provenance=res.provenance, disclaimer=DISCLAIMER)


def cards_for_site(site_id: str, decision_date: date, **choices) -> CardSet | NotCached:
    """Cards for a site and the farmer's choices; an unknown site gives NotCached, not an error."""
    try:
        request = default_request(site_id, decision_date, **choices)
    except NotCachedError as exc:
        return NotCached(site_id=site_id, message=str(exc))
    return build_cards(request)


NDVI_PRODUCT = "MOD13Q1.061"


def _between(points: pd.DataFrame, start: date | None, end: date | None) -> pd.DataFrame:
    if start:
        points = points[points["date"] >= pd.Timestamp(start)]
    if end:
        points = points[points["date"] <= pd.Timestamp(end)]
    return points


def _curve(points: pd.DataFrame) -> dict:
    """points, gaps and low_veg_windows for NdviSeries / NdviYear."""
    span = lambda t: DateSpan(start=t[0], end=t[1], label=t[2])
    return {"points": [NdviPoint(date=d.date(), ndvi=round(float(v), 4),
                                 ndvi_smooth=None if pd.isna(s) else round(float(s), 4),
                                 reliability=int(r), flagged=bool(f), satellite=sat)
                       for d, v, s, r, f, sat in zip(points["date"], points["ndvi"], points["smooth"],
                                                     points["reliability"], ndvi.flagged(points),
                                                     points["satellite"])],
            "gaps": [span(t) for t in ndvi.gap_spans(points)],
            "low_veg_windows": [span(t) for t in ndvi.low_veg_spans(points)]}


def _product(aqua: bool) -> str:
    return NDVI_PRODUCT + (" + MYD13Q1.061 (Aqua, via ORNL)" if aqua else "")


def _site_ndvi(site_id: str, aqua: bool = False):
    """(ndvi_id, raw AppEEARS table, smoothed points) or None while NDVI is pending.

    With `aqua`, Aqua (MYD13Q1) points are interleaved for display; the predictand stays Terra-only.
    Smoothing runs on the whole record before any date slicing, so edges match across views.
    Raises NotCachedError for an unknown site or a missing Aqua file.
    """
    site = get_site(site_id)
    try:
        raw = load_ndvi_raw()
    except NotCachedError:
        return None
    ndvi_id = site.get("ndvi_id", site["id"])
    points = ndvi.clean_points(raw, ndvi_id).assign(satellite="terra")
    if aqua:
        extra = ndvi.ornl_points(load_ornl(site_id, "MYD13Q1", 0)).assign(satellite="aqua")
        points = pd.concat([points, extra]).sort_values(["date", "satellite"]).reset_index(drop=True)
    return ndvi_id, raw, ndvi.with_smooth(points)


def _windows(site_id: str, start: date | None, end: date | None) -> list[NdviWindow]:
    w = _between(ndvi.window_stats(load_ornl(site_id, "MOD13Q1", 1)), start, end)
    return [NdviWindow(date=d.date(), mean=round(float(m), 4), min=round(float(lo), 4),
                       max=round(float(hi), 4), n_ok=int(n))
            for d, m, lo, hi, n in zip(w["date"], w["mean"], w["min"], w["max"], w["n_ok"])]


HLS_PRODUCT = "HLS v2.0 NDVI (HLSS30_VI.020 + HLSL30_VI.020, 30 m pixel, Fmask-filtered, via AppEEARS)"


def _hls_series(site_id: str, start: date | None, end: date | None) -> NdviSeries | NotCached:
    """The 30 m HLS curve: its own points, smoothing, gaps and low-vegetation windows, never mixed with MODIS."""
    try:
        site = get_site(site_id)
        merged = pd.concat([ndvi.hls_merged(load_hls(f"{s}-VI-020"), load_hls(f"{s}-020"), s)
                            for s in ndvi.HLS_SATELLITE])
    except NotCachedError as exc:
        if "HLS pending" not in str(exc):
            return NotCached(site_id=site_id, message=str(exc))
        merged = None
    if merged is not None:
        merged = merged[merged["ID"] == site["id"]]
        points = _between(ndvi.with_smooth(ndvi.hls_points(merged)), start, end)
    if merged is None or points.empty:
        return NdviSeries(site_id=site_id, product=HLS_PRODUCT, status="pending", points=[], gaps=[],
                          low_veg_windows=[], qa_pass_share_by_month={})
    return NdviSeries(site_id=site_id, product=HLS_PRODUCT, status="ok", **_curve(points),
                      qa_pass_share_by_month=ndvi.hls_share_by_month(merged, start, end))


def ndvi_series(site_id: str, start: date | None = None, end: date | None = None, aqua: bool = False,
                window: bool = False, hls: bool = False) -> NdviSeries | NotCached:
    """The QA-filtered greenness curve for a site, with cloud gaps and low-vegetation windows.

    `aqua` interleaves Aqua points; `window` adds the 3x3-pixel spread (ORNL files, Nov 2023 on).
    `hls` returns the separate 30 m HLS curve instead (display only), so it excludes `aqua` and `window`.
    """
    if hls:
        if aqua or window:
            raise ValueError("hls is a separate 30 m curve: it cannot be combined with aqua or window")
        return _hls_series(site_id, start, end)
    try:
        loaded = _site_ndvi(site_id, aqua)
        windows = _windows(site_id, start, end) if window and loaded else []
    except NotCachedError as exc:
        return NotCached(site_id=site_id, message=str(exc))
    points = _between(loaded[2], start, end) if loaded else None
    if points is None or points.empty:
        return NdviSeries(site_id=site_id, product=_product(aqua), status="pending", points=[], gaps=[],
                          low_veg_windows=[], qa_pass_share_by_month={})
    ndvi_id, raw, _ = loaded
    return NdviSeries(site_id=site_id, product=_product(aqua), status="ok", **_curve(points),
                      qa_pass_share_by_month=ndvi.qa_share_by_month(raw, ndvi_id, start, end),
                      window_3x3=windows)


def ndvi_for_years(site_id: str, years: list[int], aqua: bool = False) -> NdviYears | NotCached:
    """One Boro-season curve per harvest year (1 Nov before to 31 May), gaps marked, never filled."""
    try:
        loaded = _site_ndvi(site_id, aqua)
    except NotCachedError as exc:
        return NotCached(site_id=site_id, message=str(exc))
    if loaded is None:
        return NdviYears(site_id=site_id, product=_product(aqua), status="pending", years=[])
    out = []
    for y in sorted(set(years)):
        start, end = date(y - 1, *NDVI_SEASON_START), date(y, *NDVI_SEASON_END)
        part = _between(loaded[2], start, end)
        status = "missing" if part.empty else "flagged" if y >= NDVI_FLAG_FROM_YEAR else "ok"
        out.append(NdviYear(year=y, start=start, end=end, status=status, **_curve(part)))
    return NdviYears(site_id=site_id, product=_product(aqua), status="ok", years=out)
