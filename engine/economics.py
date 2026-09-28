"""Cost and outcome accumulation built on a simulated Markov trace."""
from __future__ import annotations

import math
from copy import deepcopy
import pandas as pd


def _discount_factor(rate: float, cycle: int, cycle_years: float) -> float:
    return 1 / ((1 + rate) ** (cycle * cycle_years))


def evaluate_strategy(trace: pd.DataFrame, initial_cost: float, strategy_cost_per_cycle: float,
                      state_costs: dict[str, float], state_outcomes: dict[str, float] | None,
                      cycle_years: float, cost_discount_rate: float,
                      effect_discount_rate: float) -> dict:
    """Calculate discounted totals from cycle-start state occupancy.

    The initial cost occurs at time zero. Cycle outcomes use cycles 0..n-1,
    which makes a one-year, one-cycle Alive=100% example equal its utility.
    """
    cycle_costs: list[float] = []
    cycle_outcomes: list[float] = []
    for cycle, (_, distribution) in enumerate(trace.iloc[:-1].iterrows()):
        cost = float(distribution.dot(pd.Series(state_costs))) + strategy_cost_per_cycle
        discounted_cost = cost * _discount_factor(cost_discount_rate, cycle, cycle_years)
        cycle_costs.append(discounted_cost)
        if state_outcomes is not None:
            outcome = float(distribution.dot(pd.Series(state_outcomes))) * cycle_years
            cycle_outcomes.append(outcome * _discount_factor(effect_discount_rate, cycle, cycle_years))

    total_cost = float(initial_cost + sum(cycle_costs))
    return {
        "total_cost": total_cost,
        "total_outcome": float(sum(cycle_outcomes)) if state_outcomes is not None else None,
        "cycle_costs": cycle_costs,
        "cumulative_costs": [initial_cost] + [initial_cost + sum(cycle_costs[:i]) for i in range(1, len(cycle_costs) + 1)],
        "cycle_outcomes": cycle_outcomes,
        "cumulative_outcomes": [0.0] + [sum(cycle_outcomes[:i]) for i in range(1, len(cycle_outcomes) + 1)],
    }


def calculate_incremental(strategy_a: dict, strategy_b: dict, analysis_type: str) -> dict:
    delta_cost = strategy_a["total_cost"] - strategy_b["total_cost"]
    if analysis_type == "CMA":
        return {"cost": delta_cost, "outcome": None, "icer": None, "icer_status": "not_applicable"}
    delta_outcome = strategy_a["total_outcome"] - strategy_b["total_outcome"]
    if math.isclose(delta_outcome, 0.0, abs_tol=1e-8):
        return {"cost": delta_cost, "outcome": delta_outcome, "icer": None, "icer_status": "unstable"}
    return {"cost": delta_cost, "outcome": delta_outcome, "icer": delta_cost / delta_outcome, "icer_status": "valid"}


def convert_strategy_costs(strategy: dict, conversion_factor: float) -> dict:
    """Convert all cost results while preserving outcomes and cycle timing."""
    converted = deepcopy(strategy)
    for key in ("total_cost", "cycle_costs", "cumulative_costs"):
        value = converted[key]
        converted[key] = [item * conversion_factor for item in value] if isinstance(value, list) else value * conversion_factor
    return converted
