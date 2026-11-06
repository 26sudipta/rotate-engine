"""Step 14: leave-one-year-out backtest. No leakage, the pre-written verdict, honest fields."""
import json
from datetime import date

import pytest

from rotate_engine import backtest, cards_for_site, pipeline, run_backtest
from rotate_engine.__main__ import main
from rotate_engine.config import NDVI_YEARS
from rotate_engine.io import get_site
from rotate_engine.models import BacktestResult, NotCached
from rotate_engine.pipeline import match_features, season_features, site_peak_ndvi

DATE = date(2026, 11, 13)


def site_inputs(site_id):
    site = get_site(site_id)
    _, table, _, _ = season_features(site_id, DATE)
    return table, site_peak_ndvi(site), match_features(site)


def test_backtest_refits_per_fold(monkeypatch):
    table, peaks, features = site_inputs("ctg_anwara")
    seen = []  # (target, training years) of every fit inside the backtest
    real_match, real_anom = backtest.core.find_analogs, backtest.ndvi.anomalies
    monkeypatch.setattr(backtest.core, "find_analogs",
                        lambda t, target, train, *a, **kw: seen.append((target, list(train))) or
                        real_match(t, target, train, *a, **kw))
    monkeypatch.setattr(backtest.ndvi, "anomalies",
                        lambda p, train: seen.append((None, list(train))) or real_anom(p, train))
    tested, _, folds, _ = backtest.evaluate(table, peaks, features)
    assert [f.year for f in folds] == tested
    trend_fits = iter(train for target, train in seen if target is None)
    for f in folds:  # the held-out year never enters the trend, z-scores or covariance
        assert f.year not in next(trend_fits)
    assert all(target not in train for target, train in seen if target is not None)

    # and its own NDVI cannot move its prediction
    t = tested[len(tested) // 2]
    train = [y for y in tested if y != t]
    base = backtest.fold(table, peaks, t, train, features)
    bumped = peaks.copy()
    bumped[t] += 0.5
    moved = backtest.fold(table, bumped, t, train, features)
    assert moved.pred == pytest.approx(base.pred) and moved.truth == pytest.approx(base.truth + 0.5)


def test_skill_score_is_mse_based():
    assert backtest.skill([1.0, -1.0], [1.0, -1.0])[0] == 1.0
    assert backtest.skill([0.0, 0.0], [1.0, -1.0])[0] == 0.0  # climatology scores 0
    assert backtest.skill([0.1], [0.2])[0] == pytest.approx(0.75)  # RMSE ratio 0.5 -> MSE SS 0.75


@pytest.mark.parametrize("site_id", ["ctg_anwara", "barind_godagari"])
def test_backtest_result_follows_the_written_rule(site_id):
    r = run_backtest(site_id, DATE)
    assert isinstance(r, BacktestResult) and r.tag == "Derived" and r.n_permutations == 1000
    assert all(NDVI_YEARS[0] <= y <= NDVI_YEARS[1] for y in r.years_tested)
    assert [y.year for y in r.years] == r.years_tested
    assert all(y.year > NDVI_YEARS[1] for y in r.flagged_years) and r.flagged_years  # 2025 apart
    assert 0 < r.permutation_p <= 1 and 0 <= r.sign_test_p <= 1
    assert r.beat_clim_count == sum(y.beat_clim for y in r.years)
    skill = r.ss_mse > 0 and r.permutation_p < 0.10
    assert r.verdict_text.startswith("Some skill:" if skill else "No demonstrable skill:")
    assert skill or r.verdict_text.endswith("shown as historical examples only.")
    assert pipeline._compute_backtest(site_id, DATE, 5) == r  # fixed seed, uncached: same numbers


def test_decision_season_never_tests_the_method():
    r = run_backtest("ctg_anwara", date(2015, 11, 13))  # Boro 2016 is the decision season
    assert r.years_tested[-1] == 2015 and not r.flagged_years


def test_cards_carry_the_verdict_and_never_read_as_a_prediction():
    cs = cards_for_site("ctg_anwara", DATE)
    verdict = run_backtest("ctg_anwara", DATE).verdict_text
    assert f"Backtest: {verdict}" in cs.warnings
    assert cs.confidence.sentence.endswith("These are past examples, not a prediction for this season.")
    for card in cs.cards:
        item = next(e for e in card.evidence if e.label == "How the look-alike method did on past seasons")
        assert item.value == verdict and item.tag == "Derived"


def test_unknown_site():
    assert isinstance(run_backtest("nowhere", DATE), NotCached)


def test_cli_backtest(tmp_path):
    out = tmp_path / "b.json"
    assert main(["backtest", "--site", "barind_godagari", "--date", "2026-11-13", "--out", str(out)]) == 0
    assert "verdict_text" in json.loads(out.read_text())
