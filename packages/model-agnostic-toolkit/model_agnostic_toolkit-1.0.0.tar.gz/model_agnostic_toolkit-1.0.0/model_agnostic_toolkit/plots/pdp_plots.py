import math
import warnings

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from . import interaction_heatmap_plot
from .utils import colors, get_features, minmax, sample_indicators_1d


def pdp_line_plot(result: dict, title: str = 'PDP line plot', samples: bool = True, ice: bool = True,
                  max_num_samples: int = 1000, max_num_ice: int = 100, legend: bool = True) -> go.Figure:
    """Creates a line plot for PDP scores from given results, including sample indicators and individual conditional expectation curves.

    Args:
        result (Dict): Part of a PDP importance tool's result dictionary for a single feature.
        title (str, optional): Title for the plot. Defaults to 'PDP line plot'.
        samples (bool, optional): Whether to include sample indicators. Defaults to True.
        ice (bool, optional): Whether to include individual conditional expectation curves. Defaults to True.
        max_num_samples (int, optional): Maximal number of samples. Defaults to 1000.
        max_num_ice (int, optional): Maximum number of ICE curves to plot. Defaults to 100.
        legend (bool, optional): Whether to include a legend. Defaults to True.

    Returns:
        go.Figure: The generated PDP line plot.
    """

    feature, = get_features(result, filter=['scores', 'misc'])

    fig = go.Figure()

    # plot sample indicators as black lines
    if samples:
        y_min, y_max = minmax(result['scores'],
                              result['misc']['ice'] if ice else None)
        y = y_min - 0.1 * (y_max - y_min)
        samples = sample_indicators_1d(result['misc']['samples'], y=y, max_num_samples=max_num_samples, legend=legend)
        fig.add_trace(samples)

    # plot ICE lines
    if ice:
        ice_lines = result['misc']['ice']
        if len(ice_lines) > max_num_ice:  # only plot a random subset of ICE curves
            ice_lines = [ice_lines[i] for i in np.random.choice(max_num_ice, max_num_ice, replace=False)]
            warnings.warn('Not showing all ICE curves, only {max_num_ice} of them.'
                          .format(max_num_ice=max_num_ice), RuntimeWarning)
        for i, values in enumerate(ice_lines):
            ice_line = go.Scatter(x=result[feature], y=values, mode='lines', line_width=1,
                                  line_color='black', opacity=0.05, name='ICE', showlegend=(not i) if legend else False)
            fig.add_trace(ice_line)

    # plot scores
    line = go.Scatter(x=result[feature], y=result['scores'], line_color=colors(0), showlegend=legend, name='scores')
    fig.add_trace(line)

    # add plot and axis labeling
    fig.update_layout(
        title=title,
        xaxis_title=feature,
        yaxis_title='prediction'
    )

    return fig


def pdp_grid_plot(result: dict, title: str = 'PDP grid plot', n_cols: int = 3, samples: bool = True,
                  ice: bool = True) -> go.Figure:
    """Creates a grid of line plots for PDP scores from given results, including sample indicators and individual conditional expectation curves.

    Args:
        result (Dict): A PDP importance tool's result dictionary.
        title (str, optional): Title for the plot. Defaults to 'PDP grid plot'.
        n_cols (int, optional): Number of grid columns. Defaults to 3.
        samples (bool, optional): Whether to include sample indicators. Defaults to True.
        ice (bool, optional): Whether to include confidence intervals. Defaults to True.

    Returns:
        go.Figure: The generated PDP grid plot.
    """

    features = list(result.keys())
    n_features = len(features)

    # determine min and max values for y-axis
    y_min, y_max = minmax([result[f]['scores'] for f in features],
                          [result[f]['misc']['ice'] for f in features] if ice else None)
    pad = (y_max - y_min) * 0.1
    y_min, y_max = y_min - pad, y_max + pad

    # create subplots
    n_rows = math.ceil(n_features / n_cols)
    fig = make_subplots(rows=n_rows, cols=n_cols)

    for i, feature in enumerate(features):
        row = math.ceil((i + 1) / n_cols)
        col = i % n_cols + 1

        # create single PDP plot
        line_plot = pdp_line_plot(result[feature], feature, ice=ice, samples=False, legend=not i)

        # add sample indicators
        if samples:
            samples = sample_indicators_1d(result[feature]['misc']['samples'], y=y_min, legend=not i)
            fig.add_trace(samples, row=row, col=col)

        # add subplot to plot and adjust axes
        fig.add_traces(line_plot.data, rows=row, cols=col)
        fig.update_xaxes(title_text=feature, row=row, col=col)
        fig.update_yaxes(range=[y_min, y_max], row=row, col=col)
        if col == 1:
            fig.update_yaxes(title_text='prediction', row=row, col=col)

    fig.update_layout(title=title, height=100 + 250 * n_rows)

    return fig


def pdp_heatmap_plot(result: dict, title: str = 'PDP heatmap plot', show_colorbar: bool = True,
                     colorbar_title: str = 'prediction', transpose: bool = False) -> go.Figure:
    """Creates a heatmap plot for 3D pair interaction data from PDP results.

    Args:
        result (Dict): A PDP interaction tool's result dictionary for a single feature pair.
        title (str, optional): Title for the plot. Defaults to 'PDP heatmap plot'.
        show_colorbar (bool, optional): Whether to include a colorbar in the plot. Defaults to True.
        colorbar_title (str, optional): Title for the colorbar. Defaults to 'prediction'.
        transpose (bool, optional): Whether to transpose the heatmap plot, switching both axes. Defaults to False.

    Returns:
        go.Figure: The generated heatmap plot.
    """

    return interaction_heatmap_plot(result, title, show_colorbar, colorbar_title, transpose)
