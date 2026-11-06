"""Analog-year matching: detrend -> z-score -> Ledoit-Wolf precision -> Mahalanobis D -> top k.

Everything is fitted on `train_years` only, so the backtest can refit per fold.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.stats import chi2
from sklearn.covariance import LedoitWolf

from .config import CLOSE_MATCH_QUANTILE, DETREND_FEATURES, FEATURES, K


@dataclass(frozen=True)
class Match:
    year: int
    rank: int
    distance: float
    weight: float
    close_match: bool


@dataclass(frozen=True)
class MatchResult:
    method: str  # "ledoit_wolf" or "euclidean"
    matches: tuple[Match, ...]
    shrinkage: float | None
    warnings: tuple[str, ...]


def standardise(table: pd.DataFrame, target: int, train_years: list[int],
                features: tuple[str, ...] = FEATURES) -> tuple[np.ndarray, np.ndarray]:
    """Return (Z_train, z_target). Trend, mean and SD come from the training years only."""
    if target in train_years:
        raise ValueError(f"target season {target} is in its own training set")
    x = table.loc[list(train_years) + [target], list(features)].astype(float).copy()
    years = np.asarray(x.index, dtype=float)
    n = len(train_years)
    for col in features:
        if col in DETREND_FEATURES:
            b, a = np.polyfit(years[:n], x[col].to_numpy()[:n], 1)
            x[col] = x[col] - (a + b * years)
    arr = x.to_numpy()
    mean, sd = arr[:n].mean(axis=0), arr[:n].std(axis=0, ddof=1)
    sd = np.where(sd > 0, sd, 1.0)
    z = (arr - mean) / sd
    return z[:n], z[n]


def distances(z_train: np.ndarray, z_target: np.ndarray, precision: np.ndarray) -> np.ndarray:
    d = z_train - z_target
    return np.sqrt(np.maximum(np.einsum("ij,jk,ik->i", d, precision, d), 0.0))


def kernel_weights(d: np.ndarray) -> np.ndarray:
    h = max(float(np.median(d)), 1e-9)
    w = np.exp(-(d ** 2) / (2 * h ** 2))
    return w / w.sum()


def _top_k(train_years: list[int], d: np.ndarray, k: int, cutoff: float,
           eligible: set[int] | None = None) -> tuple[Match, ...]:
    idx = [i for i in range(len(d)) if eligible is None or train_years[i] in eligible]
    order = sorted(idx, key=lambda i: (d[i], train_years[i]))[:k]
    dk = d[order]
    w = kernel_weights(dk)
    return tuple(Match(int(train_years[i]), r + 1, float(dk[r]), float(w[r]), bool(dk[r] <= cutoff))
                 for r, i in enumerate(order))


def find_analogs(table: pd.DataFrame, target: int, train_years: list[int], k: int = K,
                 method: str = "ledoit_wolf", features: tuple[str, ...] = FEATURES,
                 eligible: set[int] | None = None) -> MatchResult:
    """k nearest training seasons to `target` in the standardised feature space.

    Scaling and covariance always use all `train_years`; `eligible` only limits which can be picked.
    """
    train_years = sorted(train_years)
    z_train, z_target = standardise(table, target, train_years, features)
    p = z_train.shape[1]
    cutoff = float(np.sqrt(chi2.ppf(CLOSE_MATCH_QUANTILE, p)))
    warnings: list[str] = []
    shrinkage = None
    precision = np.eye(p)
    if method == "ledoit_wolf":
        lw = LedoitWolf().fit(z_train)
        shrinkage = float(lw.shrinkage_)
        d = distances(z_train, z_target, lw.precision_)
        if np.isfinite(d).all():
            precision = lw.precision_
        else:
            method = "euclidean"
            warnings.append("Ledoit-Wolf distances were not finite; fell back to standardised "
                            "Euclidean distance.")
    d = distances(z_train, z_target, precision)
    assert np.isfinite(d).all(), "non-finite analog distance"
    matches = _top_k(train_years, d, k, cutoff, eligible)
    if not matches[0].close_match:
        warnings.append("No close look-alike year this time: even the nearest year is outside "
                        "the 95% closeness cutoff.")
    return MatchResult(method, matches, shrinkage, tuple(warnings))


def euclid_overlap(table: pd.DataFrame, target: int, train_years: list[int], result: MatchResult,
                   k: int = K, features: tuple[str, ...] = FEATURES, eligible: set[int] | None = None) -> str:
    """How many of the chosen analogs standardised Euclidean distance also picks."""
    other = find_analogs(table, target, train_years, k, method="euclidean", features=features,
                         eligible=eligible)
    common = {m.year for m in result.matches} & {m.year for m in other.matches}
    return f"{len(common)} of {len(result.matches)}"
