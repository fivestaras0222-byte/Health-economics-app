from __future__ import annotations

import json

import pandas as pd


def result_json(model: dict, result: dict) -> str:
    """Compact JSON suitable for a Streamlit download button."""
    serializable = {"study": model["study"], "incremental": result["incremental"],
                    "strategy_a": {k: v for k, v in result["strategy_a"].items() if not hasattr(v, "to_dict")},
                    "strategy_b": {k: v for k, v in result["strategy_b"].items() if not hasattr(v, "to_dict")}}
    return json.dumps(serializable, ensure_ascii=False, indent=2)


def result_csv(model: dict, result: dict) -> bytes:
    """Export the displayed summary values as a UTF-8 CSV file."""
    analysis = model["study"]["analysis_type"]
    a, b, incremental = result["strategy_a"], result["strategy_b"], result["incremental"]
    outcome_label = "QALY" if analysis == "CUA" else model["outcomes"]["effect_unit"]
    rows = [
        {"metric": "Total Cost", "strategy_a": a["total_cost"], "strategy_b": b["total_cost"], "incremental": incremental["cost"]},
    ]
    if analysis != "CMA":
        rows.extend([
            {"metric": outcome_label, "strategy_a": a["total_outcome"], "strategy_b": b["total_outcome"], "incremental": incremental["outcome"]},
            {"metric": "ICER", "strategy_a": "", "strategy_b": "", "incremental": incremental["icer"] if incremental["icer"] is not None else "Not applicable"},
        ])
    return pd.DataFrame(rows).to_csv(index=False).encode("utf-8-sig")
