"""Tests for pyecharts_express chart builders."""

import os
import tempfile

import pandas as pd
import pytest

import pyecharts_express as px
from pyecharts.charts.chart import Chart


def _sample_df():
    return pd.DataFrame(
        {
            "city": ["Tokyo", "Osaka", "Kyoto", "Nagoya"],
            "pop": [139, 27, 15, 23],
            "region": ["Kanto", "Kansai", "Kansai", "Chubu"],
        }
    )


def _assert_renders(chart: Chart):
    assert isinstance(chart, Chart)
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "out.html")
        chart.render(path)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0


def test_bar_basic():
    chart = px.bar(_sample_df(), x="city", y="pop")
    _assert_renders(chart)


def test_bar_color_grouped():
    chart = px.bar(_sample_df(), x="city", y="pop", color="region")
    _assert_renders(chart)


def test_bar_stack():
    chart = px.bar(_sample_df(), x="city", y="pop", color="region", stack=True)
    _assert_renders(chart)


def test_bar_infer_y():
    chart = px.bar(_sample_df()[["pop"]], x=None)
    _assert_renders(chart)


def test_line_basic():
    chart = px.line(_sample_df(), x="city", y="pop")
    _assert_renders(chart)


def test_line_smooth_color():
    chart = px.line(_sample_df(), x="city", y="pop", color="region", smooth=True)
    _assert_renders(chart)


def test_scatter_basic():
    chart = px.scatter(_sample_df(), x="city", y="pop", color="region")
    _assert_renders(chart)


def test_pie_from_df():
    chart = px.pie(_sample_df(), names="city", values="pop")
    _assert_renders(chart)


def test_pie_hole():
    chart = px.pie(_sample_df(), names="city", values="pop", hole=True)
    _assert_renders(chart)


def test_funnel():
    chart = px.funnel(_sample_df(), names="city", values="pop")
    _assert_renders(chart)


def test_boxplot_by_group():
    chart = px.boxplot(_sample_df(), x="region", y="pop")
    _assert_renders(chart)


def test_boxplot_no_x():
    chart = px.boxplot(_sample_df(), y="pop")
    _assert_renders(chart)


def test_histogram():
    df = pd.DataFrame({"v": [1.0, 1.2, 1.5, 2.0, 2.1, 3.0, 3.5, 4.0]})
    chart = px.histogram(df, x="v", bins=4)
    _assert_renders(chart)


def test_histogram_density():
    df = pd.DataFrame({"v": [1.0, 1.2, 1.5, 2.0, 2.1, 3.0, 3.5, 4.0]})
    chart = px.histogram(df, x="v", bins=4, density=True)
    _assert_renders(chart)


def test_density_heatmap():
    import numpy as np

    rng = np.random.default_rng(0)
    df = pd.DataFrame(
        {"x": rng.normal(0, 1, 200), "y": rng.normal(0, 1, 200)}
    )
    chart = px.density_heatmap(df, x="x", y="y", bins=10)
    _assert_renders(chart)


def test_radar_indicators():
    df = pd.DataFrame(
        {
            "speed": [80, 90, 70],
            "power": [60, 70, 80],
            "stamina": [50, 60, 90],
        }
    )
    chart = px.radar(df)
    _assert_renders(chart)


def test_radar_with_series():
    df = pd.DataFrame(
        {
            "speed": [80, 90, 70],
            "power": [60, 70, 80],
            "stamina": [50, 60, 90],
            "name": ["A", "B", "C"],
        }
    )
    chart = px.radar(df, series="name")
    _assert_renders(chart)


def test_input_list_of_dicts():
    data = [{"x": "a", "y": 1}, {"x": "b", "y": 2}]
    chart = px.bar(data, x="x", y="y")
    _assert_renders(chart)


def test_input_dict_of_columns():
    data = {"x": ["a", "b"], "y": [1, 2]}
    chart = px.line(data, x="x", y="y")
    _assert_renders(chart)


def test_title_and_axis_names():
    chart = px.bar(
        _sample_df(),
        x="city",
        y="pop",
        title="Population",
        xaxis_name="City",
        yaxis_name="Population (10k)",
    )
    _assert_renders(chart)


def test_missing_column_raises():
    with pytest.raises(KeyError):
        px.bar(_sample_df(), x="nonexistent", y="pop")
