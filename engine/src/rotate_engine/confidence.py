"""Agreement among the k analogs, reported with its exact chance rate (binomial, p = 0.5)."""
from math import comb

from .models import Confidence


def chance_rate(k: int, agree: int) -> float:
    """P(the larger side has >= agree of k votes) when each vote is a fair coin."""
    if agree <= k / 2:
        return 1.0
    return min(1.0, sum(2 * comb(k, j) for j in range(agree, k + 1)) / 2 ** k)


def confidence(anomalies: list[float], weights: list[float], subject: str,
               basis: str = "ndvi") -> Confidence:
    """Each analog votes on the sign of its anomaly; > 0 is above normal, otherwise below."""
    k = len(anomalies)
    above = [a > 0 for a in anomalies]
    majority_above = sum(above) * 2 > k
    agree = sum(v == majority_above for v in above)
    weighted = sum(w for w, v in zip(weights, above) if v == majority_above) / sum(weights)
    rate = chance_rate(k, agree)
    label = "high" if agree == k else "moderate" if agree == k - 1 else "split"
    direction = "above_normal" if majority_above else "below_normal"
    word = "above" if majority_above else "below"
    sentence = (f"In {agree} of the {k} past seasons that started like this one, {subject} was "
                f"{word} normal. Random years agree this much about {round(rate * 100)}% of the time. "
                "These are past examples, not a prediction for this season.")
    return Confidence(k=k, agree_count=agree, direction=direction,
                      weighted_agreement=round(weighted, 4), chance_rate=rate, label=label,
                      sentence=sentence, basis=basis)
