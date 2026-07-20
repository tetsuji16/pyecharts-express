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
    reindex_series_for_axis,
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
    log_x: bool = False,
    log_y: bool = False,
    range_x: tuple[Any, Any] | None = None,
    range_y: tuple[Any, Any] | None = None,
) -> tuple[opts.InitOpts, dict[str, Any]]:
    init_opts = build_init_opts(width, height, theme)
    common = dict(
        title=title,
        xaxis_name=xaxis_name,
        yaxis_name=yaxis_name,
        xaxis_type=xaxis_type,
        yaxis_type=yaxis_type,
        log_x=log_x,
        log_y=log_y,
        range_x=range_x,
        range_y=range_y,
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
    orientation: str = "v",
    log_y: bool = False,
    range_y: tuple[Any, Any] | None = None,
    range_x: tuple[Any, Any] | None = None,
    labels: Mapping[str, str] | None = None,
    opacity: float | None = None,
    color_discrete_sequence: Sequence[str] | None = None,
    color_discrete_map: Mapping[str, str] | None = None,
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
    orientation:
        ``"v"`` (vertical, default) or ``"h"`` (horizontal).
    log_y / range_y / range_x:
        Logarithmic axis and axis bounds (plotly ``log_y`` / ``range_*``).
    labels:
        Map of column name -> display name (plotly ``labels``).
    opacity:
        Bar opacity 0–1.
    color_discrete_sequence / color_discrete_map:
        Series color palette / fixed color mapping.
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

    if labels:
        xaxis_name = labels.get(x or "", xaxis_name)
        yaxis_name = labels.get(y, yaxis_name)

    # For horizontal bars pyecharts' reversal_axis() swaps the *data* between
    # axes but keeps the AxisOpts objects in place. Therefore we must NOT pin
    # explicit "category"/"value" types (they would mismatch the swapped data)
    # and we must route log/range/axis-names to the physical axis that ends up
    # carrying the value (x) or category (y) after the reversal.
    if orientation == "h":
        axis_name_x, axis_name_y = yaxis_name, xaxis_name
        axis_type_x, axis_type_y = "value", "category"
        common_log_x, common_log_y = log_y, False
        common_range_x, common_range_y = range_y, range_x
    else:
        axis_name_x, axis_name_y = xaxis_name, yaxis_name
        axis_type_x, axis_type_y = "category", "value"
        common_log_x, common_log_y = False, log_y
        common_range_x, common_range_y = range_x, range_y

    init_opts, common = _common_kwargs(
        width, height, theme, title, axis_name_x, axis_name_y,
        axis_type_x, axis_type_y,
        log_x=common_log_x, log_y=common_log_y,
        range_x=common_range_x, range_y=common_range_y,
    )
    chart = Bar(init_opts=init_opts)
    series = split_by_color(
        df, x, y, color,
        color_discrete_sequence=color_discrete_sequence,
        color_discrete_map=color_discrete_map,
        opacity=opacity,
    )
    # When color splits a categorical x into groups with *different* categories,
    # align every series onto the union of categories so none get dropped.
    if color is not None and x is not None:
        use_xs, aligned = reindex_series_for_axis(series)
        series_iter = [(name, ys, color_val) for name, ys, color_val in aligned]
    else:
        use_xs = series[0][1]
        series_iter = [(name, ys, color_val) for name, _xs, ys, color_val in series]
    chart.add_xaxis([str(v) for v in use_xs])
    for name, ys, color_val in series_iter:
        itemstyle = opts.ItemStyleOpts()
        if color_val:
            itemstyle.opts["color"] = color_val
        if opacity is not None:
            itemstyle.opts["opacity"] = opacity
        chart.add_yaxis(
            name,
            [None if v is None else v for v in ys],
            stack="total" if stack else None,
            itemstyle_opts=itemstyle if (color_val or opacity is not None) else None,
        )
    if orientation == "h":
        chart.reversal_axis()
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
    log_x: bool = False,
    log_y: bool = False,
    range_x: tuple[Any, Any] | None = None,
    range_y: tuple[Any, Any] | None = None,
    labels: Mapping[str, str] | None = None,
    opacity: float | None = None,
    color_discrete_sequence: Sequence[str] | None = None,
    color_discrete_map: Mapping[str, str] | None = None,
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

    if labels:
        xaxis_name = labels.get(x or "", xaxis_name)
        yaxis_name = labels.get(y, yaxis_name)

    init_opts, common = _common_kwargs(
        width, height, theme, title, xaxis_name, yaxis_name, None, None,
        log_x=log_x, log_y=log_y, range_x=range_x, range_y=range_y,
    )
    chart = Line(init_opts=init_opts)
    series = split_by_color(
        df, x, y, color,
        color_discrete_sequence=color_discrete_sequence,
        color_discrete_map=color_discrete_map,
        opacity=opacity,
    )
    if color is not None and x is not None:
        use_xs, aligned = reindex_series_for_axis(series)
        series_iter = [(name, ys, color_val) for name, ys, color_val in aligned]
    else:
        use_xs = series[0][1]
        series_iter = [(name, ys, color_val) for name, _xs, ys, color_val in series]
    chart.add_xaxis(list(use_xs))
    for name, ys, color_val in series_iter:
        itemstyle = opts.ItemStyleOpts()
        if color_val:
            itemstyle.opts["color"] = color_val
        if opacity is not None:
            itemstyle.opts["opacity"] = opacity
        linestyle = opts.LineStyleOpts(color=color_val) if color_val else None
        chart.add_yaxis(
            name,
            [None if v is None else v for v in ys],
            is_smooth=smooth,
            linestyle_opts=linestyle,
            itemstyle_opts=itemstyle if (color_val or opacity is not None) else None,
        )
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
    symbol: str | None = None,
    symbol_sequence: Sequence[str] | None = None,
    log_x: bool = False,
    log_y: bool = False,
    range_x: tuple[Any, Any] | None = None,
    range_y: tuple[Any, Any] | None = None,
    labels: Mapping[str, str] | None = None,
    opacity: float | None = None,
    color_discrete_sequence: Sequence[str] | None = None,
    color_discrete_map: Mapping[str, str] | None = None,
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

    if labels:
        xaxis_name = labels.get(x or "", xaxis_name)
        yaxis_name = labels.get(y, yaxis_name)

    init_opts, common = _common_kwargs(
        width, height, theme, title, xaxis_name, yaxis_name, None, None,
        log_x=log_x, log_y=log_y, range_x=range_x, range_y=range_y,
    )
    chart = Scatter(init_opts=init_opts)
    series = split_by_color(
        df, x, y, color,
        color_discrete_sequence=color_discrete_sequence,
        color_discrete_map=color_discrete_map,
        opacity=opacity,
    )
    chart.add_xaxis(list(series[0][1]))
    sym_iter = iter(symbol_sequence or [])
    for name, _xs, ys, color_val in series:
        sym = symbol or next(sym_iter, None)
        kw: dict[str, Any] = {}
        if color_val or opacity is not None:
            itemstyle = opts.ItemStyleOpts()
            if color_val:
                itemstyle.opts["color"] = color_val
            if opacity is not None:
                itemstyle.opts["opacity"] = opacity
            kw["itemstyle_opts"] = itemstyle
        if size is not None:
            # pyecharts uses a single symbol size per series; use the mean.
            kw["symbol_size"] = int(pd.to_numeric(df[size], errors="coerce").mean())
        if sym:
            kw["symbol"] = sym
        chart.add_yaxis(name, list(ys), **kw)
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
    labels: Mapping[str, str] | None = None,
    opacity: float | None = None,
    color_discrete_sequence: Sequence[str] | None = None,
) -> Pie:
    """Create a pie chart.

    ``data`` may be a ``DataFrame`` (with ``names``/``values`` columns) or a
    ``dict`` mapping label -> value.
    """
    init_opts, _ = _common_kwargs(
        width, height, theme, title, None, None, None, None,
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
    label_map = labels or {}
    raw_labels = [str(v) for v in df[names].tolist()]
    vals = df[values].tolist()
    palette = list(color_discrete_sequence or [])
    pairs = []
    for i, (lab, val) in enumerate(zip(raw_labels, vals)):
        itemstyle = opts.ItemStyleOpts()
        if palette:
            itemstyle.opts["color"] = palette[i % len(palette)]
        if opacity is not None:
            itemstyle.opts["opacity"] = opacity
        item = opts.PieItem(
            name=label_map.get(lab, lab),
            value=val,
            itemstyle_opts=itemstyle if (palette or opacity is not None) else None,
        )
        pairs.append(item)
    radius = ["40%", "70%"] if hole else None
    chart.add(
        "",
        pairs,
        radius=radius,
        rosetype=rose_type,
    )
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
    labels: Mapping[str, str] | None = None,
    opacity: float | None = None,
    color_discrete_sequence: Sequence[str] | None = None,
) -> Funnel:
    """Create a funnel chart."""
    init_opts, _ = _common_kwargs(
        width, height, theme, title, None, None, None, None,
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
    label_map = labels or {}
    raw_labels = [str(v) for v in df[names].tolist()]
    vals = df[values].tolist()
    palette = list(color_discrete_sequence or [])
    pairs = []
    for i, (lab, val) in enumerate(zip(raw_labels, vals)):
        itemstyle = opts.ItemStyleOpts()
        if palette:
            itemstyle.opts["color"] = palette[i % len(palette)]
        if opacity is not None:
            itemstyle.opts["opacity"] = opacity
        item = opts.FunnelItem(
            name=label_map.get(lab, lab),
            value=val,
            itemstyle_opts=itemstyle if (palette or opacity is not None) else None,
        )
        pairs.append(item)
    chart.add(
        "",
        pairs,
        sort_=sort,
    )
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
    log_y: bool = False,
    range_y: tuple[Any, Any] | None = None,
    labels: Mapping[str, str] | None = None,
    opacity: float | None = None,
) -> Boxplot:
    """Create a box plot. Groups by ``x`` and computes quartiles of ``y``."""
    df = normalize_data(data)
    if y is None:
        num_cols = df.select_dtypes(include="number").columns
        y = num_cols[0] if len(num_cols) >= 1 else None
        if y is None:
            raise ValueError("`y` must be specified.")
    ensure_columns(df, y) if x is None else ensure_columns(df, x, y)

    if labels:
        xaxis_name = labels.get(x or "", xaxis_name)
        yaxis_name = labels.get(y, yaxis_name)

    init_opts, common = _common_kwargs(
        width, height, theme, title, xaxis_name, yaxis_name, None, None,
        log_y=log_y, range_y=range_y,
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
    itemstyle = opts.ItemStyleOpts()
    if opacity is not None:
        itemstyle.opts["opacity"] = opacity
    chart.add_yaxis("box", box_data, itemstyle_opts=itemstyle if opacity is not None else None)
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
    log_y: bool = False,
    range_y: tuple[Any, Any] | None = None,
    labels: Mapping[str, str] | None = None,
    opacity: float | None = None,
) -> Bar:
    """Create a histogram of a single numeric column."""
    df = normalize_data(data)
    if x is None:
        num_cols = df.select_dtypes(include="number").columns
        x = num_cols[0] if len(num_cols) >= 1 else None
        if x is None:
            raise ValueError("`x` must be specified.")
    ensure_columns(df, x)

    if labels:
        xaxis_name = labels.get(x, xaxis_name)
        yaxis_name = labels.get("count", yaxis_name)

    vals = pd.to_numeric(df[x], errors="coerce").dropna().to_numpy()
    counts, edges = np.histogram(vals, bins=bins)
    if density:
        counts = (counts / counts.sum() / (edges[1] - edges[0])).round(6)
    centers = [
        round(float((edges[i] + edges[i + 1]) / 2), 4) for i in range(bins)
    ]

    init_opts, common = _common_kwargs(
        width, height, theme, title, xaxis_name or x, yaxis_name or "count", None, None,
        log_y=log_y, range_y=range_y,
    )
    chart = Bar(init_opts=init_opts)
    itemstyle = opts.ItemStyleOpts()
    if opacity is not None:
        itemstyle.opts["opacity"] = opacity
    chart.add_xaxis([str(c) for c in centers])
    chart.add_yaxis("count", counts.tolist(),
                    itemstyle_opts=itemstyle if opacity is not None else None)
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
    labels: Mapping[str, str] | None = None,
) -> HeatMap:
    """Create a 2D histogram heatmap of two numeric columns."""
    df = normalize_data(data)
    ensure_columns(df, x, y)

    if labels:
        xaxis_name = labels.get(x, xaxis_name)
        yaxis_name = labels.get(y, yaxis_name)

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
    labels: Mapping[str, str] | None = None,
    color_discrete_sequence: Sequence[str] | None = None,
    color_discrete_map: Mapping[str, str] | None = None,
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
    # keep original column names for data access; labels only affect display
    label_map = labels or {}
    display_indicators = [label_map.get(ind, ind) for ind in indicators]
    ensure_columns(df, *indicators)

    palette = list(color_discrete_sequence or [])

    def resolve(name: str, idx: int) -> str | None:
        if color_discrete_map and name in color_discrete_map:
            return color_discrete_map[name]
        if palette:
            return palette[idx % len(palette)]
        return None

    init_opts, _ = _common_kwargs(
        width, height, theme, title, None, None, None, None
    )
    chart = Radar(init_opts=init_opts)
    maxes = {ind: float(pd.to_numeric(df[ind], errors="coerce").max() or 1) for ind in indicators}
    indicator_def = [
        opts.RadarIndicatorItem(name=display_indicators[i], max_=maxes[ind] * 1.1)
        for i, ind in enumerate(indicators)
    ]
    chart.add_schema(indicator_def)

    if series is not None:
        ensure_columns(df, series)
        grouped = df.groupby(series, sort=False)
        for idx, (name, group) in enumerate(grouped):
            vals = [
                [float(pd.to_numeric(group[ind], errors="coerce").mean() or 0)]
                for ind in indicators
            ]
            color_val = resolve(str(name), idx)
            chart.add(
                str(name),
                [v[0] for v in vals],
                color=color_val,
            )
    else:
        # One series per row, vectorized over rows.
        data_mat = df[indicators].apply(pd.to_numeric, errors="coerce").fillna(0).to_numpy(dtype=float)
        for i, row_vals in enumerate(data_mat):
            color_val = resolve(f"row {i}", i)
            chart.add(f"row {i}", [list(row_vals)], color=color_val)
    chart.set_global_opts(
        title_opts=opts.TitleOpts(title=title) if title else opts.TitleOpts()
    )
    return chart
