"""Additional chart builders covering the full plotly-express surface.

These map plotly-express function names onto native ECharts series and
coordinate-system options. A pyecharts chart class is used when one exists;
newer ECharts options such as axis jitter are configured through pyecharts'
generic option objects. Features that require an ECharts ``custom`` series
(violin, density contour, ternary) deliberately remain unsupported.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import (
    Bar3D,
    Boxplot,
    Calendar,
    Funnel,
    Gauge,
    Geo,
    Graph,
    Grid,
    HeatMap,
    Line,
    Line3D,
    Map,
    Parallel,
    Polar,
    Sankey,
    Scatter,
    Scatter3D,
    Sunburst,
    ThemeRiver,
    Tree,
    TreeMap,
    WordCloud,
)

from .core import (
    apply_common,
    build_hierarchy,
    build_init_opts,
    ensure_columns,
    normalize_data,
    split_by_color,
)
from .charts import _common_kwargs


def _common(title, width, height, theme):
    init_opts = build_init_opts(width, height, theme)
    title_opts = opts.TitleOpts(title=title) if title else opts.TitleOpts()
    return init_opts, title_opts


def area(
    data: Any,
    x: str | None = None,
    y: str | None = None,
    color: str | None = None,
    *,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
    stack: bool = False,
    xaxis_name: str | None = None,
    yaxis_name: str | None = None,
    log_x: bool = False,
    log_y: bool = False,
    range_x: tuple[Any, Any] | None = None,
    range_y: tuple[Any, Any] | None = None,
    labels: Mapping[str, str] | None = None,
    opacity: float | None = None,
    color_discrete_sequence: Sequence[str] | None = None,
    color_discrete_map: Mapping[str, str] | None = None,
) -> Line:
    """Stacked/filled area chart (plotly ``px.area``)."""
    df = normalize_data(data)
    if y is None:
        num = df.select_dtypes(include="number").columns
        y = num[0] if len(num) else None
        if y is None:
            raise ValueError("`y` must be specified.")
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
    chart.add_xaxis(list(series[0][1]))
    for name, _xs, ys, color_val in series:
        itemstyle = opts.ItemStyleOpts()
        if color_val:
            itemstyle.opts["color"] = color_val
        if opacity is not None:
            itemstyle.opts["opacity"] = opacity
        chart.add_yaxis(
            name,
            list(ys),
            stack="total" if stack else None,
            areastyle_opts=opts.AreaStyleOpts(opacity=0.4),
            itemstyle_opts=itemstyle if (color_val or opacity is not None) else None,
            linestyle_opts=opts.LineStyleOpts(color=color_val) if color_val else None,
        )
    apply_common(chart, **common)
    return chart


def funnel_area(
    data: Any,
    names: str | None = None,
    values: str | None = None,
    *,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
) -> Funnel:
    """Area-style funnel (plotly ``px.funnel_area``)."""
    init_opts, _ = _common(title, width, height, theme)
    chart = Funnel(init_opts=init_opts)
    df = normalize_data(data)
    if names is None or values is None:
        obj = df.select_dtypes(include="object").columns
        num = df.select_dtypes(include="number").columns
        names, values = obj[0], num[0]
    ensure_columns(df, names, values)
    pairs = list(zip(df[names].astype(str).tolist(), df[values].tolist()))
    chart.add(
        "",
        pairs,
        sort_="descending",
        label_opts=opts.LabelOpts(position="inside"),
        tooltip_opts=opts.TooltipOpts(trigger="item", formatter="{b}: {c}"),
    )
    chart.set_global_opts(
        title_opts=opts.TitleOpts(title=title) if title else opts.TitleOpts()
    )
    return chart


def box(df: Any, x: str | None = None, y: str | None = None, **kw) -> Boxplot:
    """Alias of :func:`boxplot` (plotly ``px.box`` naming)."""
    from .charts import boxplot

    return boxplot(df, x=x, y=y, **kw)


def violin(*args, **kwargs):
    """Not supported — pyecharts has no violin plot equivalent."""
    raise NotImplementedError(
        "pyecharts has no violin plot. Consider `px.box()` as an alternative, "
        "or use plotly-express directly for violin charts."
    )


def strip(
    data: Any,
    x: str | None = None,
    y: str | None = None,
    color: str | None = None,
    *,
    orientation: str | None = None,
    stripmode: str = "group",
    jitter: float = 20,
    jitter_overlap: bool = False,
    jitter_margin: float | None = None,
    symbol: str = "circle",
    symbol_size: float = 10,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
    xaxis_name: str | None = None,
    yaxis_name: str | None = None,
    log_x: bool = False,
    log_y: bool = False,
    range_x: tuple[Any, Any] | None = None,
    range_y: tuple[Any, Any] | None = None,
    labels: Mapping[str, str] | None = None,
    category_orders: Mapping[str, Sequence[Any]] | None = None,
    opacity: float | None = None,
    color_discrete_sequence: Sequence[str] | None = None,
    color_discrete_map: Mapping[str, str] | None = None,
) -> Scatter:
    """Create a strip plot using ECharts 6 native axis jitter.

    No point offsets are calculated by this wrapper. Marks are ordinary
    ECharts ``scatter`` data and ECharts performs the jitter layout from the
    category axis' ``jitter``, ``jitterOverlap`` and ``jitterMargin`` options.
    ``stripmode`` is accepted for Plotly Express compatibility; ECharts keeps
    color groups as separate series and applies its native collision layout
    for both modes.
    """
    if orientation not in (None, "v", "h"):
        raise ValueError("`orientation` must be 'v', 'h', or None.")
    if stripmode not in ("group", "overlay"):
        raise ValueError("`stripmode` must be 'group' or 'overlay'.")
    if jitter < 0:
        raise ValueError("`jitter` must be non-negative.")
    if symbol_size <= 0:
        raise ValueError("`symbol_size` must be positive.")

    df = normalize_data(data)
    if x is None and y is None:
        numeric = list(df.select_dtypes(include="number").columns)
        if not numeric:
            raise ValueError("At least one of `x` or `y` must be specified.")
        y = str(numeric[0])
    ensure_columns(df, *[name for name in (x, y, color) if name is not None])

    if orientation is None:
        if x is None:
            orientation = "v"
        elif y is None:
            orientation = "h"
        else:
            x_numeric = pd.api.types.is_numeric_dtype(df[x])
            y_numeric = pd.api.types.is_numeric_dtype(df[y])
            orientation = "h" if x_numeric and not y_numeric else "v"

    vertical = orientation == "v"
    category_col = x if vertical else y
    value_col = y if vertical else x
    if value_col is None:
        raise ValueError(
            f"`{'y' if vertical else 'x'}` is required for orientation={orientation!r}."
        )

    label_map = labels or {}
    xaxis_name = label_map.get(x or "", xaxis_name or x or "")
    yaxis_name = label_map.get(y or "", yaxis_name or y or "")

    if category_col is None:
        categories: list[Any] = [""]
    else:
        configured = (category_orders or {}).get(category_col)
        observed = list(dict.fromkeys(df[category_col].dropna().tolist()))
        if configured is None:
            categories = observed
        else:
            configured_list = list(configured)
            categories = configured_list + [
                value for value in observed if value not in configured_list
            ]

    init_opts, _ = _common(title, width, height, theme)
    chart = Scatter(init_opts=init_opts)
    chart.add_xaxis(categories if vertical else [])

    palette = list(color_discrete_sequence or [])

    def resolve_color(name: str, index: int) -> str | None:
        if color_discrete_map and name in color_discrete_map:
            return color_discrete_map[name]
        if palette:
            return palette[index % len(palette)]
        return None

    groups = (
        [
            (str(name), group)
            for name, group in df[df[color].notna()].groupby(color, sort=False)
        ]
        if color is not None
        else [(str(value_col), df)]
    )
    for index, (name, group) in enumerate(groups):
        category_values = (
            group[category_col].tolist()
            if category_col is not None
            else [""] * len(group)
        )
        numeric_values = pd.to_numeric(group[value_col], errors="coerce").tolist()
        points = (
            list(zip(category_values, numeric_values))
            if vertical
            else list(zip(numeric_values, category_values))
        )
        color_value = resolve_color(name, index)
        itemstyle = opts.ItemStyleOpts(color=color_value, opacity=opacity)
        chart.add_yaxis(
            name,
            points,
            symbol=symbol,
            symbol_size=symbol_size,
            itemstyle_opts=itemstyle if (color_value or opacity is not None) else None,
            label_opts=opts.LabelOpts(is_show=False),
        )

    xaxis_opts = opts.AxisOpts(
        type_="log" if log_x else ("category" if vertical else "value"),
        name=xaxis_name,
        min_=range_x[0] if range_x else None,
        max_=range_x[1] if range_x else None,
        jitter=jitter if vertical else None,
        is_jitter_overlap=jitter_overlap if vertical else None,
        jitter_margin=jitter_margin if vertical else None,
    )
    yaxis_opts = opts.AxisOpts(
        type_="log" if log_y else ("value" if vertical else "category"),
        name=yaxis_name,
        min_=range_y[0] if range_y else None,
        max_=range_y[1] if range_y else None,
        jitter=jitter if not vertical else None,
        is_jitter_overlap=jitter_overlap if not vertical else None,
        jitter_margin=jitter_margin if not vertical else None,
    )
    if not vertical:
        yaxis_opts.opts["data"] = categories
    chart.set_global_opts(
        title_opts=opts.TitleOpts(title=title) if title else opts.TitleOpts(),
        xaxis_opts=xaxis_opts,
        yaxis_opts=yaxis_opts,
        tooltip_opts=opts.TooltipOpts(trigger="item"),
    )
    return chart


def density_contour(*args, **kwargs):
    """Unsupported without a custom renderer: ECharts has no contour series."""
    raise NotImplementedError(
        "ECharts has no native 2D contour series. A custom series would violate "
        "this package's native-ECharts-only policy; use `px.density_heatmap()`."
    )


def imshow(
    img: Any,
    *,
    x: Sequence[Any] | None = None,
    y: Sequence[Any] | None = None,
    zmin: float | None = None,
    zmax: float | None = None,
    origin: str = "upper",
    color_continuous_scale: Sequence[str] | None = None,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
    labels: Mapping[str, str] | None = None,
    text_auto: bool = False,
) -> HeatMap:
    """Display a two-dimensional scalar matrix as an ECharts heatmap.

    This is a direct wrapper over ECharts ``heatmap`` series and
    ``visualMap``. RGB/RGBA image rasterization is intentionally not emulated
    because ECharts does not expose it as a heatmap-series API.
    """
    if origin not in ("upper", "lower"):
        raise ValueError("`origin` must be 'upper' or 'lower'.")

    if isinstance(img, pd.DataFrame):
        matrix = img.to_numpy()
        x_values = list(img.columns) if x is None else list(x)
        y_values = list(img.index) if y is None else list(y)
    else:
        matrix = np.asarray(img)
        if matrix.ndim != 2:
            raise ValueError("`img` must be a two-dimensional scalar matrix.")
        x_values = list(range(matrix.shape[1])) if x is None else list(x)
        y_values = list(range(matrix.shape[0])) if y is None else list(y)

    if matrix.ndim != 2:
        raise ValueError("`img` must be a two-dimensional scalar matrix.")
    if len(x_values) != matrix.shape[1] or len(y_values) != matrix.shape[0]:
        raise ValueError("`x` and `y` lengths must match the matrix dimensions.")

    numeric = np.asarray(matrix, dtype=float)
    finite = numeric[np.isfinite(numeric)]
    if finite.size == 0:
        raise ValueError("`img` must contain at least one finite numeric value.")
    visual_min = float(finite.min()) if zmin is None else float(zmin)
    visual_max = float(finite.max()) if zmax is None else float(zmax)
    if visual_min == visual_max:
        visual_max = visual_min + 1.0

    values = [
        [
            column,
            row,
            None
            if not np.isfinite(numeric[row, column])
            else float(numeric[row, column]),
        ]
        for row in range(matrix.shape[0])
        for column in range(matrix.shape[1])
    ]
    init_opts, _ = _common(title, width, height, theme)
    chart = HeatMap(init_opts=init_opts)
    chart.add_xaxis(x_values)
    chart.add_yaxis(
        "",
        y_values,
        values,
        label_opts=opts.LabelOpts(is_show=text_auto, position="inside"),
    )
    label_map = labels or {}
    chart.set_global_opts(
        title_opts=opts.TitleOpts(title=title) if title else opts.TitleOpts(),
        xaxis_opts=opts.AxisOpts(type_="category", name=label_map.get("x", "")),
        yaxis_opts=opts.AxisOpts(
            type_="category",
            name=label_map.get("y", ""),
            is_inverse=origin == "upper",
        ),
        visualmap_opts=opts.VisualMapOpts(
            min_=visual_min,
            max_=visual_max,
            range_color=(
                list(color_continuous_scale) if color_continuous_scale else None
            ),
        ),
        tooltip_opts=opts.TooltipOpts(trigger="item"),
    )
    return chart


def sunburst(
    data: Any,
    path: list[str] | None = None,
    names: str | None = None,
    parents: str | None = None,
    values: str | None = None,
    *,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
    labels: Mapping[str, str] | None = None,
    color_discrete_sequence: Sequence[str] | None = None,
) -> Sunburst:
    """Sunburst chart (plotly ``px.sunburst``)."""
    df = normalize_data(data)
    init_opts, _ = _common(title, width, height, theme)
    chart = Sunburst(init_opts=init_opts)
    hierarchy = build_hierarchy(df, path, names, parents, values)
    if labels:
        hierarchy = _apply_labels(hierarchy, labels)
    chart.add("", hierarchy)
    chart.set_global_opts(
        title_opts=opts.TitleOpts(title=title) if title else opts.TitleOpts()
    )
    return chart


def _apply_labels(hierarchy: list[dict], labels: Mapping[str, str]) -> list[dict]:
    """Recursively rename node ``name`` fields using a column->label map."""
    out = []
    for node in hierarchy:
        new_node = dict(node)
        if new_node.get("name") in labels:
            new_node["name"] = labels[new_node["name"]]
        if "children" in new_node:
            new_node["children"] = _apply_labels(new_node["children"], labels)
        out.append(new_node)
    return out


def treemap(
    data: Any,
    path: list[str] | None = None,
    names: str | None = None,
    parents: str | None = None,
    values: str | None = None,
    *,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
    labels: Mapping[str, str] | None = None,
    color_discrete_sequence: Sequence[str] | None = None,
) -> TreeMap:
    """Treemap chart (plotly ``px.treemap``)."""
    df = normalize_data(data)
    init_opts, _ = _common(title, width, height, theme)
    chart = TreeMap(init_opts=init_opts)
    hierarchy = build_hierarchy(df, path, names, parents, values)
    if labels:
        hierarchy = _apply_labels(hierarchy, labels)
    chart.add("", hierarchy)
    chart.set_global_opts(
        title_opts=opts.TitleOpts(title=title) if title else opts.TitleOpts()
    )
    return chart


def icicle(
    data: Any,
    path: list[str] | None = None,
    names: str | None = None,
    parents: str | None = None,
    values: str | None = None,
    *,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
    labels: Mapping[str, str] | None = None,
    color_discrete_sequence: Sequence[str] | None = None,
) -> Tree:
    """Icicle chart (plotly ``px.icicle``) via pyecharts Tree."""
    df = normalize_data(data)
    init_opts, _ = _common(title, width, height, theme)
    chart = Tree(init_opts=init_opts)
    hierarchy = build_hierarchy(df, path, names, parents, values)
    if labels:
        hierarchy = _apply_labels(hierarchy, labels)
    chart.add(
        "",
        hierarchy,
        layout="orthogonal",
        orient="LR",
        symbol="rect",
    )
    chart.set_global_opts(
        title_opts=opts.TitleOpts(title=title) if title else opts.TitleOpts()
    )
    return chart


def bar_polar(
    data: Any,
    theta: str,
    r: str,
    color: str | None = None,
    *,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
    stack: bool = False,
) -> Polar:
    """Polar bar chart (plotly ``px.bar_polar``)."""
    df = normalize_data(data)
    ensure_columns(df, theta, r)
    init_opts, _ = _common(title, width, height, theme)
    chart = Polar(init_opts=init_opts)
    chart.add_schema(
        angleaxis_opts=opts.AngleAxisOpts(data=df[theta].astype(str).tolist()),
        radiusaxis_opts=opts.RadiusAxisOpts(),
    )
    series = split_by_color(df, None, r, color)
    for name, _xs, ys, color_val in series:
        chart.add(name, list(ys), type_="bar", stack="t" if stack else None,
                  itemstyle_opts=opts.ItemStyleOpts(color=color_val) if color_val else None)
    chart.set_global_opts(
        title_opts=opts.TitleOpts(title=title) if title else opts.TitleOpts()
    )
    return chart


def line_polar(
    data: Any,
    theta: str,
    r: str,
    color: str | None = None,
    *,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
) -> Polar:
    """Polar line chart (plotly ``px.line_polar``)."""
    df = normalize_data(data)
    ensure_columns(df, theta, r)
    init_opts, _ = _common(title, width, height, theme)
    chart = Polar(init_opts=init_opts)
    chart.add_schema(
        angleaxis_opts=opts.AngleAxisOpts(data=df[theta].astype(str).tolist()),
        radiusaxis_opts=opts.RadiusAxisOpts(),
    )
    series = split_by_color(df, None, r, color)
    for name, _xs, ys, color_val in series:
        chart.add(name, list(ys), type_="line",
                  itemstyle_opts=opts.ItemStyleOpts(color=color_val) if color_val else None)
    chart.set_global_opts(
        title_opts=opts.TitleOpts(title=title) if title else opts.TitleOpts()
    )
    return chart


def scatter_polar(
    data: Any,
    theta: str,
    r: str,
    color: str | None = None,
    *,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
) -> Polar:
    """Polar scatter chart (plotly ``px.scatter_polar``)."""
    df = normalize_data(data)
    ensure_columns(df, theta, r)
    init_opts, _ = _common(title, width, height, theme)
    chart = Polar(init_opts=init_opts)
    chart.add_schema(
        angleaxis_opts=opts.AngleAxisOpts(data=df[theta].astype(str).tolist()),
        radiusaxis_opts=opts.RadiusAxisOpts(),
    )
    series = split_by_color(df, None, r, color)
    for name, _xs, ys, color_val in series:
        chart.add(name, list(ys), type_="scatter",
                  itemstyle_opts=opts.ItemStyleOpts(color=color_val) if color_val else None)
    chart.set_global_opts(
        title_opts=opts.TitleOpts(title=title) if title else opts.TitleOpts()
    )
    return chart


def map_choropleth(
    data: Any,
    names: str,
    values: str,
    *,
    maptype: str = "china",
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
) -> Map:
    """Choropleth / filled map (plotly ``px.choropleth``).

    ``maptype`` selects the pyecharts map registry (e.g. ``"china"``,
    ``"world"``, ``"Japan"``, or a province name).
    """
    df = normalize_data(data)
    ensure_columns(df, names, values)
    init_opts, _ = _common(title, width, height, theme)
    chart = Map(init_opts=init_opts)
    pairs = list(zip(df[names].astype(str).tolist(), df[values].tolist()))
    vmin = float(df[values].min())
    vmax = float(df[values].max())
    if vmax == vmin:
        # Degenerate visualMap (all values equal) breaks ECharts rendering.
        vmax = vmin + 1.0
    chart.add("", pairs, maptype=maptype)
    chart.set_global_opts(
        title_opts=opts.TitleOpts(title=title) if title else opts.TitleOpts(),
        visualmap_opts=opts.VisualMapOpts(min_=vmin, max_=vmax),
    )
    return chart


# alias
choropleth = map_choropleth


def scatter_geo(
    data: Any,
    lon: str,
    lat: str,
    *,
    maptype: str = "china",
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
) -> Geo:
    """Geo scatter plot (plotly ``px.scatter_geo``)."""
    df = normalize_data(data)
    ensure_columns(df, lon, lat)
    init_opts, _ = _common(title, width, height, theme)
    chart = Geo(init_opts=init_opts)
    chart.add_schema(maptype=maptype)
    names = [str(i) for i in range(len(df))]
    lons = df[lon].to_numpy(dtype=float)
    lats = df[lat].to_numpy(dtype=float)
    for name, lo, la in zip(names, lons, lats):
        chart.add_coordinate(name, float(lo), float(la))
    pairs = [(name, 1) for name in names]
    chart.add("", pairs, type_="scatter")
    chart.set_global_opts(
        title_opts=opts.TitleOpts(title=title) if title else opts.TitleOpts(),
        visualmap_opts=opts.VisualMapOpts(max_=1),
    )
    return chart


def line_geo(
    data: Any,
    lon: str,
    lat: str,
    *,
    maptype: str = "china",
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
) -> Geo:
    """Geo line plot (plotly ``px.line_geo``)."""
    df = normalize_data(data)
    ensure_columns(df, lon, lat)
    init_opts, _ = _common(title, width, height, theme)
    chart = Geo(init_opts=init_opts)
    chart.add_schema(maptype=maptype)
    names = [str(i) for i in range(len(df))]
    lons = df[lon].to_numpy(dtype=float)
    lats = df[lat].to_numpy(dtype=float)
    for name, lo, la in zip(names, lons, lats):
        chart.add_coordinate(name, float(lo), float(la))
    pairs = [(name, 1) for name in names]
    chart.add("", pairs, type_="lines", linestyle_opts=opts.LineStyleOpts(width=2))
    chart.set_global_opts(
        title_opts=opts.TitleOpts(title=title) if title else opts.TitleOpts()
    )
    return chart


def parallel_coordinates(
    data: Any,
    dimensions: list[str] | None = None,
    color: str | None = None,
    *,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
) -> Parallel:
    """Parallel coordinates plot (plotly ``px.parallel_coordinates``)."""
    df = normalize_data(data)
    if dimensions is None:
        dimensions = list(df.select_dtypes(include="number").columns)
    ensure_columns(df, *dimensions)
    init_opts, _ = _common(title, width, height, theme)
    chart = Parallel(init_opts=init_opts)
    schema = [
        opts.ParallelAxisOpts(dim=i, name=col, min_=float(df[col].min()), max_=float(df[col].max()))
        for i, col in enumerate(dimensions)
    ]
    chart.add_schema(schema)
    if color is not None and color in df.columns:
        for name, group in df.groupby(color, sort=False):
            chart.add(str(name), group[dimensions].values.tolist())
    else:
        chart.add("data", df[dimensions].values.tolist())
    chart.set_global_opts(
        title_opts=opts.TitleOpts(title=title) if title else opts.TitleOpts()
    )
    return chart


def parallel_categories(
    data: Any,
    dimensions: list[str] | None = None,
    color: str | None = None,
    *,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
) -> Parallel:
    """Parallel categories plot (plotly ``px.parallel_categories``)."""
    df = normalize_data(data)
    if dimensions is None:
        dimensions = list(df.columns)
    ensure_columns(df, *dimensions)
    init_opts, _ = _common(title, width, height, theme)
    chart = Parallel(init_opts=init_opts)
    schema = [
        opts.ParallelAxisOpts(
            dim=i, name=col, data=df[col].astype(str).unique().tolist()
        )
        for i, col in enumerate(dimensions)
    ]
    chart.add_schema(schema)
    if color is not None and color in df.columns:
        for name, group in df.groupby(color, sort=False):
            chart.add(str(name), group[dimensions].astype(str).values.tolist())
    else:
        chart.add("data", df[dimensions].astype(str).values.tolist())
    chart.set_global_opts(
        title_opts=opts.TitleOpts(title=title) if title else opts.TitleOpts()
    )
    return chart


def scatter_matrix(
    data: Any,
    dimensions: list[str] | None = None,
    color: str | None = None,
    *,
    title: str | None = None,
    width: str = "900px",
    height: str = "900px",
    theme: str | None = None,
) -> Grid:
    """Scatter plot matrix / SPLOM (plotly ``px.scatter_matrix``)."""
    df = normalize_data(data)
    if dimensions is None:
        dimensions = list(df.select_dtypes(include="number").columns)
    ensure_columns(df, *dimensions)
    init_opts, _ = _common(title, width, height, theme)
    grid = Grid(init_opts=init_opts)
    n = len(dimensions)
    cell = 100.0 / n
    for i, yi in enumerate(dimensions):
        for j, xi in enumerate(dimensions):
            c = Scatter()
            xs = df[xi].tolist()
            ys = df[yi].tolist()
            c.add_xaxis([str(v) for v in xs])
            c.add_yaxis(yi, ys)
            c.set_global_opts(
                xaxis_opts=opts.AxisOpts(name=xi, is_show=(i == n - 1)),
                yaxis_opts=opts.AxisOpts(name=yi, is_show=(j == 0)),
            )
            left = f"{j * cell}%"
            top = f"{i * cell}%"
            grid.add(c, grid_opts=opts.GridOpts(pos_left=left, pos_top=top, width=f"{cell}%", height=f"{cell}%"))
    return grid


def sankey(
    data: Any,
    source: str | None = None,
    target: str | None = None,
    values: str | None = None,
    *,
    nodes: list[dict] | None = None,
    links: list[dict] | None = None,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
) -> Sankey:
    """Sankey diagram (plotly ``px.sankey``).

    Pass ``source``/``target``/``values`` columns, OR explicit ``nodes`` and
    ``links`` lists.
    """
    init_opts, _ = _common(title, width, height, theme)
    chart = Sankey(init_opts=init_opts)
    if links is None:
        df = normalize_data(data)
        ensure_columns(df, source, target, values)
        node_names = pd.unique(df[[source, target]].values.ravel())
        node_list = [{"name": str(n)} for n in node_names]
        src = df[source].astype(str).to_numpy()
        tgt = df[target].astype(str).to_numpy()
        val = df[values].to_numpy(dtype=float)
        link_list = [
            {"source": s, "target": t, "value": float(v)}
            for s, t, v in zip(src, tgt, val)
        ]
    else:
        node_list = nodes or []
        link_list = links
    chart.add("", nodes=node_list, links=link_list)
    chart.set_global_opts(
        title_opts=opts.TitleOpts(title=title) if title else opts.TitleOpts()
    )
    return chart


def gauge(
    data: Any,
    values: str | None = None,
    names: str | None = None,
    *,
    min_: float = 0,
    max_: float = 100,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
) -> Gauge:
    """Gauge chart."""
    df = normalize_data(data)
    init_opts, _ = _common(title, width, height, theme)
    chart = Gauge(init_opts=init_opts)
    if values is None:
        num = df.select_dtypes(include="number").columns
        values = num[0]
    ensure_columns(df, values)
    if names is not None and names in df.columns:
        pairs = list(zip(df[names].astype(str).tolist(), df[values].tolist()))
    else:
        pairs = [(str(i), v) for i, v in enumerate(df[values].tolist())]
    chart.add("", pairs, min_=min_, max_=max_)
    chart.set_global_opts(
        title_opts=opts.TitleOpts(title=title) if title else opts.TitleOpts()
    )
    return chart


def graph(
    data: Any,
    source: str | None = None,
    target: str | None = None,
    *,
    nodes: list[dict] | None = None,
    links: list[dict] | None = None,
    categories: list[str] | None = None,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
) -> Graph:
    """Graph / network chart (plotly ``px.scatter`` on a graph layout)."""
    init_opts, _ = _common(title, width, height, theme)
    chart = Graph(init_opts=init_opts)
    if links is None:
        df = normalize_data(data)
        ensure_columns(df, source, target)
        node_names = pd.unique(df[[source, target]].values.ravel())
        node_list = [{"name": str(n), "symbolSize": 10} for n in node_names]
        src = df[source].astype(str).to_numpy()
        tgt = df[target].astype(str).to_numpy()
        link_list = [
            {"source": s, "target": t} for s, t in zip(src, tgt)
        ]
        cats = None
    else:
        node_list = nodes or []
        link_list = links
        cats = [{"name": c} for c in categories] if categories else None
    chart.add("", nodes=node_list, links=link_list, categories=cats)
    chart.set_global_opts(
        title_opts=opts.TitleOpts(title=title) if title else opts.TitleOpts()
    )
    return chart


def themeriver(
    data: Any,
    date: str,
    value: str,
    category: str,
    *,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
) -> ThemeRiver:
    """Theme river chart."""
    df = normalize_data(data)
    ensure_columns(df, date, value, category)
    init_opts, _ = _common(title, width, height, theme)
    chart = ThemeRiver(init_opts=init_opts)
    cats = df[category].astype(str).unique().tolist()
    dates = df[date].astype(str).to_numpy()
    values = df[value].to_numpy(dtype=float)
    categories = df[category].astype(str).to_numpy()
    rows = [
        [str(dt), float(v), str(c)]
        for dt, v, c in zip(dates, values, categories)
    ]
    chart.add(cats, rows, singleaxis_opts=opts.SingleAxisOpts(type_="time"))
    chart.set_global_opts(
        title_opts=opts.TitleOpts(title=title) if title else opts.TitleOpts(),
    )
    return chart


def calendar_heatmap(
    data: Any,
    date: str,
    value: str,
    *,
    year: int | None = None,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
) -> Calendar:
    """Calendar heatmap."""
    df = normalize_data(data)
    ensure_columns(df, date, value)
    init_opts, _ = _common(title, width, height, theme)
    chart = Calendar(init_opts=init_opts)
    d = pd.to_datetime(df[date])
    if year is None:
        year = d.dt.year.mode().iloc[0]
    dates = d.dt.date.astype(str).to_numpy()
    values = df[value].to_numpy(dtype=float)
    pairs = [[str(dt), float(v)] for dt, v in zip(dates, values)]
    vmin = float(df[value].min())
    vmax = float(df[value].max())
    if vmax == vmin:
        vmax = vmin + 1.0
    chart.add(
        "",
        pairs,
        calendar_opts=opts.CalendarOpts(range_=str(year)),
    )
    chart.set_global_opts(
        title_opts=opts.TitleOpts(title=title) if title else opts.TitleOpts(),
        visualmap_opts=opts.VisualMapOpts(
            min_=vmin, max_=vmax,
            orient="horizontal", pos_bottom="5%",
        ),
    )
    return chart


def wordcloud(
    data: Any,
    words: str | None = None,
    values: str | None = None,
    *,
    pairs: list[tuple[str, int]] | None = None,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
) -> WordCloud:
    """Word cloud."""
    init_opts, _ = _common(title, width, height, theme)
    chart = WordCloud(init_opts=init_opts)
    if pairs is None:
        df = normalize_data(data)
        ensure_columns(df, words, values)
        wp = list(zip(df[words].astype(str).tolist(), df[values].tolist()))
    else:
        wp = list(pairs)
    chart.add("", wp, word_size_range=[12, 60])
    chart.set_global_opts(
        title_opts=opts.TitleOpts(title=title) if title else opts.TitleOpts()
    )
    return chart


def _validate_3d_columns(
    df: pd.DataFrame, x: str, y: str, z: str, color: str | None
) -> None:
    ensure_columns(df, x, y, z)
    if color is not None:
        ensure_columns(df, color)


def _visualmap_bounds(values: pd.Series) -> tuple[float, float]:
    numeric = pd.to_numeric(values, errors="coerce").dropna()
    if numeric.empty:
        raise ValueError("`z` must contain at least one numeric value.")
    minimum = float(numeric.min())
    maximum = float(numeric.max())
    if minimum == maximum:
        maximum = minimum + 1.0
    return minimum, maximum


def scatter_3d(
    data: Any,
    x: str,
    y: str,
    z: str,
    color: str | None = None,
    *,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
) -> Scatter3D:
    """3D scatter plot (plotly ``px.scatter_3d``).

    Uses ECharts GL (pyecharts Scatter3D) with a Cartesian3D coordinate system.
    """
    df = normalize_data(data)
    _validate_3d_columns(df, x, y, z, color)
    init_opts, _ = _common(title, width, height, theme)
    chart = Scatter3D(init_opts=init_opts)

    if color is not None:
        for name, group in df.groupby(color, sort=False):
            chart.add(
                str(name),
                group[[x, y, z]].values.tolist(),
                itemstyle_opts=opts.ItemStyleOpts(opacity=0.8),
            )
    else:
        chart.add(
            "",
            df[[x, y, z]].values.tolist(),
            itemstyle_opts=opts.ItemStyleOpts(opacity=0.8),
        )

    global_opts: dict[str, Any] = {
        "title_opts": opts.TitleOpts(title=title) if title else opts.TitleOpts()
    }
    if color is None:
        minimum, maximum = _visualmap_bounds(df[z])
        global_opts["visualmap_opts"] = opts.VisualMapOpts(
            min_=minimum, max_=maximum
        )
    chart.set_global_opts(**global_opts)
    return chart


def line_3d(
    data: Any,
    x: str,
    y: str,
    z: str,
    color: str | None = None,
    *,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
) -> Line3D:
    """3D line plot (plotly ``px.line_3d``)."""
    df = normalize_data(data)
    _validate_3d_columns(df, x, y, z, color)
    init_opts, _ = _common(title, width, height, theme)
    chart = Line3D(init_opts=init_opts)

    if color is not None:
        for name, group in df.groupby(color, sort=False):
            chart.add(str(name), group[[x, y, z]].values.tolist())
    else:
        chart.add("", df[[x, y, z]].values.tolist())

    chart.set_global_opts(
        title_opts=opts.TitleOpts(title=title) if title else opts.TitleOpts(),
    )
    return chart


def bar_3d(
    data: Any,
    x: str,
    y: str,
    z: str,
    color: str | None = None,
    *,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
) -> Bar3D:
    """3D bar chart (plotly ``px.bar`` with 3D semantics via ECharts Bar3D)."""
    df = normalize_data(data)
    _validate_3d_columns(df, x, y, z, color)
    init_opts, _ = _common(title, width, height, theme)
    chart = Bar3D(init_opts=init_opts)

    if color is not None:
        for name, group in df.groupby(color, sort=False):
            chart.add(str(name), group[[x, y, z]].values.tolist(), shading="lambert")
    else:
        chart.add("", df[[x, y, z]].values.tolist(), shading="lambert")

    global_opts: dict[str, Any] = {
        "title_opts": opts.TitleOpts(title=title) if title else opts.TitleOpts()
    }
    if color is None:
        minimum, maximum = _visualmap_bounds(df[z])
        global_opts["visualmap_opts"] = opts.VisualMapOpts(
            min_=minimum, max_=maximum
        )
    chart.set_global_opts(**global_opts)
    return chart


def scatter_ternary(
    data: Any,
    a: str,
    b: str,
    c: str,
    color: str | None = None,
    *,
    title: str | None = None,
    width: str | None = None,
    height: str | None = None,
    theme: str | None = None,
) -> Scatter:
    """Raise because ECharts has no ternary coordinate system."""
    raise NotImplementedError(
        "ECharts and pyecharts have no ternary coordinate system. "
        "Use plotly-express directly for ternary charts."
    )
