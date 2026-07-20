"""Core helpers: data normalization and common option building.

pyecharts-express accepts several input shapes and normalizes them into a
pandas DataFrame so the chart builders can assume a uniform structure.

Supported inputs
-----------------
* ``pandas.DataFrame``
* ``list[dict]``  (records, e.g. ``[{"x": 1, "y": 2}, ...]``)
* ``dict`` of columns (e.g. ``{"x": [1, 2], "y": [3, 4]}``)
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence

import pandas as pd
from pyecharts import options as opts
from pyecharts.charts.chart import Chart


def normalize_data(data: Any) -> pd.DataFrame:
    """Convert supported input shapes into a :class:`pandas.DataFrame`.

    Note: a generator of dict records is materialized into a list first so it
    is not partially consumed by the ``list[dict]`` detection below.
    """
    if isinstance(data, pd.DataFrame):
        return data.copy()
    if isinstance(data, Mapping):
        # dict of columns -> DataFrame
        return pd.DataFrame(data)
    if isinstance(data, Iterable) and not isinstance(data, (str, bytes)):
        # Materialize so we don't lose the first element when peeking, and to
        # avoid iterating an unbounded generator twice.
        materialized = list(data)
        if not materialized:
            return pd.DataFrame()
        first = materialized[0]
        if isinstance(first, Mapping):
            return pd.DataFrame(materialized)
        raise TypeError(
            "list input must be a list of dict records, "
            f"got element of type {type(first).__name__!r}"
        )
    raise TypeError(f"Unsupported data type: {type(data).__name__!r}")


def ensure_columns(df: pd.DataFrame, *names: str) -> None:
    """Raise a clear error when a required column is missing."""
    missing = [n for n in names if n not in df.columns]
    if missing:
        raise KeyError(f"Column(s) not found: {missing}")


def split_by_color(
    df: pd.DataFrame,
    x: str | None,
    y: str,
    color: str | None,
    *,
    color_discrete_sequence: Sequence[str] | None = None,
    color_discrete_map: Mapping[str, str] | None = None,
    opacity: float | None = None,
) -> list[tuple[str, Sequence[Any], Sequence[Any], str | None]]:
    """Return ``(series_name, x_vals, y_vals, color_value)`` tuples.

    When ``color`` is given the data is grouped by that column and one series
    is produced per group. Otherwise a single series named ``y`` is returned.
    Rows with a missing ``color`` value are dropped (they can't belong to a
    named series).

    ``color_discrete_sequence`` assigns palette colors in series order;
    ``color_discrete_map`` pins specific series names to specific colors.
    The returned ``color_value`` is the resolved CSS color (or ``None`` to let
    pyecharts use its default palette). ``opacity`` (0–1) is returned alongside
    via the caller, which merges it into each series' ``itemStyle``.
    """
    palette = list(color_discrete_sequence or [])

    def resolve(name: str, idx: int) -> str | None:
        if color_discrete_map and name in color_discrete_map:
            return color_discrete_map[name]
        if palette:
            return palette[idx % len(palette)]
        return None

    if color is None:
        xs = df[x].tolist() if x is not None else list(range(len(df)))
        ys = df[y].tolist()
        return [(str(y), xs, ys, None)]

    out: list[tuple[str, Sequence[Any], Sequence[Any], str | None]] = []
    sub = df[df[color].notna()]
    for idx, (name, group) in enumerate(sub.groupby(color, sort=False)):
        xs = group[x].tolist() if x is not None else list(range(len(group)))
        ys = group[y].tolist()
        out.append((str(name), xs, ys, resolve(str(name), idx)))
    return out


def build_init_opts(
    width: str | None,
    height: str | None,
    theme: str | None,
) -> opts.InitOpts:
    """Construct :class:`InitOpts` from express-level kwargs."""
    kwargs: dict[str, Any] = {}
    if width is not None:
        kwargs["width"] = width
    if height is not None:
        kwargs["height"] = height
    if theme is not None:
        kwargs["theme"] = theme
    return opts.InitOpts(**kwargs)


def apply_common(
    chart: Chart,
    *,
    title: str | None = None,
    xaxis_name: str | None = None,
    yaxis_name: str | None = None,
    xaxis_type: str | None = None,
    yaxis_type: str | None = None,
    log_x: bool = False,
    log_y: bool = False,
    range_x: tuple[Any, Any] | None = None,
    range_y: tuple[Any, Any] | None = None,
    opacity: float | None = None,
) -> Chart:
    """Apply title / axis titles / axis types / scales / ranges to a chart.

    Parameters
    ----------
    log_x, log_y:
        Use a logarithmic axis (equivalent to plotly ``log_x`` / ``log_y``).
    range_x, range_y:
        ``(min, max)`` axis bounds (plotly ``range_x`` / ``range_y``).
    opacity:
        Item opacity 0–1 (plotly ``opacity``).
    """
    title_opts = opts.TitleOpts(title=title) if title else opts.TitleOpts()
    xaxis_opts = opts.AxisOpts(
        name=xaxis_name or "",
        type_="log" if log_x else xaxis_type,
        min_=range_x[0] if range_x else None,
        max_=range_x[1] if range_x else None,
    )
    yaxis_opts = opts.AxisOpts(
        name=yaxis_name or "",
        type_="log" if log_y else yaxis_type,
        min_=range_y[0] if range_y else None,
        max_=range_y[1] if range_y else None,
    )
    kwargs: dict[str, Any] = dict(
        title_opts=title_opts,
        xaxis_opts=xaxis_opts,
        yaxis_opts=yaxis_opts,
    )
    chart.set_global_opts(**kwargs)
    return chart


def reindex_series_for_axis(
    series: list[tuple[str, Sequence[Any], Sequence[Any], str | None]],
) -> tuple[list[Any], list[tuple[str, list[Any | None], str | None]]]:
    """Align color-split series onto a shared categorical axis.

    When ``color`` groups rows by a categorical ``x`` column, different groups
    may contain *different* categories. pyecharts aligns every series to the
    single ``xAxis`` it is given, so we must build the union of all categories
    (first-appearance order) and pad each series' y-values with ``None`` for
    categories it does not contain. Without this, bars/lines for categories
    missing from the first group silently fail to render.

    Returns ``(axis_order, aligned_series)`` where each aligned entry is
    ``(name, padded_ys, color_value)``.
    """
    order: list[Any] = []
    seen: set[Any] = set()
    for _name, xs, _ys, _c in series:
        for v in xs:
            if v not in seen:
                seen.add(v)
                order.append(v)
    index = {v: i for i, v in enumerate(order)}
    aligned: list[tuple[str, list[Any | None], str | None]] = []
    for name, xs, ys, color_val in series:
        padded = [None] * len(order)
        for x, y in zip(xs, ys):
            padded[index[x]] = y
        aligned.append((name, padded, color_val))
    return order, aligned


def build_hierarchy(
    df: pd.DataFrame,
    path: list[str] | None,
    names: str | None,
    parents: str | None,
    values: str | None,
) -> list[dict]:
    """Build a nested dict/list structure for sunburst / treemap / tree.

    Two input modes are supported:

    1. ``path`` — ordered list of columns describing the hierarchy level by
       level (e.g. ``["region", "country", "city"]``). Leaf value comes from
       ``values`` (or 1 if ``None``).
    2. ``names`` / ``parents`` — explicit node + parent columns (plotly
       ``px.sunburst(names=, parents=)`` style). ``values`` gives leaf size.
    """
    if path:
        ensure_columns(df, *path)
        if values is not None:
            ensure_columns(df, values)
            # Vectorized aggregation: correctly accumulates duplicate leaf
            # paths (e.g. two rows with the same full path sum their values)
            # and avoids the O(rows) Python iterrows loop.
            agg = df.groupby(list(path), sort=False)[values].sum()
        else:
            agg = df.groupby(list(path), sort=False).size().astype(float)

        root: dict = {}
        for raw_key, val in zip(agg.index, agg.values):
            key = tuple(str(k) for k in (raw_key if isinstance(raw_key, tuple) else (raw_key,)))
            node = root
            for i, level in enumerate(key):
                if i < len(key) - 1:
                    child = node.get(level)
                    if not isinstance(child, dict):
                        child = {}
                        node[level] = child
                    node = child
                else:
                    node[level] = float(val)

        def to_list(d: dict) -> list[dict]:
            out = []
            for name, sub in d.items():
                if isinstance(sub, dict):
                    out.append({"name": name, "children": to_list(sub)})
                else:
                    out.append({"name": name, "value": sub})
            return out

        return to_list(root)

    if names is not None and parents is not None:
        ensure_columns(df, names, parents)
        if values is not None:
            ensure_columns(df, values)
        nodes = {}
        for _, row in df.iterrows():
            n = str(row[names])
            p = str(row[parents]) if pd.notna(row[parents]) and row[parents] != "" else None
            v = float(row[values]) if values is not None else 1.0
            nodes[n] = {"name": n, "value": v, "parent": p}
        # build tree
        children: dict = {}
        roots = []
        for n, info in nodes.items():
            p = info["parent"]
            if p is None or p not in nodes:
                roots.append(info)
            else:
                children.setdefault(p, []).append(info)
        # attach children recursively
        def attach(info):
            kids = children.get(info["name"], [])
            if kids:
                info["children"] = [attach(k) for k in kids]
            else:
                # leaf keeps value
                pass
            return info

        result = [attach(r) for r in roots]
        # if single root with children, flatten one level like plotly
        return result

    raise ValueError("Either `path` or both `names` and `parents` must be given.")
