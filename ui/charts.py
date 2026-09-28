"""Basic Plotly charts for the result area."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def state_chart(trace: pd.DataFrame, title: str, cycle_title: str = "Cycle",
                proportion_title: str = "Patient proportion", state_title: str = "State"):
    frame = trace.reset_index().melt(
        id_vars="cycle", var_name=state_title, value_name=proportion_title
    )
    fig = px.area(
        frame, x="cycle", y=proportion_title, color=state_title,
        title=title, labels={"cycle": cycle_title, proportion_title: proportion_title,
                             state_title: state_title},
    )
    fig.update_layout(
        xaxis_title=cycle_title,
        yaxis_title=proportion_title,
        yaxis_tickformat=".0%",
        legend_title_text="",
    )
    return fig


def comparison_chart(values_a: list[float], values_b: list[float], name_a: str, name_b: str, title: str, y_title: str, x_title: str = "Cycle"):
    cycles = list(range(len(values_a)))
    fig = go.Figure()
    fig.add_scatter(x=cycles, y=values_a, mode="lines+markers", name=name_a)
    fig.add_scatter(x=cycles, y=values_b, mode="lines+markers", name=name_b)
    fig.update_layout(title=title, xaxis_title=x_title, yaxis_title=y_title, legend_title_text="")
    return fig
