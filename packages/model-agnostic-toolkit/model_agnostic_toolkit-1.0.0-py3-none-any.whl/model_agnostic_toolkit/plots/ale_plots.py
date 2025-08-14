import math

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from . import interaction_heatmap_plot
from .utils import colors, get_features, minmax, sample_indicators_1d


def ale_line_plot(result: dict, title: str = 'ALE line plot', samples: bool = True, max_num_samples: int = 1000,
                  ci: bool = False, legend: bool = True) -> go.Figure:
    """Creates a line plot for ALE scores from given results, including sample indicators and confidence intervals.

    Args:
        result (Dict): Part of an ALE importance tool's result dictionary for a single feature.
        title (str, optional): Title for the plot. Defaults to 'ALE line plot'.
        samples (bool, optional): Whether to include sample indicators. Defaults to True.
        ci (bool, optional): Whether to include confidence intervals. Defaults to False.
        legend (bool, optional): Whether to include a legend. Defaults to True.
        max_num_samples (int, optional): Maximal number of samples considered. Defaults to 1000

    Returns:
        go.Figure: The generated ALE line plot.
    """

    feature, = get_features(result, filter=['scores', 'misc'])

    fig = go.Figure()

    # plot sample indicators as black lines
    if samples:
        y_min, y_max = minmax(result['scores'],
                              result['misc']['lower_ci'] if ci else None,
                              result['misc']['upper_ci'] if ci else None)
        y = y_min - 0.1 * (y_max - y_min)
        samples = sample_indicators_1d(result['misc']['samples'], y=y, max_num_samples=max_num_samples, legend=legend)
        fig.add_trace(samples)

    # plot 90% confidence interval
    if ci:
        confidence = int(100 * result['misc']['confidence'])
        lower_ci = go.Scatter(
            x=result[feature],
            y=result['misc']['lower_ci'],
            mode='lines',
            line_color=colors(0, 0),
            showlegend=False,
            name=f'{confidence}% CI',
        )
        upper_ci = go.Scatter(
            x=result[feature],
            y=result['misc']['upper_ci'],
            mode='none',
            fill='tonexty',
            fillcolor=colors(0, 0.1),
            showlegend=legend,
            name=f'{confidence}% CI',
        )
        fig.add_trace(lower_ci)
        fig.add_trace(upper_ci)

    # plot scores
    line = go.Scatter(x=result[feature], y=result['scores'], line_color=colors(0, 1), showlegend=legend, name='scores')
    fig.add_trace(line)

    # add plot and axis labeling
    fig.update_layout(
        title=title,
        xaxis_title=feature,
        yaxis_title='effect on prediction'
    )

    return fig


def ale_grid_plot(result: dict, n_cols: int = 3, title: str = 'ALE grid plot', samples: bool = True,
                  ci: bool = False) -> go.Figure:
    """Creates a grid of line plots for ALE scores from given results, including sample indicators and confidence intervals.

    Args:
        result (Dict): An ALE importance tool's result dictionary.
        n_cols (int, optional): Number of grid columns. Defaults to 3.
        title (str, optional): Title for the plot. Defaults to 'ALE grid plot'.
        samples (bool, optional): Whether to include sample indicators. Defaults to True.
        ci (bool, optional): Whether to include confidence intervals. Defaults to False.

    Returns:
        go.Figure: The generated ALE grid plot.
    """

    features = list(result.keys())
    n_features = len(features)

    # determine min and max values for y-axis
    y_min, y_max = minmax([result[f]['scores'] for f in features],
                          [result[f]['misc']['lower_ci'] for f in features] if ci else None,
                          [result[f]['misc']['upper_ci'] for f in features] if ci else None)
    pad = (y_max - y_min) * 0.1
    y_min, y_max = y_min - pad, y_max + pad

    # create subplots
    n_rows = math.ceil(n_features / n_cols)
    fig = make_subplots(rows=n_rows, cols=n_cols)

    for i, feature in enumerate(features):
        row = math.ceil((i + 1) / n_cols)
        col = i % n_cols + 1

        # create single ALE plot
        line_plot = ale_line_plot(result[feature], feature, ci=ci, samples=False, legend=not i)

        # add sample indicators
        if samples:
            samples = sample_indicators_1d(result[feature]['misc']['samples'], y=y_min, legend=not i)
            fig.add_trace(samples, row=row, col=col)

        # add subplot to plot and adjust axes
        fig.add_traces(line_plot.data, rows=row, cols=col)
        fig.update_xaxes(title_text=feature, row=row, col=col)
        fig.update_yaxes(range=[y_min, y_max], row=row, col=col)
        if col == 1:
            fig.update_yaxes(title_text='effect on prediction', row=row, col=col)

    fig.update_layout(title=title, height=100 + 250 * n_rows)

    return fig

def ale_heatmap_plot(result: dict, title: str = 'ALE heatmap plot', show_colorbar: bool = True,
                     colorbar_title: str = 'effect on prediction', transpose: bool = False) -> go.Figure:
    """Creates a heatmap plot for 3D pair interaction data from ALE results.

    Args:
        result (Dict): An ALE interaction tool's result dictionary for a single feature pair.
        title (str, optional): Title for the plot. Defaults to 'ALE heatmap plot'.
        show_colorbar (bool, optional): Whether to include a colorbar in the plot. Defaults to True.
        colorbar_title (str, optional): Title for the colorbar. Defaults to 'effect on prediction'.
        transpose (bool, optional): Whether to transpose the heatmap plot, switching both axes. Defaults to False.

    Returns:
        go.Figure: The generated heatmap plot.
    """

    fig = interaction_heatmap_plot(result, title, show_colorbar, colorbar_title, transpose)

    return fig
