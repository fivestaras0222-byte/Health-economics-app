"""Input controls and conversion into a model dictionary."""
from __future__ import annotations

import pandas as pd
import streamlit as st
from ui.i18n import t


def _years(value: float, unit: str) -> float:
    return value / {"年": 1, "季度": 4, "月": 12, "Year": 1, "Quarter": 4, "Month": 12}[unit]


def render_inputs(language: str, preset: dict | None = None) -> tuple[dict, bool]:
    tr = lambda key: t(key, language)
    units, perspectives = tr("years"), tr("perspectives")
    preset = preset or {}
    input_version = st.session_state.get("input_version", 0)
    widget_key = lambda name: f"{name}_{input_version}"
    study_preset = preset.get("study", {})
    time_preset = preset.get("time", {})
    markov_preset = preset.get("markov", {})
    cost_preset = preset.get("costs", {})
    with st.expander(tr("design"), expanded=True):
        project_name = st.text_input(tr("project"), study_preset.get("project_name", "Health economics evaluation" if language == "en" else "卫生经济学评价项目"), key=widget_key("project_name"))
        analysis_options = ["CMA", "CEA", "CUA"]
        analysis_type = st.radio(tr("analysis"), analysis_options, horizontal=True, index=analysis_options.index(study_preset.get("analysis_type", "CUA")) if study_preset.get("analysis_type", "CUA") in analysis_options else 2, key=widget_key("analysis_type"))
        ca, cb = st.columns(2)
        with ca: name_a = st.text_input(tr("strategy_a"), study_preset.get("strategy_a", "Treatment A"), key=widget_key("strategy_a"))
        with cb: name_b = st.text_input(tr("strategy_b"), study_preset.get("strategy_b", "Treatment B"), key=widget_key("strategy_b"))
        perspective = st.selectbox(tr("perspective"), perspectives, key=widget_key("perspective"))
        currency_options = ["CNY", "USD"]
        source_currency_key = widget_key("input_currency")
        current_currency_key = widget_key("current_currency")
        source_default = study_preset.get("currency", "CNY")
        if current_currency_key not in st.session_state:
            st.session_state[current_currency_key] = source_default if source_default in currency_options else "CNY"

        def sync_current_currency() -> None:
            st.session_state[current_currency_key] = st.session_state[source_currency_key]

        input_currency = st.selectbox(
            "初始成本货币" if language == "zh" else "Initial cost currency",
            currency_options,
            index=currency_options.index(source_default) if source_default in currency_options else 0,
            key=source_currency_key,
            on_change=sync_current_currency,
        )
        switch_col, current_col = st.columns(2)
        with switch_col:
            if st.button("切换汇率" if language == "zh" else "Switch currency", use_container_width=True, key=widget_key("switch_currency")):
                st.session_state[current_currency_key] = "USD" if st.session_state[current_currency_key] == "CNY" else "CNY"
                st.rerun()
        with current_col:
            st.caption("当前货币" if language == "zh" else "Current currency")
            st.markdown(f"**{st.session_state[current_currency_key]}**")
        currency = st.session_state[current_currency_key]
        exchange_rate = st.number_input(
            "汇率：1 USD = X CNY" if language == "zh" else "Exchange rate: 1 USD = X CNY",
            min_value=1.0001, value=7.0,
            format="%.4f", key=widget_key("exchange_rate_usd_cny"),
        )
        st.caption("切换时按 1 USD = X CNY 自动换算成本；汇率请手动填写。" if language == "zh" else "Switching converts costs using 1 USD = X CNY. Enter the rate manually.")
        price_year = st.number_input(tr("price_year"), 2000, 2100, int(study_preset.get("price_year", 2026)), key=widget_key("price_year"))
    with st.expander(tr("model"), expanded=True):
        ch, cl = st.columns(2)
        with ch:
            horizon_value = st.number_input(tr("horizon"), min_value=0.01, value=float(time_preset.get("horizon_years", 5.0)), key=widget_key("horizon"))
            horizon_unit = st.selectbox(tr("horizon_unit"), units, key=widget_key("horizon_unit"))
        with cl:
            cycle_value = st.number_input(tr("cycle"), min_value=0.01, value=float(time_preset.get("cycle_years", 1.0)), key=widget_key("cycle"))
            cycle_unit = st.selectbox(tr("cycle_unit"), units, key=widget_key("cycle_unit"))
        cd, ed = st.columns(2)
        with cd: cost_rate = st.number_input(tr("cost_discount"), 0.0, 1.0, float(time_preset.get("cost_discount_rate", 0.0)), format="%.4f", key=widget_key("cost_discount"))
        with ed: effect_rate = st.number_input(tr("effect_discount"), 0.0, 1.0, float(time_preset.get("effect_discount_rate", 0.0)), format="%.4f", key=widget_key("effect_discount"))
        states_text = st.text_area(tr("states"), "\n".join(markov_preset.get("states", ["Stable", "Progression", "Death"])), key=widget_key("states"))
        states = [item.strip() for item in states_text.splitlines() if item.strip()]
        initial_values = list(markov_preset.get("initial_distribution", [1.0] + [0.0] * max(0, len(states)-1)))
        # A changed state list or malformed import must not crash the interface.
        if len(initial_values) != len(states):
            initial_values = [1.0] + [0.0] * max(0, len(states)-1)
        initial = st.data_editor(pd.DataFrame({tr("state"): states, tr("initial"): initial_values}), hide_index=True, disabled=[tr("state")], key=widget_key("initial_distribution"))
        st.caption(tr("initial_caption"))
        # Default values match the complete three-state test scenario.
        if markov_preset.get("transition_matrix") and markov_preset.get("states") == states:
            matrix_default = pd.DataFrame(markov_preset["transition_matrix"], index=states, columns=states)
        elif states == ["Stable", "Progression", "Death"]:
            matrix_default = pd.DataFrame(
                [[0.80, 0.15, 0.05], [0.00, 0.90, 0.10], [0.00, 0.00, 1.00]],
                index=states, columns=states,
            )
        else:
            matrix_default = pd.DataFrame(0.0, index=states, columns=states)
            for i in range(len(states)): matrix_default.iloc[i, i] = 1.0
        matrix = st.data_editor(matrix_default, key=widget_key("transition_matrix"))
        st.caption(tr("matrix_caption"))
    with st.expander(tr("costs"), expanded=True):
        is_default_scenario = states == ["Stable", "Progression", "Death"]
        costs = st.data_editor(
            pd.DataFrame({tr("item"): [tr("initial_cost"), tr("strategy_cost")], name_a: [cost_preset.get("initial_cost", {}).get("A", 10000.0 if is_default_scenario else 0.0), cost_preset.get("strategy_cost_per_cycle", {}).get("A", 500.0 if is_default_scenario else 0.0)], name_b: [cost_preset.get("initial_cost", {}).get("B", 8000.0 if is_default_scenario else 0.0), cost_preset.get("strategy_cost_per_cycle", {}).get("B", 300.0 if is_default_scenario else 0.0)]}),
            hide_index=True, disabled=[tr("item")], key=widget_key("strategy_costs")
        )
        state_cost_values = [cost_preset.get("state_cost_per_cycle", {}).get(state, default) for state, default in zip(states, [2000.0, 5000.0, 0.0] if is_default_scenario else [0.0]*len(states))]
        state_cost = st.data_editor(pd.DataFrame({tr("state"): states, tr("state_cost"): state_cost_values}), hide_index=True, disabled=[tr("state")], key=widget_key("state_costs"))
    outcomes = None
    if analysis_type != "CMA":
        with st.expander(tr("utility") if analysis_type == "CUA" else tr("effect"), expanded=True):
            effect_unit = st.text_input(tr("effect_unit"), preset.get("outcomes", {}).get("effect_unit", "life-years"), key=widget_key("effect_unit")) if analysis_type == "CEA" else "QALY"
            imported_outcomes = preset.get("outcomes", {}).get("state_utility" if analysis_type == "CUA" else "state_effect", {})
            if imported_outcomes:
                defaults_a = [imported_outcomes.get("A", {}).get(state, 0.0) for state in states]
                defaults_b = [imported_outcomes.get("B", {}).get(state, 0.0) for state in states]
            elif is_default_scenario and analysis_type == "CUA":
                defaults_a, defaults_b = [0.90, 0.50, 0.0], [0.80, 0.45, 0.0]
            elif is_default_scenario and analysis_type == "CEA":
                # Teaching/test values: effective life-years per cycle by state.
                defaults_a, defaults_b = [1.00, 0.75, 0.0], [0.90, 0.65, 0.0]
            else:
                defaults_a, defaults_b = [0.0]*len(states), [0.0]*len(states)
            frame = st.data_editor(pd.DataFrame({tr("state"): states, name_a: defaults_a, name_b: defaults_b}), hide_index=True, disabled=[tr("state")], key=widget_key(f"outcomes_{analysis_type}"))
            outcomes = {"A": dict(zip(states, frame[name_a].tolist())), "B": dict(zip(states, frame[name_b].tolist()))}
    else: effect_unit = None
    run = st.button(tr("run"), type="primary", use_container_width=True)
    model = {"study": {"project_name": project_name, "objective": "", "analysis_type": analysis_type, "strategy_a": name_a, "strategy_b": name_b, "perspective": perspective, "input_currency": input_currency, "currency": currency, "exchange_rate_usd_cny": exchange_rate, "price_year": int(price_year)}, "time": {"horizon_years": _years(horizon_value, horizon_unit), "cycle_years": _years(cycle_value, cycle_unit), "cost_discount_rate": cost_rate, "effect_discount_rate": effect_rate}, "markov": {"states": states, "initial_distribution": initial[tr("initial")].tolist(), "transition_matrix": matrix.values.tolist()}, "costs": {"initial_cost": {"A": costs.iloc[0][name_a], "B": costs.iloc[0][name_b]}, "strategy_cost_per_cycle": {"A": costs.iloc[1][name_a], "B": costs.iloc[1][name_b]}, "state_cost_per_cycle": dict(zip(states, state_cost[tr("state_cost")].tolist()))}, "outcomes": {"effect_unit": effect_unit, "state_utility": outcomes if analysis_type == "CUA" else {}, "state_effect": outcomes if analysis_type == "CEA" else {}}}
    return model, run
