# graphcart

**graphcart** is a modular, one‑stop Python package for dataset visualization.
It ships with a single high-level function, `visualize`, plus a set of focused
helpers grouped by domain (basic, statistical, correlation, 3D, time‑series, interactive).

## Installation
```bash
pip install graphcart
```

## Quick start
```python
import pandas as pd
import seaborn as sns
from visuals.core import visualize

df = sns.load_dataset("iris")
visualize(df, "scatter", x="sepal_length", y="sepal_width", hue="species")
visualize(df, "heatmap")
visualize(df, "scatter3d", x="sepal_length", y="sepal_width", z="petal_length")
```

## Plot types
- Basic: bar, line, scatter, hist, box, pie, area
- Statistical: violin, swarm, strip, kde
- Correlation: heatmap, pair
- Advanced: hexbin, bubble, radar, waterfall
- 3D: scatter3d, surface3d
- Time series: ts (line), rolling mean
- Interactive: scatter_int, map

## Contributing
PRs welcome! Please run tests with `pytest`.

## License
MIT
