"""Basic Plotly charts for the result area."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def state_chart(trace: pd.DataFrame, title: str):
    frame = trace.reset_index().melt(id_vars="cycle", var_name="健康状态", value_name="患者比例")
    fig = px.area(frame, x="cycle", y="患者比例", color="健康状态", title=title)
    fig.update_layout(yaxis_tickformat=".0%", legend_title_text="")
    return fig


def comparison_chart(values_a: list[float], values_b: list[float], name_a: str, name_b: str, title: str, y_title: str, x_title: str = "Cycle"):
    cycles = list(range(len(values_a)))
    fig = go.Figure()
    fig.add_scatter(x=cycles, y=values_a, mode="lines+markers", name=name_a)
    fig.add_scatter(x=cycles, y=values_b, mode="lines+markers", name=name_b)
    fig.update_layout(title=title, xaxis_title=x_title, yaxis_title=y_title, legend_title_text="")
    return fig
