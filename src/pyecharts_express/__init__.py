"""pyecharts-express: plotly-express style API for pyecharts.

Build ECharts visualizations with concise, dataframe-friendly calls.

Example
-------
>>> import pyecharts_express as px
>>> from pyecharts.render import make_snapshot
>>> chart = px.bar(df, x="city", y="population", color="region", title="Populations")
>>> chart.render("chart.html")
"""

from __future__ import annotations

from ._version import __version__
from .charts import (
    bar,
    boxplot,
    density_heatmap,
    funnel,
    histogram,
    line,
    pie,
    radar,
    scatter,
)

__all__ = [
    "__version__",
    "bar",
    "line",
    "scatter",
    "pie",
    "funnel",
    "boxplot",
    "histogram",
    "density_heatmap",
    "radar",
]
