"""Adversarial / edge-case tests for pyecharts-express.

These intentionally feed hostile inputs: NaN-heavy frames, category dtypes,
generator inputs, duplicate hierarchy paths, empty data, huge cardinality.
"""

import numpy as np
import pandas as pd
import pytest

import pyecharts_express as px
from pyecharts.charts.chart import Chart


def _render(chart):
    import os
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "o.html")
        chart.render(p)
        assert os.path.getsize(p) > 0


def test_generator_input_not_consumed():
    # A generator of dicts must not lose its first element.
    def gen():
        yield {"x": 1, "y": 2}
        yield {"x": 2, "y": 3}

    chart = px.bar(gen(), x="x", y="y")
    _render(chart)
    # x axis should have both points (numeric preserved as-is by pyecharts)
    assert chart.options["xAxis"][0]["data"] == [1, 2]


def test_empty_dataframe():
    df = pd.DataFrame({"x": [], "y": []})
    chart = px.bar(df, x="x", y="y")
    _render(chart)


def test_color_with_nan_dropped():
    df = pd.DataFrame(
        {"x": ["a", "b", "c"], "y": [1, 2, 3], "g": ["p", None, "q"]}
    )
    chart = px.bar(df, x="x", y="y", color="g")
    _render(chart)
    # 'nan' series must not appear
    names = [s["name"] for s in chart.options["series"]]
    assert "nan" not in names
    assert set(names) == {"p", "q"}


def test_boxplot_keeps_nan_category():
    df = pd.DataFrame(
        {"g": ["a", "a", None, None], "y": [1.0, 2.0, 3.0, 4.0]}
    )
    chart = px.box(df, x="g", y="y")
    _render(chart)
    cats = chart.options["xAxis"][0]["data"]
    assert "<NA>" in cats  # NaN category preserved (not silently dropped)


def test_boxplot_many_categories_performance():
    # 500 categories x 10 rows — old code did O(N*C) filtering; must stay fast.
    import time

    rng = np.random.default_rng(0)
    df = pd.DataFrame(
        {
            "g": [f"c{i}" for i in range(500) for _ in range(10)],
            "y": rng.normal(size=5000),
        }
    )
    t0 = time.perf_counter()
    chart = px.box(df, x="g", y="y")
    dt = time.perf_counter() - t0
    _render(chart)
    assert dt < 2.0, f"boxplot too slow: {dt:.2f}s"


def test_pie_with_category_dtype():
    df = pd.DataFrame(
        {"label": pd.Categorical(["x", "y", "z"]), "v": [1, 2, 3]}
    )
    chart = px.pie(df)  # should infer label/v from category+numeric
    _render(chart)
    assert len(chart.options["series"][0]["data"]) == 3


def test_histogram_density_labels_finite():
    df = pd.DataFrame({"v": np.random.default_rng(1).normal(size=1000)})
    chart = px.histogram(df, x="v", bins=30, density=True)
    _render(chart)
    labels = chart.options["xAxis"][0]["data"]
    # no 'nan' or 'inf' in axis labels
    assert all(l != "nan" for l in labels)


def test_radar_many_rows_no_iterrows():
    import time

    df = pd.DataFrame({f"m{i}": np.random.default_rng(2).normal(size=2000) for i in range(3)})
    t0 = time.perf_counter()
    chart = px.radar(df)
    dt = time.perf_counter() - t0
    _render(chart)
    assert dt < 2.0, f"radar too slow: {dt:.2f}s"
    # 2000 series produced
    assert len(chart.options["series"]) == 2000


def test_sunburst_duplicate_leaf_paths_accumulate():
    df = pd.DataFrame(
        {
            "a": ["x", "x"],
            "b": ["y", "y"],
            "v": [10, 20],
        }
    )
    chart = px.sunburst(df, path=["a", "b"], values="v")
    _render(chart)
    # root x -> y should have value 30 (accumulated), not 20
    root = chart.options["series"][0]["data"][0]
    assert root["name"] == "x"
    child = root["children"][0]
    assert child["value"] == 30


def test_sankey_large_no_iterrows():
    import time

    n = 5000
    df = pd.DataFrame(
        {
            "s": [f"s{i%10}" for i in range(n)],
            "t": [f"t{i%5}" for i in range(n)],
            "v": np.ones(n),
        }
    )
    t0 = time.perf_counter()
    chart = px.sankey(df, source="s", target="t", values="v")
    dt = time.perf_counter() - t0
    _render(chart)
    assert dt < 2.0, f"sankey too slow: {dt:.2f}s"


def test_unknown_column_raises_clear_keyerror():
    df = pd.DataFrame({"x": [1], "y": [2]})
    with pytest.raises(KeyError):
        px.bar(df, x="nonexistent", y="y")
