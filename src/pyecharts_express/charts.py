"""High-level chart builders (plotly-express style) for pyecharts.

Every function returns a pyecharts ``Chart`` instance, so you can keep using
the standard pyecharts API afterwards (``.render()``, ``.render_notebook()``,
``.dump_options()``, etc.).
"""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Bar, Boxplot, Funnel, HeatMap, Line, Pie, Radar, Scatter

from .core import (
    apply_common,
    build_init_opts,
    ensure_columns,
    normalize_data,
    split_by_color,
)


def _common_kwargs(
    width: str | None,
    height: str | None,
    theme: str | None,
    title: str | None,
    xaxis_name: str | None,
    yaxis_name: str | None,
    xaxis_type: str | None,
    yaxis_type: str | None,
) -> tuple[opts.InitOpts, dict[str, Any]]:
    init_opts = build_init_opts(width, height, theme)
    common = dict(
        title=title,
        xaxis_name=xaxis_name,
        yaxis_name=yaxis_name,
        xaxis_type=xaxis_type,
        yaxis_type=yaxis_type,
    )
    return init_opts, common


def bar(
    data: Any,
    x: str | None = None,
    y: str | None = None,
    color: str | None = None,
    *,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
    xaxis_name: str | None = None,
    yaxis_name: str | None = None,
    stack: bool = False,
) -> Bar:
    """Create a bar chart.

    Parameters
    ----------
    data:
        ``DataFrame``, ``list[dict]``, or ``dict`` of columns.
    x:
        Column for the categorical axis. If ``None`` and ``color`` is ``None``,
        a positional index is used.
    y:
        Column for bar heights. Required unless ``data`` is a bare dict of one
        series (then it is inferred).
    color:
        Column used to split bars into multiple series (grouped/stacked).
    """
    df = normalize_data(data)
    if y is None:
        # infer single numeric column
        num_cols = df.select_dtypes(include="number").columns
        if len(num_cols) == 1:
            y = num_cols[0]
        else:
            raise ValueError("`y` must be specified (multiple numeric columns found).")
    ensure_columns(df, y) if x is None else ensure_columns(df, x, y)

    init_opts, common = _common_kwargs(
        width, height, theme, title, xaxis_name, yaxis_name, None, None
    )
    chart = Bar(init_opts=init_opts)
    series = split_by_color(df, x, y, color)
    # x axis from the first series
    xs = series[0][1]
    chart.add_xaxis(list(xs))
    for name, _xs, ys in series:
        chart.add_yaxis(name, list(ys), stack="total" if stack else None)
    apply_common(chart, **common)
    return chart


def line(
    data: Any,
    x: str | None = None,
    y: str | None = None,
    color: str | None = None,
    *,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
    xaxis_name: str | None = None,
    yaxis_name: str | None = None,
    smooth: bool = False,
) -> Line:
    """Create a line chart."""
    df = normalize_data(data)
    if y is None:
        num_cols = df.select_dtypes(include="number").columns
        if len(num_cols) == 1:
            y = num_cols[0]
        else:
            raise ValueError("`y` must be specified (multiple numeric columns found).")
    ensure_columns(df, y) if x is None else ensure_columns(df, x, y)

    init_opts, common = _common_kwargs(
        width, height, theme, title, xaxis_name, yaxis_name, None, None
    )
    chart = Line(init_opts=init_opts)
    series = split_by_color(df, x, y, color)
    chart.add_xaxis(list(series[0][1]))
    for name, _xs, ys in series:
        chart.add_yaxis(name, list(ys), is_smooth=smooth)
    apply_common(chart, **common)
    return chart


def scatter(
    data: Any,
    x: str | None = None,
    y: str | None = None,
    color: str | None = None,
    *,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
    xaxis_name: str | None = None,
    yaxis_name: str | None = None,
    size: str | None = None,
) -> Scatter:
    """Create a scatter chart."""
    df = normalize_data(data)
    if y is None:
        num_cols = df.select_dtypes(include="number").columns
        if len(num_cols) >= 1:
            y = num_cols[-1]
        else:
            raise ValueError("`y` must be specified.")
    ensure_columns(df, y) if x is None else ensure_columns(df, x, y)

    init_opts, common = _common_kwargs(
        width, height, theme, title, xaxis_name, yaxis_name, None, None
    )
    chart = Scatter(init_opts=init_opts)
    series = split_by_color(df, x, y, color)
    chart.add_xaxis(list(series[0][1]))
    for name, _xs, ys in series:
        chart.add_yaxis(name, list(ys))
    apply_common(chart, **common)
    return chart


