# FrameDisplay: Enhanced DataFrame Display

<div align="center">

[![GitHub](https://img.shields.io/badge/nsarang-framedisplay-red?logo=github&logoSize=auto)](https://github.com/nsarang/framedisplay)
[![PyPI](https://img.shields.io/pypi/v/framedisplay?logoSize=auto)](https://pypi.org/project/framedisplay/)
[![Python Versions](https://img.shields.io/pypi/pyversions/framedisplay?logoSize=auto)](https://pypi.org/project/framedisplay/)
![License](https://img.shields.io/pypi/l/framedisplay?logo=auto&refresh=123)
[![Codecov](https://codecov.io/gh/nsarang/framedisplay/branch/main/graph/badge.svg)](https://codecov.io/gh/nsarang/framedisplay)

<br/>
<img alt="DataFrame" src="https://raw.githubusercontent.com/nsarang/framedisplay/refs/heads/main/assets/dataframe.png" width="500px" style="max-width: 100%;">

<br/>
<br/>
</div>

FrameDisplay is a lightweight Python package for rendering Pandas DataFrames as interactive HTML tables within Jupyter Notebooks and JupyterLab. It improves the default DataFrame display by adding features such as resizable columns, client-side sorting, sticky headers and index for improved navigation, data type indicators in column headers, distinct styling for null values, and tooltips for viewing complete cell content.

I work extensively with Pandas in my personal projects and have always wanted something similar to Databricks' display function, but for Jupyter. The existing open-source alternatives were either too heavyweight, lacked the visual appeal or didn't check all the boxes I needed. So I built this package to bridge that gap. It's not perfect yet, but I like it more than the alternatives :)


Live demo: [CodePen](https://codepen.io/B-L-A-Z-E/pen/empJPKV)

## Features

- **Resizable Columns**: Drag column dividers to resize them.
- **Sortable Columns**: Click on column headers to sort the data.
- **Sticky Header & Index**: The header and index rows remain visible during vertical and horizontal scrolling.
- **Column Type Icons**: Icons in headers indicate data types (numeric, string, etc.).
- **Null Value Styling**: `null` values are visually distinct.
- **Tooltips**: Hover over cell content to see the full value.
- **No Size Limit**: Display DataFrames of any size (be mindful of browser performance with very large tables).

**Roadmap**
- Virtual scrolling for improved performance with very large DataFrames.
- Additional customization options (e.g., theming).

## Installation

```bash
pip install framedisplay
```

## Usage

To display a DataFrame, simply import `framedisplay` and use the `frame_display` function:

```python
import pandas as pd
import numpy as np
import framedisplay as fd

df = pd.DataFrame({
    'Name': ['Alice', 'Bob', np.nan],
    'Age': [25, np.nan, 35],
    'Score': [95.5, 87.2, np.nan]
})

fd.frame_display(df)
```

You can also enable FrameDisplay globally for all DataFrames in Jupyter by calling `fd.integrate_with_pandas()`:

```python
import pandas as pd
import framedisplay as fd

# Enable FrameDisplay for all DataFrames
fd.integrate_with_pandas()

# This will now display using FrameDisplay
df
```

## How it Works

FrameDisplay renders your Pandas DataFrame into an HTML table and injects custom CSS and JavaScript to enable interactive features directly in your Jupyter Notebook or browser.

## Configuration (Optional)

You can customize the behavior and appearance by setting a global `window.FrameDisplayConfig` object in a Jupyter cell before displaying:

```python
from IPython.display import display, HTML

display(HTML("""
<script>
window.FrameDisplayConfig = {
    minColumnWidth: 30,
    resizerWidth: 8,
    resizerHoverColor: 'rgba(0,0,0,0.1)',
    showHoverEffect: true,
    autoInit: true,
    allowReInit: true
};
</script>
"""))
```

## Offline Mode

If you are working in an environment without internet access, you can inject the necessary JavaScript and CSS locally by calling `initialize()` at the start of your notebook. This bundles the required assets into the notebook itself.

```python
import framedisplay as fd
fd.initialize()

# Now you can use fd.frame_display(df) without needing an internet connection
```

## License

MIT
