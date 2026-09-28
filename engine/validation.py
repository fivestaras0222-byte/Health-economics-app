"""Validation routines kept independent from the Streamlit interface."""
from __future__ import annotations

import math
from typing import Iterable

import numpy as np


EPSILON = 1e-8


def _number_errors(values: Iterable[float], label: str, minimum: float | None = None,
                   maximum: float | None = None) -> list[str]:
    errors: list[str] = []
    for index, value in enumerate(values):
        try:
            number = float(value)
        except (TypeError, ValueError):
            errors.append(f"{label}第 {index + 1} 项不是有效数字。")
            continue
        if not math.isfinite(number):
            errors.append(f"{label}第 {index + 1} 项不能为 NaN 或 Inf。")
        elif minimum is not None and number < minimum:
            errors.append(f"{label}第 {index + 1} 项不能小于 {minimum}。")
        elif maximum is not None and number > maximum:
            errors.append(f"{label}第 {index + 1} 项不能大于 {maximum}。")
    return errors


def validate_model(model: dict) -> list[str]:
    """Return all user-facing validation messages; never raise for input errors."""
    errors: list[str] = []
    states = model["markov"]["states"]
    initial = model["markov"]["initial_distribution"]
    matrix = model["markov"]["transition_matrix"]
    analysis_type = model["study"]["analysis_type"]

    if len(states) < 1:
        errors.append("请至少输入一个健康状态。")
    if len(set(states)) != len(states):
        errors.append("健康状态名称不能重复。")
    if len(initial) != len(states):
        errors.append("初始状态分布的数量必须与健康状态数量一致。")
    else:
        errors += _number_errors(initial, "初始状态分布", 0, 1)
        if not errors or all("初始状态分布" not in item for item in errors):
            total = float(np.sum(np.asarray(initial, dtype=float)))
            if not math.isclose(total, 1.0, abs_tol=EPSILON):
                errors.append(f"初始状态比例总和为 {total:.6f}，应为 1.000000。")

    if len(matrix) != len(states):
        errors.append("转移矩阵行数必须与健康状态数量一致。")
    for row_index, row in enumerate(matrix):
        if len(row) != len(states):
            errors.append(f"{states[row_index] if row_index < len(states) else '第 '+str(row_index+1)} 行的转移概率数量不正确。")
            continue
        row_errors = _number_errors(row, f"{states[row_index]} 行转移概率", 0, 1)
        errors += row_errors
        if not row_errors:
            total = float(np.sum(np.asarray(row, dtype=float)))
            if not math.isclose(total, 1.0, abs_tol=EPSILON):
                errors.append(f"{states[row_index]} 行的转移概率总和为 {total:.6f}，应为 1.000000。")

    time = model["time"]
    if time["horizon_years"] <= 0:
        errors.append("时间范围必须大于 0。")
    if time["cycle_years"] <= 0:
        errors.append("周期长度必须大于 0。")
    if time["horizon_years"] / time["cycle_years"] % 1 > EPSILON:
        errors.append("时间范围必须能被周期长度整除。")
    errors += _number_errors([time["cost_discount_rate"], time["effect_discount_rate"]], "折现率", 0)
    errors += _number_errors([model["study"].get("exchange_rate_usd_cny", 7.0)], "汇率", 1.0000001)

    costs = model["costs"]
    errors += _number_errors(
        [costs["initial_cost"]["A"], costs["initial_cost"]["B"],
         costs["strategy_cost_per_cycle"]["A"], costs["strategy_cost_per_cycle"]["B"]],
        "方案成本", 0,
    )
    errors += _number_errors(list(costs["state_cost_per_cycle"].values()), "健康状态成本", 0)

    if analysis_type == "CUA":
        for strategy, values in model["outcomes"]["state_utility"].items():
            errors += _number_errors(list(values.values()), f"{strategy}方案 Utility", 0, 1)
    if analysis_type == "CEA":
        for strategy, values in model["outcomes"]["state_effect"].items():
            errors += _number_errors(list(values.values()), f"{strategy}方案 Effect", 0)
    return errors
