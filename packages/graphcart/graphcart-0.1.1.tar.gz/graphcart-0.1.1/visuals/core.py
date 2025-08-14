from .utils import ensure_df
from .basic_plots import bar_plot, line_plot, scatter_plot, histogram, box_plot, pie_chart, area_plot
from .statistical_plots import violin_plot, swarm_plot, strip_plot, kde_plot
from .correlation_plots import correlation_heatmap, pair_plot
from .advanced_plots import hexbin_plot, bubble_plot, radar_chart, waterfall_chart
from .plots_3d import scatter3d, surface3d
from .timeseries_plots import ts_line, rolling_mean
from .interactive_plots import interactive_scatter, interactive_map

PLOTS = {
    # basic
    "bar": bar_plot,
    "line": line_plot,
    "scatter": scatter_plot,
    "hist": histogram,
    "box": box_plot,
    "pie": pie_chart,
    "area": area_plot,
    # statistical
    "violin": violin_plot,
    "swarm": swarm_plot,
    "strip": strip_plot,
    "kde": kde_plot,
    # correlation
    "heatmap": correlation_heatmap,
    "pair": pair_plot,
    # advanced
    "hexbin": hexbin_plot,
    "bubble": bubble_plot,
    "radar": radar_chart,
    "waterfall": waterfall_chart,
    # 3d
    "scatter3d": scatter3d,
    "surface3d": surface3d,
    # time series
    "ts": ts_line,
    "rolling": rolling_mean,
    # interactive
    "scatter_int": interactive_scatter,
    "map": interactive_map,
}

def visualize(data, plot_type: str, **kwargs):
    """Unified entry point.

    Example:
        visualize(df, "scatter", x="sepal_length", y="sepal_width", hue="species")
    """
    if plot_type not in PLOTS:
        raise ValueError(f"Unsupported plot_type: {plot_type}. Choose one of: {sorted(PLOTS.keys())}")
    df = ensure_df(data)
    fn = PLOTS[plot_type]
    return fn(df, **kwargs)