def pie(
    data: Any,
    names: str | None = None,
    values: str | None = None,
    *,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
    hole: bool = False,
    rose_type: str | None = None,
) -> Pie:
    """Create a pie chart.

    ``data`` may be a ``DataFrame`` (with ``names``/``values`` columns) or a
    ``dict`` mapping label -> value.
    """
    init_opts, _ = _common_kwargs(
        width, height, theme, title, None, None, None, None
    )
    chart = Pie(init_opts=init_opts)
    df = normalize_data(data)
    if names is None or values is None:
        # infer: object/category column + numeric column
        obj_cols = df.select_dtypes(include=["object", "category"]).columns
        num_cols = df.select_dtypes(include="number").columns
        if len(obj_cols) >= 1 and len(num_cols) >= 1:
            names, values = obj_cols[0], num_cols[0]
        else:
            raise ValueError("`names` and `values` must be specified.")
    ensure_columns(df, names, values)
    pairs = list(zip(df[names].astype(str).tolist(), df[values].tolist()))
    radius = ["40%", "70%"] if hole else None
    chart.add("", pairs, radius=radius, rosetype=rose_type)
    chart.set_global_opts(
        title_opts=opts.TitleOpts(title=title) if title else opts.TitleOpts(),
        legend_opts=opts.LegendOpts(orient="vertical", pos_left="left"),
    )
    return chart


def funnel(
    data: Any,
    names: str | None = None,
    values: str | None = None,
    *,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
    sort: str = "descending",
) -> Funnel:
    """Create a funnel chart."""
    init_opts, _ = _common_kwargs(
        width, height, theme, title, None, None, None, None
    )
    chart = Funnel(init_opts=init_opts)
    df = normalize_data(data)
    if names is None or values is None:
        obj_cols = df.select_dtypes(include=["object", "category"]).columns
        num_cols = df.select_dtypes(include="number").columns
        if len(obj_cols) >= 1 and len(num_cols) >= 1:
            names, values = obj_cols[0], num_cols[0]
        else:
            raise ValueError("`names` and `values` must be specified.")
    ensure_columns(df, names, values)
    pairs = list(zip(df[names].astype(str).tolist(), df[values].tolist()))
    chart.add("", pairs, sort_=sort)
    chart.set_global_opts(
        title_opts=opts.TitleOpts(title=title) if title else opts.TitleOpts()
    )
    return chart


def boxplot(
    data: Any,
    x: str | None = None,
    y: str | None = None,
    *,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
    xaxis_name: str | None = None,
    yaxis_name: str | None = None,
) -> Boxplot:
    """Create a box plot. Groups by ``x`` and computes quartiles of ``y``."""
    df = normalize_data(data)
    if y is None:
        num_cols = df.select_dtypes(include="number").columns
        y = num_cols[0] if len(num_cols) >= 1 else None
        if y is None:
            raise ValueError("`y` must be specified.")
    ensure_columns(df, y) if x is None else ensure_columns(df, x, y)

    init_opts, common = _common_kwargs(
        width, height, theme, title, xaxis_name, yaxis_name, None, None
    )
    chart = Boxplot(init_opts=init_opts)
    ynum = pd.to_numeric(df[y], errors="coerce")
    if x is None:
        categories = ["data"]
        groups = [("data", ynum)]
    else:
        # Keep original category order (first appearance), include NaN as its
        # own category instead of silently dropping it.
        cat_cols = df[x].astype("string")
        order = list(dict.fromkeys(cat_cols.tolist()))
        categories = [str(c) for c in order]
        groups = [
            (str(c), ynum[cat_cols == c] if pd.notna(c) else ynum[cat_cols.isna()])
            for c in order
        ]

    box_data: list[list[float]] = []
    for _cat, vals in groups:
        vals = vals.dropna()
        if len(vals) == 0:
            box_data.append([0.0, 0.0, 0.0, 0.0, 0.0])
            continue
        q1, median, q3 = np.percentile(vals, [25, 50, 75])
        iqr = q3 - q1
        lo = max(float(vals.min()), q1 - 1.5 * iqr)
        hi = min(float(vals.max()), q3 + 1.5 * iqr)
        box_data.append([lo, float(q1), float(median), float(q3), hi])

    chart.add_xaxis(categories)
    chart.add_yaxis("box", box_data)
    apply_common(chart, **common)
    return chart


