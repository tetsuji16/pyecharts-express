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
    """Convert supported input shapes into a :class:`pandas.DataFrame`."""
    if isinstance(data, pd.DataFrame):
        return data.copy()
    if isinstance(data, Mapping):
        # dict of columns -> DataFrame
        return pd.DataFrame(data)
    if isinstance(data, Iterable) and not isinstance(data, (str, bytes)):
        first = next(iter(data), None)
        if isinstance(first, Mapping):
            return pd.DataFrame(list(data))
        raise TypeError(
            "list input must be a list of dict records, "
            f"got element of type {type(first).__name__!r}"
        )
    raise TypeError(f"Unsupported data type: {type(data).__name__!r}")


def ensure_columns(df: pd.DataFrame, *names: str) -> None:
    """Raise a clear error when a required column is missing."""
    missing = [n for n in names if n not in df.columns]
    if missing:
        raise KeyError(
            f"Column(s) {missing} not found. Available columns: {list(df.columns)}"
        )


def split_by_color(
    df: pd.DataFrame, x: str | None, y: str, color: str | None
) -> list[tuple[str, Sequence[Any], Sequence[Any]]]:
    """Return ``(series_name, x_vals, y_vals)`` tuples.

    When ``color`` is given the data is grouped by that column and one series
    is produced per group. Otherwise a single series named ``y`` is returned.
    """
    if color is None:
        xs = df[x].tolist() if x is not None else list(range(len(df)))
        ys = df[y].tolist()
        return [(str(y), xs, ys)]

    out: list[tuple[str, Sequence[Any], Sequence[Any]]] = []
    for name, group in df.groupby(color, sort=False):
        xs = group[x].tolist() if x is not None else list(range(len(group)))
        ys = group[y].tolist()
        out.append((str(name), xs, ys))
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
) -> Chart:
    """Apply title / axis titles / axis types to a chart."""
    title_opts = opts.TitleOpts(title=title) if title else opts.TitleOpts()
    xaxis_opts = opts.AxisOpts(
        name=xaxis_name or "",
        type_=xaxis_type,
    )
    yaxis_opts = opts.AxisOpts(
        name=yaxis_name or "",
        type_=yaxis_type,
    )
    chart.set_global_opts(
        title_opts=title_opts,
        xaxis_opts=xaxis_opts,
        yaxis_opts=yaxis_opts,
    )
    return chart


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

        # group rows into nested dict keyed by tuple path
        root: dict = {}
        for _, row in df.iterrows():
            key = tuple(str(row[p]) for p in path)
            val = float(row[values]) if values is not None else 1.0
            node = root
            for i, level in enumerate(key):
                if level not in node:
                    node[level] = {} if i < len(key) - 1 else val
                if i == len(key) - 1:
                    # accumulate leaf value
                    if isinstance(node[level], dict):
                        node[level] = val
                    else:
                        node[level] = node[level] + val
                node = node[level] if isinstance(node[level], dict) else root

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
