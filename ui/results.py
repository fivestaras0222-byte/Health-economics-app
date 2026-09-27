"""Result cards, tables and ICER explanation."""
from __future__ import annotations

import pandas as pd
import streamlit as st
from ui.i18n import t


def money(value: float, currency: str) -> str:
    return f"{currency} {value:,.2f}"


def render_results(result: dict, model: dict, language: str) -> None:
    tr = lambda key: t(key, language)
    study = model["study"]; analysis = study["analysis_type"]; inc = result["incremental"]
    a = result["strategy_a"]; b = result["strategy_b"]
    st.subheader(tr("summary"))
    cols = st.columns(3)
    cols[0].metric(f"{study['strategy_a']} {tr('total_cost')}", money(a["total_cost"], study["currency"]))
    cols[1].metric(f"{study['strategy_b']} {tr('total_cost')}", money(b["total_cost"], study["currency"]))
    cols[2].metric(tr("delta_cost"), money(inc["cost"], study["currency"]))
    if analysis != "CMA":
        outcome_label = "QALY" if analysis == "CUA" else model["outcomes"]["effect_unit"]
        cols = st.columns(3)
        cols[0].metric(f"{study['strategy_a']} {outcome_label}", f"{a['total_outcome']:,.4f}")
        cols[1].metric(f"{study['strategy_b']} {outcome_label}", f"{b['total_outcome']:,.4f}")
        cols[2].metric(f"Δ {outcome_label}", f"{inc['outcome']:,.4f}")

    st.subheader(tr("incremental"))
    rows = [{tr("metric"): tr("total_cost"), study["strategy_a"]: money(a["total_cost"], study["currency"]), study["strategy_b"]: money(b["total_cost"], study["currency"]), tr("delta"): money(inc["cost"], study["currency"])}]
    if analysis != "CMA":
        label = "QALY" if analysis == "CUA" else model["outcomes"]["effect_unit"]
        rows.append({tr("metric"): label, study["strategy_a"]: f"{a['total_outcome']:.4f}", study["strategy_b"]: f"{b['total_outcome']:.4f}", tr("delta"): f"{inc['outcome']:.4f}"})
        icer_value = tr("not_applicable") if inc["icer"] is None else f"{inc['icer']:,.2f} {study['currency']}/{label}"
        rows.append({tr("metric"): "ICER", study["strategy_a"]: "—", study["strategy_b"]: "—", tr("delta"): icer_value})
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
    if inc["icer_status"] == "unstable":
        st.warning(tr("unstable"))
