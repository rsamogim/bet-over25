from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import shin
from scipy.optimize import brentq
from scipy.stats import poisson

MONTE_CARLO_SIMULATIONS = 100_000
MONTE_CARLO_TOLERANCE = 0.02


@dataclass
class DevigResult:
    prob_over_2_5: float
    prob_under_2_5: float
    expected_goals: float
    monte_carlo_prob_under_2_5: float


def devig_over_under_2_5(odd_over_2_5: float, odd_under_2_5: float) -> DevigResult:
    prob_over, prob_under = shin.calculate_implied_probabilities(
        [odd_over_2_5, odd_under_2_5]
    )
    expected_goals = _solve_expected_goals(prob_under)
    mc_prob_under = _monte_carlo_prob_under(expected_goals)

    if abs(mc_prob_under - prob_under) > MONTE_CARLO_TOLERANCE:
        raise ValueError(
            f"Monte Carlo (p={mc_prob_under:.4f}) diverge do valor analítico "
            f"(p={prob_under:.4f}) além da tolerância {MONTE_CARLO_TOLERANCE} — "
            "provável erro de implementação, não usar o resultado."
        )

    return DevigResult(
        prob_over_2_5=prob_over,
        prob_under_2_5=prob_under,
        expected_goals=expected_goals,
        monte_carlo_prob_under_2_5=mc_prob_under,
    )


def _solve_expected_goals(prob_under_2_5: float, low: float = 0.01, high: float = 15.0) -> float:
    return brentq(lambda lam: poisson.cdf(2, lam) - prob_under_2_5, low, high)


def _monte_carlo_prob_under(expected_goals: float, n: int = MONTE_CARLO_SIMULATIONS) -> float:
    rng = np.random.default_rng()
    sims = rng.poisson(expected_goals, size=n)
    return float(np.mean(sims <= 2))
