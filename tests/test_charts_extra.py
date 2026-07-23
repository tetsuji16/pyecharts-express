"""Tests for the extended pyecharts_express chart builders (plotly-express coverage)."""

import os
import tempfile

import numpy as np
import pandas as pd
import pytest

import pyecharts_express as px
def _assert_renders(chart):
    # Grid / Page are composite charts, not subclasses of Chart
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "out.html")
        chart.render(path)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0


def _hier_df():
    return pd.DataFrame(
        {
            "region": ["Kanto", "Kanto", "Kansai", "Kansai"],
            "pref": ["Tokyo", "Saitama", "Osaka", "Kyoto"],
            "city": ["Shinjuku", "Omiya", "Umeda", "Gion"],
            "val": [100, 40, 80, 30],
            "x": [1, 2, 3, 4],
            "y": [2, 3, 1, 4],
            "r": [5, 6, 7, 8],
        }
    )


def test_area():
    _assert_renders(px.area(_hier_df(), x="x", y="y"))


def test_area_stack():
    _assert_renders(px.area(_hier_df(), x="x", y="y", color="region", stack=True))


def test_funnel_area():
    _assert_renders(px.funnel_area(_hier_df(), names="pref", values="val"))


def test_box_alias():
    _assert_renders(px.box(_hier_df(), x="region", y="val"))


def test_strip_uses_native_echarts_axis_jitter():
    chart = px.strip(
        _hier_df(),
        x="region",
        y="val",
        color="pref",
        jitter=24,
        jitter_overlap=False,
    )
    assert chart.options["xAxis"][0]["jitter"] == 24
    assert chart.options["xAxis"][0]["jitterOverlap"] is False
    assert all(series["type"] == "scatter" for series in chart.options["series"])
    assert all("renderItem" not in series for series in chart.options["series"])
    _assert_renders(chart)


def test_strip_horizontal_jitters_category_y_axis():
    chart = px.strip(_hier_df(), x="val", y="region", orientation="h")
    assert chart.options["yAxis"][0]["type"] == "category"
    assert chart.options["yAxis"][0]["jitter"] == 20
    assert chart.options["yAxis"][0]["data"] == ["Kanto", "Kansai"]
    assert chart.options["series"][0]["data"][0] == (100, "Kanto")
    _assert_renders(chart)


def test_imshow_uses_native_heatmap_and_visualmap():
    frame = pd.DataFrame([[1, 2], [3, 4]], index=["a", "b"], columns=["u", "v"])
    chart = px.imshow(
        frame,
        origin="upper",
        color_continuous_scale=["#000000", "#ffffff"],
        text_auto=True,
    )
    assert chart.options["series"][0]["type"] == "heatmap"
    assert chart.options["yAxis"][0]["inverse"] is True
    assert chart.options["visualMap"].opts["min"] == 1
    assert chart.options["visualMap"].opts["max"] == 4
    assert chart.options["visualMap"].opts["inRange"]["color"] == [
        "#000000",
        "#ffffff",
    ]
    assert "renderItem" not in chart.options["series"][0]
    _assert_renders(chart)


def test_sunburst_path():
    _assert_renders(px.sunburst(_hier_df(), path=["region", "pref", "city"], values="val"))


def test_sunburst_names_parents():
    df = pd.DataFrame(
        {
            "names": ["root", "a", "b", "a1", "b1"],
            "parents": ["", "root", "root", "a", "b"],
            "values": [0, 10, 20, 5, 8],
        }
    )
    _assert_renders(px.sunburst(df, names="names", parents="parents", values="values"))


def test_treemap():
    _assert_renders(px.treemap(_hier_df(), path=["region", "pref"], values="val"))


def test_icicle():
    _assert_renders(px.icicle(_hier_df(), path=["region", "pref"], values="val"))


def test_bar_polar():
    _assert_renders(px.bar_polar(_hier_df(), theta="pref", r="val"))


def test_line_polar():
    _assert_renders(px.line_polar(_hier_df(), theta="pref", r="val"))


def test_scatter_polar():
    _assert_renders(px.scatter_polar(_hier_df(), theta="pref", r="val"))


def test_map_choropleth():
    _assert_renders(px.map_choropleth(_hier_df(), names="pref", values="val"))


def test_choropleth_alias():
    _assert_renders(px.choropleth(_hier_df(), names="pref", values="val"))


def test_scatter_geo():
    _assert_renders(px.scatter_geo(_hier_df(), lon="x", lat="y"))


def test_line_geo():
    _assert_renders(px.line_geo(_hier_df(), lon="x", lat="y"))


def test_parallel_coordinates():
    _assert_renders(px.parallel_coordinates(_hier_df(), dimensions=["x", "y", "val"]))


def test_parallel_categories():
    _assert_renders(px.parallel_categories(_hier_df(), dimensions=["region", "pref"]))


def test_scatter_matrix():
    _assert_renders(px.scatter_matrix(_hier_df(), dimensions=["x", "y", "val"]))


def test_sankey():
    _assert_renders(px.sankey(_hier_df(), source="pref", target="region", values="val"))


def test_gauge():
    _assert_renders(px.gauge(_hier_df(), values="val"))


def test_graph():
    _assert_renders(px.graph(_hier_df(), source="pref", target="region"))


def test_themeriver():
    df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=10),
            "val": np.arange(10),
            "cat": ["a"] * 10,
        }
    )
    _assert_renders(px.themeriver(df, date="date", value="val", category="cat"))


def test_calendar_heatmap():
    df = pd.DataFrame(
        {"date": pd.date_range("2024-01-01", periods=30), "val": np.arange(30)}
    )
    _assert_renders(px.calendar_heatmap(df, date="date", value="val"))


def test_wordcloud():
    df = pd.DataFrame({"word": ["a", "b", "c"], "count": [10, 20, 30]})
    _assert_renders(px.wordcloud(df, words="word", values="count"))


@pytest.mark.parametrize("chart_fn", [px.scatter_3d, px.line_3d, px.bar_3d])
def test_3d_charts_render_with_echarts_gl(chart_fn):
    df = pd.DataFrame(
        {"x": [1, 2, 3], "y": [4, 5, 6], "z": [7, 8, 9], "group": ["a", "a", "b"]}
    )
    chart = chart_fn(df, x="x", y="y", z="z", color="group")
    assert "echarts-gl" in chart.js_dependencies.items
    assert [series["name"] for series in chart.options["series"]] == ["a", "b"]
    _assert_renders(chart)


@pytest.mark.parametrize("chart_fn", [px.scatter_3d, px.line_3d, px.bar_3d])
def test_3d_charts_reject_missing_color_column(chart_fn):
    df = pd.DataFrame({"x": [1], "y": [2], "z": [3]})
    with pytest.raises(KeyError, match="missing"):
        chart_fn(df, x="x", y="y", z="z", color="missing")


@pytest.mark.parametrize("chart_fn", [px.scatter_3d, px.bar_3d])
def test_3d_visualmap_has_non_degenerate_bounds(chart_fn):
    df = pd.DataFrame({"x": [1, 2], "y": [3, 4], "z": [-5, -5]})
    chart = chart_fn(df, x="x", y="y", z="z")
    visualmap = chart.options["visualMap"].opts
    assert visualmap["min"] == -5
    assert visualmap["max"] == -4


def test_scatter_ternary_is_explicitly_unsupported():
    with pytest.raises(NotImplementedError, match="no ternary coordinate system"):
        px.scatter_ternary([], a="a", b="b", c="c")


def test_not_implemented_raise():
    with pytest.raises(NotImplementedError):
        px.violin()
    with pytest.raises(NotImplementedError):
        px.density_contour()
