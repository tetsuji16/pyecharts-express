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
