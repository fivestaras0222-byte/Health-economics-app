"""Small, dependency-free interface translation catalogue."""
from __future__ import annotations


TEXT = {
    "zh": {
        "language": "界面语言", "title": "卫生经济学评价分析系统",
        "subtitle": "CMA · CEA · CUA · 基础 Markov 队列模型", "design": "① 研究设计",
        "model": "② 时间与 Markov 模型", "costs": "③ 成本参数",
        "utility": "④ Utility 参数", "effect": "④ Effect 参数", "project": "项目名称",
        "analysis": "评价类型", "strategy_a": "A方案", "strategy_b": "B方案",
        "currency": "货币", "price_year": "价格基年", "horizon": "时间范围",
        "horizon_unit": "时间单位", "cycle": "周期长度", "cycle_unit": "周期单位",
        "cost_discount": "成本折现率", "effect_discount": "效果折现率",
        "states": "健康状态（每行一个）", "state": "状态", "initial": "初始比例",
        "initial_caption": "初始状态比例总和必须为 1。", "matrix_caption": "每行转移概率总和必须为 1。",
        "item": "项目", "initial_cost": "一次性成本", "strategy_cost": "方案周期成本",
        "state_cost": "状态成本 / 周期", "effect_unit": "Effect 单位", "effect_cycle": "Effect / 周期",
        "run": "▶ 运行模型", "summary": "结果摘要", "incremental": "增量结果",
        "total_cost": "总成本", "delta_cost": "Δ Cost（A − B）", "delta": "增量（A − B）",
        "metric": "指标", "trend": "趋势图", "state_chart": "Markov 状态变化",
        "cost_chart": "累计成本趋势", "cycle_axis": "周期", "state_proportion": "患者比例",
        "cum_cost": "累计成本", "cum_qaly": "累计 QALY", "cum_effect": "累计 Effect",
        "model_error": "模型尚未运行，请修正以下问题：", "completed": "模型计算完成",
        "empty": "请在左侧完成输入，然后点击“运行模型”。", "export": "导出结果 JSON",
        "unstable": "ICER 不稳定或不适用：ΔEffect / ΔQALY 接近 0。请结合 ΔCost 和增量结局解读。",
        "not_applicable": "不适用", "years": ["年", "季度", "月"],
    },
    "en": {
        "language": "Language", "title": "Health Economics Evaluation System",
        "subtitle": "CMA · CEA · CUA · Basic Markov cohort model", "design": "① Study design",
        "model": "② Time and Markov model", "costs": "③ Cost parameters",
        "utility": "④ Utility parameters", "effect": "④ Effect parameters", "project": "Project name",
        "analysis": "Analysis type", "strategy_a": "Strategy A", "strategy_b": "Strategy B",
        "currency": "Currency", "price_year": "Price year", "horizon": "Time horizon",
        "horizon_unit": "Time unit", "cycle": "Cycle length", "cycle_unit": "Cycle unit",
        "cost_discount": "Cost discount rate", "effect_discount": "Effect discount rate",
        "states": "Health states (one per line)", "state": "State", "initial": "Initial proportion",
        "initial_caption": "Initial state proportions must sum to 1.", "matrix_caption": "Each transition-probability row must sum to 1.",
        "item": "Item", "initial_cost": "Initial cost", "strategy_cost": "Strategy cost per cycle",
        "state_cost": "State cost per cycle", "effect_unit": "Effect unit", "effect_cycle": "Effect per cycle",
        "run": "▶ Run model", "summary": "Results summary", "incremental": "Incremental results",
        "total_cost": "Total cost", "delta_cost": "Δ Cost (A − B)", "delta": "Incremental (A − B)",
        "metric": "Metric", "trend": "Charts", "state_chart": "Markov state transitions",
        "cost_chart": "Cumulative cost", "cycle_axis": "Cycle", "state_proportion": "Patient proportion",
        "cum_cost": "Cumulative cost", "cum_qaly": "Cumulative QALY", "cum_effect": "Cumulative Effect",
        "model_error": "The model was not run. Please correct the following issues:", "completed": "Model completed",
        "empty": "Complete the inputs on the left, then select Run model.", "export": "Export results as JSON",
        "unstable": "ICER is unstable or not applicable because ΔEffect / ΔQALY is close to zero. Interpret ΔCost and the incremental outcome directly.",
        "not_applicable": "Not applicable", "years": ["Year", "Quarter", "Month"],
    },
}


def t(key: str, language: str):
    return TEXT[language].get(key, key)
