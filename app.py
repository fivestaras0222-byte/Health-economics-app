from __future__ import annotations

import math
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from engine.economics import calculate_incremental, evaluate_strategy
from engine.markov import run_markov
from engine.validation import validate_model
from ui.charts import comparison_chart, state_chart
from ui.inputs import render_inputs
from ui.i18n import t
from ui.results import render_results
from utils.export import result_csv, result_json
from utils.importer import load_excel_model


def convert_strategy_costs(strategy: dict, conversion_factor: float) -> dict:
    """Convert cost totals and their trend series without changing outcomes."""
    converted = dict(strategy)
    converted["total_cost"] = strategy["total_cost"] * conversion_factor
    converted["cycle_costs"] = [value * conversion_factor for value in strategy["cycle_costs"]]
    converted["cumulative_costs"] = [value * conversion_factor for value in strategy["cumulative_costs"]]
    return converted


st.set_page_config(page_title="HEval 卫生经济学评价分析系统", page_icon="⚕", layout="wide")
st.markdown("""<style>
    .block-container {padding-top: 1.6rem; padding-bottom: 2rem;}
    [data-testid='stVerticalBlockBorderWrapper'] {border-color: #dbe5ee; border-radius: 10px;}
</style>""", unsafe_allow_html=True)
language_label = st.sidebar.selectbox("Language / 界面语言", ["中文", "English"])
language = "zh" if language_label == "中文" else "en"
tr = lambda key: t(key, language)
upload_label = "使用 XLSX 文件导入" if language == "zh" else "Use XLSX file to import"
choose_label = "选择 XLSX 文件" if language == "zh" else "Choose XLSX file"
format_label = "XLSX 格式说明" if language == "zh" else "XLSX format"
format_text = (
    "仅一个工作表、仅两行：第 1 行为字段名，第 2 行为数值。多状态数值使用 | 分隔；转移矩阵各行使用 ; 分隔。请直接使用下方已测试数据作为模板。"
    if language == "zh" else
    "Use one worksheet with exactly two rows: field names in row 1 and values in row 2. Separate state values with | and transition-matrix rows with ;. Use the tested files below as templates."
)
uploaded_file = st.sidebar.file_uploader(choose_label, type=["xlsx"], key="excel_upload")
if st.sidebar.button(upload_label, use_container_width=True, disabled=uploaded_file is None):
    try:
        imported_model = load_excel_model(uploaded_file)
        # Give every import a fresh set of widget keys.  Without this, Streamlit
        # can reuse an earlier 3-state data_editor value after a 5-state file is
        # displayed, causing the model to change when the user clicks Run.
        st.session_state["input_version"] = st.session_state.get("input_version", 0) + 1
        for state_key in ("project_name", "analysis_type", "strategy_a", "strategy_b", "input_currency", "currency", "exchange_rate_usd_cny", "price_year", "horizon", "horizon_unit", "cycle", "cycle_unit", "cost_discount", "effect_discount", "states", "initial_distribution", "transition_matrix", "strategy_costs", "state_costs", "outcomes_CEA", "outcomes_CUA", "effect_unit", "latest_result", "latest_model"):
            st.session_state.pop(state_key, None)
        st.session_state["imported_model"] = imported_model
        st.rerun()
    except Exception as exc:
        st.sidebar.error(("导入失败：" if language == "zh" else "Import failed: ") + str(exc))
st.sidebar.caption(format_label + "：" + format_text)
template_label = "示例文件下载" if language == "zh" else "Download example file"
template_help = "下载后可直接填写第 2 行并导入。" if language == "zh" else "Edit row 2 directly, then import the file."
template_path = ROOT / "assets" / "model_input_template.xlsx"
if template_path.exists():
    st.sidebar.download_button(template_label, template_path.read_bytes(), "model_input_template.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", help=template_help, use_container_width=True)
reset_label = "恢复默认测试数据" if language == "zh" else "Restore default test data"
if st.sidebar.button(reset_label, use_container_width=True):
    # Reset also needs a fresh key namespace, otherwise a prior imported model
    # may be restored from Streamlit's widget-state cache.
    st.session_state["input_version"] = st.session_state.get("input_version", 0) + 1
    for state_key in ("project_name", "analysis_type", "strategy_a", "strategy_b", "input_currency", "currency", "exchange_rate_usd_cny", "price_year", "horizon", "horizon_unit", "cycle", "cycle_unit", "cost_discount", "effect_discount", "states", "initial_distribution", "transition_matrix", "strategy_costs", "state_costs", "outcomes_CEA", "outcomes_CUA", "effect_unit", "latest_result", "latest_model", "imported_model"):
        st.session_state.pop(state_key, None)
    st.rerun()
