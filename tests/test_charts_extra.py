"""Tests for the extended pyecharts_express chart builders (plotly-express coverage)."""

import os
import tempfile

import numpy as np
import pandas as pd
import pytest

import pyecharts_express as px
from pyecharts.charts.chart import Chart


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


def test_not_implemented_raise():
    with pytest.raises(NotImplementedError):
        px.violin()
    with pytest.raises(NotImplementedError):
        px.strip()
    with pytest.raises(NotImplementedError):
        px.density_contour()
