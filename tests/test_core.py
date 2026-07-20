"""Tests for pyecharts_express core data normalization."""

import pandas as pd
import pytest

from pyecharts_express.core import (
    ensure_columns,
    normalize_data,
    split_by_color,
)


def test_normalize_dataframe_passthrough():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    out = normalize_data(df)
    assert list(out.columns) == ["a", "b"]
    # copy, not the same object
    assert out is not df


def test_normalize_list_of_dicts():
    data = [{"x": 1, "y": 2}, {"x": 3, "y": 4}]
    out = normalize_data(data)
    assert list(out.columns) == ["x", "y"]
    assert len(out) == 2


def test_normalize_dict_of_columns():
    data = {"x": [1, 2, 3], "y": [4, 5, 6]}
    out = normalize_data(data)
    assert list(out.columns) == ["x", "y"]
    assert len(out) == 3


def test_normalize_invalid_list_raises():
    with pytest.raises(TypeError):
        normalize_data([1, 2, 3])


def test_ensure_columns_missing():
    df = pd.DataFrame({"a": [1]})
    with pytest.raises(KeyError):
        ensure_columns(df, "a", "b")


def test_split_by_color_none_returns_single_series():
    df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
    series = split_by_color(df, "x", "y", None)
    assert len(series) == 1
    name, xs, ys, color_val = series[0]
    assert name == "y"
    assert xs == [1, 2]
    assert ys == [3, 4]
    assert color_val is None


def test_split_by_color_no_x_uses_index():
    df = pd.DataFrame({"y": [3, 4, 5]})
    series = split_by_color(df, None, "y", None)
    _name, xs, ys, _color = series[0]
    assert xs == [0, 1, 2]
    assert ys == [3, 4, 5]


def test_split_by_color_groups():
    df = pd.DataFrame(
        {"x": ["a", "b", "a", "b"], "y": [1, 2, 3, 4], "g": ["p", "p", "q", "q"]}
    )
    series = split_by_color(df, "x", "y", "g")
    assert len(series) == 2
    names = {n for n, _, _, _ in series}
    assert names == {"p", "q"}