st.sidebar.markdown("<p style='color:#C62828;font-size:0.72rem;white-space:nowrap;margin:0.6rem 0 0;'>Disclaimer: Only used for research purposes</p>", unsafe_allow_html=True)
st.title(tr("title"))
st.caption(tr("subtitle"))

left, right = st.columns([1, 1.65], gap="large")
with left:
    model, run = render_inputs(language, st.session_state.get("imported_model"))

if run:
    errors = validate_model(model)
    if errors:
        with left:
            st.error(tr("model_error"))
            for error in errors:
                st.write(f"• {error}")
    else:
        cycles = round(model["time"]["horizon_years"] / model["time"]["cycle_years"])
        with st.spinner("正在运行 Markov 模型..."):
            trace = run_markov(model["markov"]["initial_distribution"], model["markov"]["transition_matrix"], cycles, model["markov"]["states"])
            outcome_values = None if model["study"]["analysis_type"] == "CMA" else (
                model["outcomes"]["state_utility"] if model["study"]["analysis_type"] == "CUA" else model["outcomes"]["state_effect"])
            common = dict(trace=trace, state_costs=model["costs"]["state_cost_per_cycle"],
                          cycle_years=model["time"]["cycle_years"], cost_discount_rate=model["time"]["cost_discount_rate"],
                          effect_discount_rate=model["time"]["effect_discount_rate"])
            a = evaluate_strategy(initial_cost=model["costs"]["initial_cost"]["A"], strategy_cost_per_cycle=model["costs"]["strategy_cost_per_cycle"]["A"], state_outcomes=None if outcome_values is None else outcome_values["A"], **common)
            b = evaluate_strategy(initial_cost=model["costs"]["initial_cost"]["B"], strategy_cost_per_cycle=model["costs"]["strategy_cost_per_cycle"]["B"], state_outcomes=None if outcome_values is None else outcome_values["B"], **common)
            study = model["study"]
            if study["input_currency"] == study["currency"]:
                conversion_factor = 1.0
            elif study["input_currency"] == "CNY":
                conversion_factor = 1 / study["exchange_rate_usd_cny"]
            else:
                conversion_factor = study["exchange_rate_usd_cny"]
            a = convert_strategy_costs(a, conversion_factor)
            b = convert_strategy_costs(b, conversion_factor)
            st.session_state["latest_result"] = {"trace": trace, "strategy_a": a, "strategy_b": b,
                                                  "incremental": calculate_incremental(a, b, model["study"]["analysis_type"])}
            st.session_state["latest_model"] = model
        with left: st.success(tr("completed"))

with right:
    if "latest_result" not in st.session_state:
        st.info(tr("empty"))
    else:
        result = st.session_state["latest_result"]; saved_model = st.session_state["latest_model"]
        render_results(result, saved_model, language)
        st.subheader(tr("trend"))
        # Set the labels here as well as in charts.py.  This keeps the language
        # correct when an older charts.py file is still present after a web upload.
        chart_cycle_label = "周期" if language == "zh" else "Cycle"
        chart_proportion_label = "患者比例" if language == "zh" else "Patient proportion"
        state_figure = state_chart(result["trace"], tr("state_chart"))
        state_figure.update_layout(
            xaxis_title=chart_cycle_label,
            yaxis_title=chart_proportion_label,
        )
        st.plotly_chart(state_figure, use_container_width=True)
        study = saved_model["study"]
        st.plotly_chart(comparison_chart(result["strategy_a"]["cumulative_costs"], result["strategy_b"]["cumulative_costs"], study["strategy_a"], study["strategy_b"], tr("cost_chart"), f"{tr('cum_cost')} ({study['currency']})", tr("cycle_axis")), use_container_width=True)
        if study["analysis_type"] != "CMA":
            if study["analysis_type"] == "CUA":
                label = "累计 QALY" if language == "zh" else "Cumulative QALY"
            else:
                prefix = "累计 Effect" if language == "zh" else "Cumulative Effect"
                label = f"{prefix} ({saved_model['outcomes']['effect_unit']})"
            outcome_title = label
            st.plotly_chart(comparison_chart(result["strategy_a"]["cumulative_outcomes"], result["strategy_b"]["cumulative_outcomes"], study["strategy_a"], study["strategy_b"], outcome_title, label, tr("cycle_axis")), use_container_width=True)
        st.download_button(tr("export"), result_json(saved_model, result), "health_economics_result.json", "application/json")
        csv_label = "导出结果 CSV" if language == "zh" else "Export results as CSV"
        st.download_button(csv_label, result_csv(saved_model, result), "health_economics_result.csv", "text/csv")