def histogram(
    data: Any,
    x: str | None = None,
    *,
    bins: int = 20,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
    xaxis_name: str | None = None,
    yaxis_name: str | None = None,
    density: bool = False,
) -> Bar:
    """Create a histogram of a single numeric column."""
    df = normalize_data(data)
    if x is None:
        num_cols = df.select_dtypes(include="number").columns
        x = num_cols[0] if len(num_cols) >= 1 else None
        if x is None:
            raise ValueError("`x` must be specified.")
    ensure_columns(df, x)
    vals = pd.to_numeric(df[x], errors="coerce").dropna().to_numpy()
    counts, edges = np.histogram(vals, bins=bins)
    if density:
        counts = (counts / counts.sum() / (edges[1] - edges[0])).round(6)
    centers = [
        round(float((edges[i] + edges[i + 1]) / 2), 4) for i in range(bins)
    ]

    init_opts, common = _common_kwargs(
        width, height, theme, title, xaxis_name or x, yaxis_name or "count", None, None
    )
    chart = Bar(init_opts=init_opts)
    chart.add_xaxis([str(c) for c in centers])
    chart.add_yaxis("count", counts.tolist())
    apply_common(chart, **common)
    return chart


def density_heatmap(
    data: Any,
    x: str,
    y: str,
    *,
    bins: int = 20,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
    xaxis_name: str | None = None,
    yaxis_name: str | None = None,
) -> HeatMap:
    """Create a 2D histogram heatmap of two numeric columns."""
    df = normalize_data(data)
    ensure_columns(df, x, y)
    xv = pd.to_numeric(df[x], errors="coerce").to_numpy()
    yv = pd.to_numeric(df[y], errors="coerce").to_numpy()
    mask = ~(np.isnan(xv) | np.isnan(yv))
    xv, yv = xv[mask], yv[mask]
    if len(xv) == 0:
        raise ValueError("No valid (x, y) pairs after dropping NaNs.")

    counts, xedges, yedges = np.histogram2d(xv, yv, bins=bins)
    x_centers = [round(float((xedges[i] + xedges[i + 1]) / 2), 4) for i in range(bins)]
    y_centers = [round(float((yedges[i] + yedges[i + 1]) / 2), 4) for i in range(bins)]

    init_opts, _ = _common_kwargs(
        width, height, theme, title, xaxis_name or x, yaxis_name or y, None, None
    )
    chart = HeatMap(init_opts=init_opts)
    chart.add_xaxis([str(c) for c in x_centers])
    value_list = [[i, j, int(counts[i, j])] for j in range(bins) for i in range(bins)]
    chart.add_yaxis("density", [str(c) for c in y_centers], value_list)
    chart.set_global_opts(
        visualmap_opts=opts.VisualMapOpts(min_=0, max_=int(round(counts.max())) or 1),
        title_opts=opts.TitleOpts(title=title) if title else opts.TitleOpts(),
        xaxis_opts=opts.AxisOpts(name=xaxis_name or x),
        yaxis_opts=opts.AxisOpts(name=yaxis_name or y),
    )
    return chart


def radar(
    data: Any,
    indicators: list[str] | None = None,
    *,
    series: str | None = None,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
) -> Radar:
    """Create a radar chart.

    ``indicators`` are the numeric axes. Each row becomes one radar series,
    optionally grouped by ``series`` column. If no ``series`` column, each row
    is labeled by its index.
    """
    df = normalize_data(data)
    if indicators is None:
        indicators = list(df.select_dtypes(include="number").columns)
    if not indicators:
        raise ValueError("No numeric indicator columns found.")
    ensure_columns(df, *indicators)

    init_opts, _ = _common_kwargs(
        width, height, theme, title, None, None, None, None
    )
    chart = Radar(init_opts=init_opts)
    maxes = {ind: float(pd.to_numeric(df[ind], errors="coerce").max() or 1) for ind in indicators}
    indicator_def = [opts.RadarIndicatorItem(name=ind, max_=maxes[ind] * 1.1) for ind in indicators]
    chart.add_schema(indicator_def)

    if series is not None:
        ensure_columns(df, series)
        grouped = df.groupby(series, sort=False)
        for name, group in grouped:
            vals = [
                [float(pd.to_numeric(group[ind], errors="coerce").mean() or 0)]
                for ind in indicators
            ]
            # pyecharts expects one row per series: [[v1, v2, ...]]
            chart.add(str(name), [v[0] for v in vals])
    else:
        # One series per row, vectorized over rows.
        data_mat = df[indicators].apply(pd.to_numeric, errors="coerce").fillna(0).to_numpy(dtype=float)
        for i, row_vals in enumerate(data_mat):
            chart.add(f"row {i}", [list(row_vals)])
    chart.set_global_opts(
        title_opts=opts.TitleOpts(title=title) if title else opts.TitleOpts()
    )
    return chart
