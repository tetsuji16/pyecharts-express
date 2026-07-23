# pyecharts-express

[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://github.com/tetsuji16/pyecharts-express/actions/workflows/tests.yml/badge.svg)](https://github.com/tetsuji16/pyecharts-express/actions)
[![PyPI version](https://img.shields.io/pypi/v/pyecharts-express.svg)](https://pypi.org/project/pyecharts-express/)

**A plotly-express style API for [pyecharts](https://pyecharts.org) (ECharts).**

Pass a pandas `DataFrame` or `list[dict]` directly and build charts with
intuitive keywords like `x` / `y` / `color`. Every function returns a plain
pyecharts `Chart` object, so the standard pyecharts API
(`.render()`, `.render_notebook()`, `Grid` composition, etc.) stays fully
available afterwards.

---

## Features

- 📊 **plotly-express style signatures** — `bar(df, x="city", y="pop", color="region")`
- 🐼 **pandas-friendly** — accepts `DataFrame` / `list[dict]` / `dict`
- 🎨 **pyecharts-compatible** — returns a raw `Chart`, freely customizable
- 🧩 **covers the plotly-express chart surface** using native ECharts series/options
- 🪶 **lightweight** — a thin wrapper layer; the full power of pyecharts is reachable
- 🎛️ **plotly-express compatible options** — `color_discrete_sequence` / `color_discrete_map`, `log_x` / `log_y`, `range_x` / `range_y`, `labels`, `opacity`, `orientation`, `symbol`
- 🧪 **tested** — `pytest` covers every chart type and the new options (87 tests)

---

## Installation

```bash
pip install pyecharts-express
# or
uv add pyecharts-express
```

---

## Quick start

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
# chart.render_notebook()   # inline display in Jupyter
```

---

## Chart reference

pyecharts-express mirrors the major plotly-express functions. Functions with
no pyecharts class are mapped directly to native ECharts APIs when ECharts
itself supports them. Features that would require a `custom` series remain
unsupported.

### Basic
| Function | Description | Key args |
|----------|-------------|----------|
| `px.bar` | Bar chart | `x`, `y`, `color`, `stack` |
| `px.line` | Line chart | `x`, `y`, `color`, `smooth` |
| `px.scatter` | Scatter plot | `x`, `y`, `color` |
| `px.area` | Area chart | `x`, `y`, `color`, `stack` |
| `px.funnel` | Funnel chart | `names`, `values`, `sort` |
| `px.funnel_area` | Area funnel | `names`, `values` |

### Part-of-whole
| Function | Description | Key args |
|----------|-------------|----------|
| `px.pie` | Pie chart | `names`, `values`, `hole`, `rose_type` |
| `px.sunburst` | Sunburst | `path` or (`names`, `parents`), `values` |
| `px.treemap` | Treemap | `path` or (`names`, `parents`), `values` |
| `px.icicle` | Icicle | `path` or (`names`, `parents`), `values` |

### Distributions
| Function | Description | Key args |
|----------|-------------|----------|
| `px.histogram` | Histogram | `x`, `bins`, `density` |
| `px.box` / `px.boxplot` | Box plot | `x`, `y` |
| `px.violin` | ❌ unsupported (requires custom rendering) | — |
| `px.strip` | Strip plot (ECharts 6 native jitter) | `x`, `y`, `color`, `jitter` |
| `px.density_heatmap` | 2D histogram | `x`, `y`, `bins` |
| `px.density_contour` | ❌ unsupported (requires custom rendering) | — |

### Matrix
| Function | Description | Key args |
|----------|-------------|----------|
| `px.imshow` | Scalar matrix via ECharts heatmap | `x`, `y`, `zmin`, `zmax`, `origin` |

### Polar
| Function | Description | Key args |
|----------|-------------|----------|
| `px.bar_polar` | Polar bar | `theta`, `r`, `color`, `stack` |
| `px.line_polar` | Polar line | `theta`, `r`, `color` |
| `px.scatter_polar` | Polar scatter | `theta`, `r`, `color` |

### Maps
| Function | Description | Key args |
|----------|-------------|----------|
| `px.map_choropleth` / `px.choropleth` | Choropleth map | `names`, `values`, `maptype` |
| `px.scatter_geo` | Geo scatter | `lon`, `lat`, `maptype` |
| `px.line_geo` | Geo line | `lon`, `lat`, `maptype` |

### Multidimensional
| Function | Description | Key args |
|----------|-------------|----------|
| `px.scatter_matrix` | Scatter plot matrix (SPLOM) | `dimensions`, `color` |
| `px.parallel_coordinates` | Parallel coordinates | `dimensions`, `color` |
| `px.parallel_categories` | Parallel categories | `dimensions`, `color` |
| `px.scatter_3d` | 3D scatter (ECharts GL) | `x`, `y`, `z`, `color` |
| `px.line_3d` | 3D line (ECharts GL) | `x`, `y`, `z`, `color` |
| `px.bar_3d` | 3D bar (ECharts GL) | `x`, `y`, `z`, `color` |
| `px.scatter_ternary` | ❌ unsupported (no ECharts equivalent) | — |

### Misc
| Function | Description | Key args |
|----------|-------------|----------|
| `px.radar` | Radar chart | `indicators`, `series` |
| `px.sankey` | Sankey diagram | `source`, `target`, `values` |
| `px.gauge` | Gauge | `values`, `min_`, `max_` |
| `px.graph` | Network graph | `source`, `target` |
| `px.themeriver` | Theme river | `date`, `value`, `category` |
| `px.calendar_heatmap` | Calendar heatmap | `date`, `value`, `year` |
| `px.wordcloud` | Word cloud | `words`, `values` |

---

## Hierarchical data

`sunburst` / `treemap` / `icicle` accept two input shapes:

```python
# 1. path (ordered hierarchy columns)
px.sunburst(df, path=["region", "pref", "city"], values="population")

# 2. names / parents (plotly style)
px.sunburst(df, names="node", parents="parent", values="value")
```

---

## Input shapes

Every function accepts:

```python
# 1. pandas DataFrame
px.bar(df, x="city", y="pop")

# 2. list[dict] (records)
px.line([{"x": 1, "y": 2}, {"x": 2, "y": 4}], x="x", y="y")

# 3. dict (column-oriented)
px.bar({"x": ["a", "b"], "y": [1, 2]}, x="x", y="y")
```

---

## Common options

```python
px.bar(
    df, x="city", y="pop",
    title="Title",
    xaxis_name="City",
    yaxis_name="Population",
    width="800px",
    height="500px",
    theme="dark",
)
```

---

## Options (plotly-express compatible)

Most chart functions accept these shared keyword arguments:

| Option | Applies to | Description |
|--------|-----------|-------------|
| `color_discrete_sequence` | bar, line, scatter, area, pie, funnel, radar | Ordered list of CSS colors assigned to series in order |
| `color_discrete_map` | bar, line, scatter, area, pie, funnel, radar | Dict mapping series name → fixed CSS color |
| `log_x` / `log_y` | bar, line, scatter, area, histogram, boxplot | Use a logarithmic axis |
| `range_x` / `range_y` | bar, line, scatter, area, histogram, boxplot | `(min, max)` axis bounds |
| `labels` | all | Dict `{column: display_name}` renaming axis titles / categories / indicator names |
| `opacity` | bar, line, scatter, area, pie, funnel, boxplot, histogram | Item opacity 0–1 |
| `orientation` | bar | `"v"` (default) or `"h"` (horizontal) |
| `symbol` / `symbol_sequence` | scatter | Marker shape (`"circle"`, `"rect"`, …) |

Example:

```python
chart = px.bar(
    df, x="city", y="pop", color="region",
    color_discrete_sequence=["#1f77b4", "#ff7f0e"],
    log_y=True,
    labels={"pop": "Population (log)"},
    opacity=0.8,
)
```

---

## Interop with pyecharts

The return value is a raw pyecharts `Chart`, so you can extend it with the
standard API:

```python
chart = px.bar(df, x="city", y="pop")
chart.set_series_opts(label_opts=opts.LabelOpts(is_show=True))
chart.render("custom.html")
```

Compose multiple charts with `Grid` / `Page`:

```python
from pyecharts.charts import Page
page = Page()
page.add(px.bar(df, x="city", y="pop"))
page.add(px.line(df, x="city", y="pop"))
page.render("page.html")
```

---

## Development

```bash
git clone https://github.com/tetsuji16/pyecharts-express
cd pyecharts-express
uv sync
uv run pytest
```

---

## License

[MIT](LICENSE)
