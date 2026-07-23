"""pyecharts-express: plotly-express style API for pyecharts.

Build ECharts visualizations with concise, dataframe-friendly calls.

Example
-------
>>> import pyecharts_express as px
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
from .charts_extra import (
    area,
    bar_3d,
    bar_polar,
    box,
    calendar_heatmap,
    choropleth,
    density_contour,
    funnel_area,
    graph,
    gauge,
    icicle,
    imshow,
    line_3d,
    line_geo,
    line_polar,
    map_choropleth,
    parallel_categories,
    parallel_coordinates,
    sankey,
    scatter_3d,
    scatter_geo,
    scatter_matrix,
    scatter_polar,
    scatter_ternary,
    strip,
    sunburst,
    themeriver,
    treemap,
    violin,
    wordcloud,
)

__all__ = [
    "__version__",
    # core set
    "bar",
    "line",
    "scatter",
    "pie",
    "funnel",
    "boxplot",
    "histogram",
    "density_heatmap",
    "radar",
    # extended (plotly-express coverage)
    "area",
    "funnel_area",
    "box",
    "violin",
    "strip",
    "density_contour",
    "imshow",
    "sunburst",
    "treemap",
    "icicle",
    "bar_polar",
    "line_polar",
    "scatter_polar",
    "map_choropleth",
    "choropleth",
    "scatter_geo",
    "line_geo",
    "parallel_coordinates",
    "parallel_categories",
    "scatter_matrix",
    "sankey",
    "gauge",
    "graph",
    "themeriver",
    "calendar_heatmap",
    "wordcloud",
    # ECharts GL / ternary compatibility
    "scatter_3d",
    "line_3d",
    "bar_3d",
    "scatter_ternary",
]
