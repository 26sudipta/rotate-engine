"""Leave-one-year-out backtest of the NDVI analog pool (report "Backtest protocol").

The protocol and verdict rule were fixed in docs/ENGINE.md before the first run.
"""
from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd
from scipy.stats import binomtest

from . import analogs as core
from . import ndvi
from .config import (K, NDVI_YEARS, N_PERMUTATIONS, PERMUTATION_SEED, SKILL_P, VERDICT_NO_SKILL,
                     VERDICT_SKILL)
from .models import BacktestResult, BacktestYear, CalibrationBin


@dataclass(frozen=True)
class Fold:
    year: int
    truth: float
    pred: float
    pred_euclid: float
    analog_years: tuple[int, ...]
    weights: tuple[float, ...]
    agree: int
    majority_above: bool
    train_anom: pd.Series  # training years' anomalies, for the permutation null
    terciles: tuple[float, float]  # training-anomaly tercile edges


def fold(table: pd.DataFrame, peaks: pd.Series, year: int, train: list[int],
         features: tuple[str, ...], k: int = K) -> Fold:
    """Predict `year` from `train` only: features, trend, z-scores, covariance and NDVI trend."""
    anom = ndvi.anomalies(peaks.loc[train + [year]], train)
    lw = core.find_analogs(table, year, train, k, features=features)
    eu = core.find_analogs(table, year, train, k, method="euclidean", features=features)
    predict = lambda r: float(sum(m.weight * anom[m.year] for m in r.matches))
    above = sum(anom[m.year] > 0 for m in lw.matches)
    train_anom = anom.loc[train]
    lo, hi = np.quantile(train_anom.to_numpy(), [1 / 3, 2 / 3])
    return Fold(year=year, truth=float(anom[year]), pred=predict(lw), pred_euclid=predict(eu),
                analog_years=tuple(m.year for m in lw.matches),
                weights=tuple(m.weight for m in lw.matches), agree=max(above, k - above),
                majority_above=above * 2 > k, train_anom=train_anom, terciles=(float(lo), float(hi)))


def skill(pred, truth) -> tuple[float, float, float]:
    """(SS_MSE, MSE_analog, MSE_clim); climatology predicts an anomaly of 0."""
    pred, truth = np.asarray(pred, float), np.asarray(truth, float)
    mse_a, mse_c = float(np.mean((pred - truth) ** 2)), float(np.mean(truth ** 2))
    return 1 - mse_a / mse_c, mse_a, mse_c


def permutation_p(folds: list[Fold], observed: float, k: int, n: int = N_PERMUTATIONS,
                  seed: int = PERMUTATION_SEED) -> float:
    """Share of runs with k random training years per fold (fold weights kept) scoring >= observed."""
    rng = np.random.default_rng(seed)
    truth = [f.truth for f in folds]
    hits = 0
    for _ in range(n):
        pred = [float(np.dot(f.weights, rng.choice(f.train_anom.to_numpy(), k, replace=False)))
                for f in folds]
        hits += skill(pred, truth)[0] >= observed
    return (1 + hits) / (1 + n)


def _tercile(x: float, edges: tuple[float, float]) -> int:
    return int(np.searchsorted(edges, x))


def _row(f: Fold) -> BacktestYear:
    return BacktestYear(year=f.year, ndvi_anomaly=round(f.truth, 4), predicted=round(f.pred, 4),
                        analog_years=list(f.analog_years), agree_count=f.agree,
                        beat_clim=abs(f.pred - f.truth) < abs(f.truth))


def evaluate(table: pd.DataFrame, peaks: pd.Series, features: tuple[str, ...], k: int = K):
    """(tested years, excluded years, LOYO folds, folds for flagged years after NDVI_YEARS)."""
    usable = lambda y: y in peaks.index and y in table.index and table.loc[y, list(features)].notna().all()
    span = range(NDVI_YEARS[0], NDVI_YEARS[1] + 1)
    tested = [y for y in span if usable(y)]
    excluded = [y for y in span if y not in tested]
    folds = [fold(table, peaks, y, [t for t in tested if t != y], features, k) for y in tested]
    later = [y for y in peaks.index if y > NDVI_YEARS[1] and usable(y)]
    return tested, excluded, folds, [fold(table, peaks, int(y), tested, features, k) for y in later]


def result(site_id: str, decision_date: date, doy: tuple[int, int], tested: list[int],
           excluded: list[int], folds: list[Fold], flagged: list[Fold], k: int = K) -> BacktestResult:
    truth = [f.truth for f in folds]
    ss, mse_a, mse_c = skill([f.pred for f in folds], truth)
    pred = np.array([f.pred for f in folds])
    corr = None if pred.std() == 0 else float(np.corrcoef(pred, truth)[0, 1])
    beat = sum(abs(f.pred - f.truth) < abs(f.truth) for f in folds)
    p_perm = permutation_p(folds, ss, k)
    bins = []
    for a in range(k // 2 + 1, k + 1):
        group = [f for f in folds if f.agree == a]
        rate = (sum((f.truth > 0) == f.majority_above for f in group) / len(group)) if group else None
        bins.append(CalibrationBin(agree_count=a, n=len(group), hit_rate=None if rate is None else round(rate, 4)))
    verdict = VERDICT_SKILL if ss > 0 and p_perm < SKILL_P else VERDICT_NO_SKILL
    return BacktestResult(
        site_id=site_id, decision_date=decision_date, years_tested=tested, k=k,
        predictand=(f"Boro peak-window NDVI (day of year {doy[0]}–{doy[1]}) minus the training-year "
                    f"trend; matched on the 60 days before {decision_date:%d %b} each year"),
        ss_mse=round(ss, 4), mse_analog=round(mse_a, 6), mse_clim=round(mse_c, 6),
        ss_mse_euclid=round(skill([f.pred_euclid for f in folds], truth)[0], 4),
        anomaly_corr=None if corr is None else round(corr, 4),
        tercile_hit_rate=round(float(np.mean([_tercile(f.pred, f.terciles) == _tercile(f.truth, f.terciles)
                                              for f in folds])), 4),
        beat_clim_count=int(beat),
        sign_test_p=round(binomtest(int(beat), len(folds), 0.5, alternative="greater").pvalue, 4),
        permutation_p=round(p_perm, 4), n_permutations=N_PERMUTATIONS, calibration_bins=bins,
        verdict_text=verdict.format(ss=ss, n=len(tested), first=tested[0], last=tested[-1], p=p_perm),
        excluded_years=excluded, years=[_row(f) for f in folds], flagged_years=[_row(f) for f in flagged])
