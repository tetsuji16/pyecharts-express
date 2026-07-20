# pyecharts-express

[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://github.com/tetsuji16/pyecharts-express/actions/workflows/tests.yml/badge.svg)](https://github.com/tetsuji16/pyecharts-express/actions)

**Plotly-Express 風の簡潔な API で [pyecharts](https://pyecharts.org) (ECharts) のチャートを作るライブラリ。**

pandas の `DataFrame` や `list[dict]` をそのまま渡して、`x` / `y` / `color` といったキーワードで直感的にチャートを生成できます。返り値は普通の pyecharts の `Chart` オブジェクトなので、その後は標準の pyecharts API（`.render()`、`.render_notebook()`、`Grid` との組み合わせなど）がそのまま使えます。

---

## 特徴

- 📊 **plotly-express 風のシグネチャ** — `bar(df, x="city", y="pop", color="region")`
- 🐼 **pandas フレンドリー** — `DataFrame` / `list[dict]` / `dict` をそのまま受付
- 🎨 **pyecharts と互換** — 返り値は生の `Chart` なので追加カスタマイズ自由
- 🧩 **plotly-express の全チャートに対応**（不可能なものは明確に案内）
- 🪶 **軽量** — 薄いラッパー層のみ。pyecharts の全機能にアクセス可能
- 🧪 **テスト済み** — `pytest` で全チャート種別をカバー（54 tests）

---

## インストール

```bash
pip install pyecharts-express
# または
uv add pyecharts-express
```

---

## クイックスタート

```python
import pandas as pd
import pyecharts_express as px

df = pd.DataFrame({
    "city":   ["Tokyo", "Osaka", "Kyoto", "Nagoya"],
    "pop":    [139, 27, 15, 23],
    "region": ["Kanto", "Kansai", "Kansai", "Chubu"],
})

chart = px.bar(df, x="city", y="pop", color="region", title="Population")
chart.render("bar.html")
# chart.render_notebook()   # Jupyter でインライン表示
```

---

## 対応チャート一覧

plotly-express の主要関数を網羅しています（該当チャートがないものは `NotImplementedError` で案内）。

### 基本
| 関数 | 説明 | 主な引数 |
|------|------|----------|
| `px.bar` | 棒グラフ | `x`, `y`, `color`, `stack` |
| `px.line` | 折れ線グラフ | `x`, `y`, `color`, `smooth` |
| `px.scatter` | 散布図 | `x`, `y`, `color` |
| `px.area` | 面積グラフ | `x`, `y`, `color`, `stack` |
| `px.funnel` | ファネル図 | `names`, `values`, `sort` |
| `px.funnel_area` | 面積ファネル図 | `names`, `values` |

### 部分全体
| 関数 | 説明 | 主な引数 |
|------|------|----------|
| `px.pie` | 円グラフ | `names`, `values`, `hole`, `rose_type` |
| `px.sunburst` | サンバースト | `path` or (`names`, `parents`), `values` |
| `px.treemap` | ツリーマップ | `path` or (`names`, `parents`), `values` |
| `px.icicle` | アイシクル図 | `path` or (`names`, `parents`), `values` |

### 分布
| 関数 | 説明 | 主な引数 |
|------|------|----------|
| `px.histogram` | ヒストグラム | `x`, `bins`, `density` |
| `px.box` / `px.boxplot` | 箱ひげ図 | `x`, `y` |
| `px.violin` | ❌ 非対応（pyecharts に該当なし） | — |
| `px.strip` | ❌ 非対応 | — |
| `px.density_heatmap` | 2D ヒストグラム | `x`, `y`, `bins` |
| `px.density_contour` | ❌ 非対応（pyecharts に該当なし） | — |

### 極座標
| 関数 | 説明 | 主な引数 |
|------|------|----------|
| `px.bar_polar` | 極座標棒 | `theta`, `r`, `color`, `stack` |
| `px.line_polar` | 極座標線 | `theta`, `r`, `color` |
| `px.scatter_polar` | 極座標散布 | `theta`, `r`, `color` |

### 地図
| 関数 | 説明 | 主な引数 |
|------|------|----------|
| `px.map_choropleth` / `px.choropleth` | 塗り分け地図 | `names`, `values`, `maptype` |
| `px.scatter_geo` | 地理座標散布 | `lon`, `lat`, `maptype` |
| `px.line_geo` | 地理座標線 | `lon`, `lat`, `maptype` |

### 多次元
| 関数 | 説明 | 主な引数 |
|------|------|----------|
| `px.scatter_matrix` | 散布行列 (SPLOM) | `dimensions`, `color` |
| `px.parallel_coordinates` | 平行座標 | `dimensions`, `color` |
| `px.parallel_categories` | 平行カテゴリ | `dimensions`, `color` |

### その他
| 関数 | 説明 | 主な引数 |
|------|------|----------|
| `px.radar` | レーダーチャート | `indicators`, `series` |
| `px.sankey` | サンキー図 | `source`, `target`, `values` |
| `px.gauge` | ゲージ | `values`, `min_`, `max_` |
| `px.graph` | ネットワーク図 | `source`, `target` |
| `px.themeriver` | テーマリバー | `date`, `value`, `category` |
| `px.calendar_heatmap` | カレンダーHeatmap | `date`, `value`, `year` |
| `px.wordcloud` | ワードクラウド | `words`, `values` |

---

## 階層データの渡し方

`sunburst` / `treemap` / `icicle` は2通りの入力を受け付けます：

```python
# 1. path（階層の列を順に指定）
px.sunburst(df, path=["region", "pref", "city"], values="population")

# 2. names / parents（plotly スタイル）
px.sunburst(df, names="node", parents="parent", values="value")
```

---

## 入力データの形

すべての関数は以下の入力を受け付けます：

```python
# 1. pandas DataFrame
px.bar(df, x="city", y="pop")

# 2. list[dict]（レコード形式）
px.line([{"x": 1, "y": 2}, {"x": 2, "y": 4}], x="x", y="y")

# 3. dict（列指向）
px.bar({"x": ["a", "b"], "y": [1, 2]}, x="x", y="y")
```

---

## 共通オプション

```python
px.bar(
    df, x="city", y="pop",
    title="タイトル",
    xaxis_name="都市",
    yaxis_name="人口",
    width="800px",
    height="500px",
    theme="dark",
)
```

---

## pyecharts との連携

返り値はそのまま pyecharts の `Chart` なので、標準 API で拡張できます：

```python
chart = px.bar(df, x="city", y="pop")
chart.set_series_opts(label_opts=opts.LabelOpts(is_show=True))
chart.render("custom.html")
```

複数チャートの配置には `Grid` / `Page` が使えます：

```python
from pyecharts.charts import Page
page = Page()
page.add(px.bar(df, x="city", y="pop"))
page.add(px.line(df, x="city", y="pop"))
page.render("page.html")
```

---

## 開発

```bash
git clone https://github.com/tetsuji16/pyecharts-express
cd pyecharts-express
uv sync
uv run pytest
```

---

## ライセンス

[MIT](LICENSE)
