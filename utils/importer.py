"""Import the deliberately simple two-row XLSX model-input format."""
from __future__ import annotations

from io import BytesIO
import math

import pandas as pd


REQUIRED_FIELDS = {
    "project_name", "analysis_type", "strategy_a", "strategy_b", "perspective", "currency", "price_year",
    "horizon_years", "cycle_years", "cost_discount_rate", "effect_discount_rate", "effect_unit", "states",
    "initial_distribution", "transition_matrix", "initial_cost_a", "initial_cost_b", "strategy_cost_a",
    "strategy_cost_b", "state_costs", "cea_effect_a", "cea_effect_b", "cua_utility_a", "cua_utility_b",
}


def _number(value, field: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid number: {field}") from exc
    if not math.isfinite(number):
        raise ValueError(f"Invalid number: {field}")
    return number


def _list(value, field: str, separator: str = "|") -> list[float]:
    return [_number(item.strip(), field) for item in str(value).split(separator) if item.strip()]


def load_excel_model(uploaded_file) -> dict:
    """Load one sheet with headers in row 1 and values in row 2."""
    content = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else uploaded_file.read()
    frame = pd.read_excel(BytesIO(content), sheet_name=0, nrows=1).fillna("")
    missing = REQUIRED_FIELDS - set(frame.columns)
    if missing:
        raise ValueError("Missing fields: " + ", ".join(sorted(missing)))
    row = frame.iloc[0].to_dict()
    states = [item.strip() for item in str(row["states"]).split("|") if item.strip()]
    if not states or len(states) != len(set(states)):
        raise ValueError("states must contain unique names separated by |")
    matrix = [_list(matrix_row, "transition_matrix", ",") for matrix_row in str(row["transition_matrix"]).split(";") if matrix_row.strip()]
    if len(matrix) != len(states) or any(len(matrix_row) != len(states) for matrix_row in matrix):
        raise ValueError("transition_matrix must have one semicolon-separated row per state")
    def state_values(field: str) -> dict[str, float]:
        values = _list(row[field], field)
        if len(values) != len(states):
            raise ValueError(f"{field} must contain one | separated value per state")
        return dict(zip(states, values))
    return {
        "study": {"project_name": str(row["project_name"]), "objective": "", "analysis_type": str(row["analysis_type"]), "strategy_a": str(row["strategy_a"]), "strategy_b": str(row["strategy_b"]), "perspective": str(row["perspective"]), "currency": str(row["currency"]), "price_year": int(_number(row["price_year"], "price_year"))},
        "time": {"horizon_years": _number(row["horizon_years"], "horizon_years"), "cycle_years": _number(row["cycle_years"], "cycle_years"), "cost_discount_rate": _number(row["cost_discount_rate"], "cost_discount_rate"), "effect_discount_rate": _number(row["effect_discount_rate"], "effect_discount_rate")},
        "markov": {"states": states, "initial_distribution": _list(row["initial_distribution"], "initial_distribution"), "transition_matrix": matrix},
        "costs": {"initial_cost": {"A": _number(row["initial_cost_a"], "initial_cost_a"), "B": _number(row["initial_cost_b"], "initial_cost_b")}, "strategy_cost_per_cycle": {"A": _number(row["strategy_cost_a"], "strategy_cost_a"), "B": _number(row["strategy_cost_b"], "strategy_cost_b")}, "state_cost_per_cycle": state_values("state_costs")},
        "outcomes": {"effect_unit": str(row["effect_unit"]), "state_effect": {"A": state_values("cea_effect_a"), "B": state_values("cea_effect_b")}, "state_utility": {"A": state_values("cua_utility_a"), "B": state_values("cua_utility_b")}},
    }
