"""Adversarial regression tests for pyecharts_express.

These pin down bugs found during adversarial review:
* horizontal bars must place categories on the y-axis
* color-split categorical axes must use the union of categories (no drops)
* build_hierarchy must accumulate duplicate leaf paths (and be fast)
* visualMap must not collapse to a degenerate min==max range
"""

import datetime

import pandas as pd
import pytest

import pyecharts_express as px
from pyecharts.charts.chart import Chart

from pyecharts_express.core import build_hierarchy


def _render(chart):
    assert isinstance(chart, Chart)
    import tempfile, os

    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "o.html")
        chart.render(p)
        assert os.path.getsize(p) > 0


def test_horizontal_bar_puts_categories_on_yaxis():
    df = pd.DataFrame({"cat": ["A", "B", "C"], "val": [3, 1, 2]})
    chart = px.bar(df, x="cat", y="val", orientation="h")
    # categories belong on the (vertical) y-axis for a horizontal bar
    assert chart.options["yAxis"][0].get("data") == ["A", "B", "C"]
    _render(chart)


def test_horizontal_bar_color_log_labels():
    df = pd.DataFrame(
        {"cat": ["A", "B", "C"], "val": [3, 1, 2], "g": ["x", "x", "y"]}
    )
    chart = px.bar(
        df, x="cat", y="val", color="g", orientation="h", log_y=True, yaxis_name="V"
    )
    assert chart.options["yAxis"][0].get("data") == ["A", "B", "C"]
    assert len(chart.options["series"]) == 2
    # value axis (physical x after reversal) carries the log scale + value label
    assert chart.options["xAxis"][0].get("type") == "log"
    assert chart.options["xAxis"][0].get("name") == "V"
    _render(chart)


def test_bar_color_nonoverlapping_categories_union_and_padding():
    df = pd.DataFrame(
        {"cat": ["A", "B", "C"], "val": [3, 1, 2], "g": ["x", "x", "y"]}
    )
    chart = px.bar(df, x="cat", y="val", color="g")
    # all three categories must be present on the axis
    assert chart.options["xAxis"][0].get("data") == ["A", "B", "C"]
    # group 'x' has A,B; group 'y' has C -> padded with None where absent
    s0 = chart.options["series"][0]["data"]
    s1 = chart.options["series"][1]["data"]
    assert s0 == [3, 1, None]
    assert s1 == [None, None, 2]
    _render(chart)


def test_line_color_nonoverlapping_categories():
    df = pd.DataFrame(
        {"cat": ["A", "B", "C"], "val": [3, 1, 2], "g": ["x", "x", "y"]}
    )
    chart = px.line(df, x="cat", y="val", color="g")
    assert chart.options["xAxis"][0].get("data") == ["A", "B", "C"]
    assert len(chart.options["series"]) == 2
    _render(chart)


def test_build_hierarchy_accumulates_duplicate_leaves():
    df = pd.DataFrame(
        {"r": ["R1", "R1", "R1"], "c": ["a", "a", "b"], "v": [1, 2, 3]}
    )
    hier = build_hierarchy(df, path=["r", "c"], names=None, parents=None, values="v")
    children = {ch["name"]: ch for ch in hier[0]["children"]}
    assert children["a"]["value"] == 3  # 1 + 2
    assert children["b"]["value"] == 3


def test_build_hierarchy_preserves_total_sum():
    n = 20000
    df = pd.DataFrame(
        {
            "r": [f"r{i % 50}" for i in range(n)],
            "c": [f"c{i % 200}" for i in range(n)],
            "v": range(n),
        }
    )
    hier = build_hierarchy(df, path=["r", "c"], names=None, parents=None, values="v")

    def leaf_sum(nodes):
        total = 0
        for nd in nodes:
            if "children" in nd:
                total += leaf_sum(nd["children"])
            else:
                total += nd["value"]
        return total

    assert leaf_sum(hier) == df["v"].sum()


def test_map_visualmap_not_degenerate_when_all_equal():
    df = pd.DataFrame({"p": ["Beijing", "Shanghai"], "v": [100, 100]})
    chart = px.map_choropleth(df, names="p", values="v", maptype="china")
    opts = chart.options["visualMap"].opts
    assert opts["min"] != opts["max"]


def test_calendar_visualmap_not_degenerate_when_all_equal():
    df = pd.DataFrame(
        {
            "d": [datetime.date(2023, 1, 1), datetime.date(2023, 1, 2)],
            "v": [5, 5],
        }
    )
    chart = px.calendar_heatmap(df, date="d", value="v", year=2023)
    opts = chart.options["visualMap"].opts
    assert opts["min"] != opts["max"]
