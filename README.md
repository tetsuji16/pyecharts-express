# pyecharts-express

[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Plotly-Express 風の簡潔な API で [pyecharts](https://pyecharts.org) (ECharts) のチャートを作るライブラリ。**

pandas の `DataFrame` や `list[dict]` をそのまま渡して、`x` / `y` / `color` といったキーワードで直感的にチャートを生成できます。返り値は普通の pyecharts の `Chart` オブジェクトなので、その後は標準の pyecharts API（`.render()`、`.render_notebook()`、`Grid` との組み合わせなど）がそのまま使えます。

---

## 特徴

- 📊 **plotly-express 風のシグネチャ** — `bar(df, x="city", y="pop", color="region")`
- 🐼 **pandas フレンドリー** — `DataFrame` / `list[dict]` / `dict` をそのまま受付
- 🎨 **pyecharts と互換** — 返り値は生の `Chart` なので追加カスタマイズ自由
- 🪶 **軽量** — 薄いラッパー層のみ。pyecharts の全機能にアクセス可能
- 🧪 **テスト済み** — `pytest` で全チャート種別をカバー

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

# 棒グラフ（region で色分け）
chart = px.bar(df, x="city", y="pop", color="region", title="Population")
chart.render("bar.html")          # HTML 出力
# chart.render_notebook()         # Jupyter でインライン表示
```

---

## 対応チャート

| 関数 | 説明 | 主な引数 |
|------|------|----------|
| `px.bar` | 棒グラフ | `x`, `y`, `color`, `stack` |
| `px.line` | 折れ線グラフ | `x`, `y`, `color`, `smooth` |
| `px.scatter` | 散布図 | `x`, `y`, `color`, `size` |
| `px.pie` | 円グラフ | `names`, `values`, `hole`, `rose_type` |
| `px.funnel` | ファネル図 | `names`, `values`, `sort` |
| `px.boxplot` | 箱ひげ図 | `x`, `y`（グループ化） |
| `px.histogram` | ヒストグラム | `x`, `bins`, `density` |
| `px.density_heatmap` | 2D ヒストグラム | `x`, `y`, `bins` |
| `px.radar` | レーダーチャート | `indicators`, `series` |

---

## 入力データの形

すべての関数は以下の入力を受け付けます：

```python
# 1. pandas DataFrame
px.bar(df, x="city", y="pop")

# 2. list[dict]（レコード形式）
px.line(
    [{"x": 1, "y": 2}, {"x": 2, "y": 4}],
    x="x", y="y",
)

# 3. dict（列指向）
px.bar({"x": ["a", "b"], "y": [1, 2]}, x="x", y="y")
```

---

## 共通オプション

すべてのチャート関数が受け付ける共通キーワード：

```python
px.bar(
    df, x="city", y="pop",
    title="タイトル",          # グラフタイトル
    xaxis_name="都市",         # X軸ラベル
    yaxis_name="人口",         # Y軸ラベル
    width="800px",             # 幅
    height="500px",            # 高さ
    theme="dark",              # テーマ (light/dark/roma/...)
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
