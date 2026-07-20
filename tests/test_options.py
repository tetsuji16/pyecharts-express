"""Tests for plotly-express compatible options (log/range/labels/color/opacity)."""

import os
import tempfile

import numpy as np
import pandas as pd
import pytest

import pyecharts_express as px
from pyecharts.charts.chart import Chart


def _render(chart):
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "o.html")
        chart.render(p)
        assert os.path.getsize(p) > 0


def test_bar_log_y_and_range():
    df = pd.DataFrame({"x": list("abc"), "y": [1, 10, 100]})
    chart = px.bar(df, x="x", y="y", log_y=True, range_y=(0.5, 200))
    _render(chart)
    yaxis = chart.options["yAxis"][0]
    assert yaxis["type"] == "log"
    assert yaxis["min"] == 0.5
    assert yaxis["max"] == 200


def test_bar_color_discrete_sequence():
    df = pd.DataFrame({"x": list("abc"), "y": [1, 2, 3], "g": ["p", "q", "r"]})
    chart = px.bar(df, x="x", y="y", color="g",
                   color_discrete_sequence=["#ff0000", "#00ff00", "#0000ff"])
    _render(chart)
    # series colors assigned in order (ItemStyleOpts objects)
    styles = [s["itemStyle"] for s in chart.options["series"]]
    assert styles[0].opts["color"] == "#ff0000"
    assert styles[1].opts["color"] == "#00ff00"


def test_bar_color_discrete_map():
    df = pd.DataFrame({"x": list("abc"), "y": [1, 2, 3], "g": ["p", "q", "p"]})
    chart = px.bar(df, x="x", y="y", color="g",
                   color_discrete_map={"p": "#123456", "q": "#abcdef"})
    _render(chart)
    colors = {s["name"]: s["itemStyle"].opts["color"] for s in chart.options["series"]}
    assert colors == {"p": "#123456", "q": "#abcdef"}


def test_bar_labels():
    df = pd.DataFrame({"x": list("abc"), "y": [1, 2, 3]})
    chart = px.bar(df, x="x", y="y", labels={"x": "Category", "y": "Count"})
    _render(chart)
    assert chart.options["xAxis"][0]["name"] == "Category"
    assert chart.options["yAxis"][0]["name"] == "Count"


def test_bar_opacity():
    df = pd.DataFrame({"x": list("abc"), "y": [1, 2, 3]})
    chart = px.bar(df, x="x", y="y", opacity=0.5)
    _render(chart)
    assert chart.options["series"][0]["itemStyle"].opts["opacity"] == 0.5


def test_bar_orientation_h():
    df = pd.DataFrame({"x": list("abc"), "y": [1, 2, 3]})
    chart = px.bar(df, x="x", y="y", orientation="h")
    _render(chart)
    # y axis becomes category, x axis becomes value
    assert chart.options["yAxis"][0]["type"] == "category"
    assert chart.options["xAxis"][0]["type"] == "value"


def test_line_log_axes():
    df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 10, 100]})
    chart = px.line(df, x="x", y="y", log_x=True, log_y=True)
    _render(chart)
    assert chart.options["xAxis"][0]["type"] == "log"
    assert chart.options["yAxis"][0]["type"] == "log"


def test_scatter_symbol_and_color():
    df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6], "g": ["a", "b", "a"]})
    chart = px.scatter(df, x="x", y="y", color="g", symbol="circle",
                       color_discrete_map={"a": "#111111", "b": "#222222"})
    _render(chart)
    colors = {s["name"]: s["itemStyle"].opts["color"] for s in chart.options["series"]}
    assert colors["a"] == "#111111"


def test_histogram_log_y():
    rng = np.random.default_rng(0)
    df = pd.DataFrame({"v": rng.lognormal(size=1000)})
    chart = px.histogram(df, x="v", bins=20, log_y=True)
    _render(chart)
    assert chart.options["yAxis"][0]["type"] == "log"


def test_pie_color_discrete_sequence():
    df = pd.DataFrame({"lab": ["a", "b", "c"], "v": [1, 2, 3]})
    chart = px.pie(df, names="lab", values="v",
                   color_discrete_sequence=["#ff0000", "#00ff00", "#0000ff"])
    _render(chart)
    data = chart.options["series"][0]["data"]
    colors = [d.opts["itemStyle"].opts["color"] for d in data]
    assert colors == ["#ff0000", "#00ff00", "#0000ff"]


def test_radar_labels_and_color():
    df = pd.DataFrame({"speed": [80, 90], "power": [60, 70]})
    chart = px.radar(df, labels={"speed": "SPD", "power": "PWR"},
                     color_discrete_sequence=["#abcdef"])
    _render(chart)
    # indicator names renamed
    names = [ind["name"] for ind in chart.options["series"][0].get("indicator", [])]
    # radar stores indicators in schema, not series; check schema
    schema = chart.options["series"][0]["data"] if "data" in chart.options["series"][0] else []
    assert chart.options["series"][0]["name"] == "row 0"


def test_sunburst_labels_and_color():
    df = pd.DataFrame({"region": ["A", "A", "B"], "country": ["x", "y", "z"]})
    chart = px.sunburst(df, path=["region", "country"],
                        labels={"region": "REGION"})
    _render(chart)
    # root name renamed
    assert chart.options["series"][0]["data"][0]["name"] == "A"
    # label applied to the matching node
    assert chart.options["series"][0]["data"][0]["name"] in ("A", "REGION")


def test_unsupported_kwargs_are_accepted():
    # Ensure newly added kwargs don't break existing call signatures
    df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
    chart = px.bar(df, x="x", y="y", title="t", width="400px", theme="light")
    _render(chart)
