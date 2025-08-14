from itertools import product
from typing import Union

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import norm

from .utils import colors, get_features, minmax, sample_indicators_2d


def interaction_bar_plot(result: dict, title: str = 'Interaction bar plot', max_num_bars: int = 10,
                         score_axis_title: str = 'feature interaction', horizontal: bool = True,
                         show_alpha_levels: Union[bool, list[float]] = False) -> go.Figure:
    """Creates bar plot for 1D interaction data from given results.

    Args:
        result (Dict): An interaction tool's result dictionary with real values for each feature pair.
        title (str, optional): Title for the plot. Defaults to 'Interaction bar plot'.
        max_num_bars (int, optional): Number of pairs to include in the plot, sorted by their interaction scores. Use `None` to include all pairs. Defaults to 10.
        score_axis_title (str, optional): Title for the score axis (usually x-axis). Defaults to 'feature interaction'.
        horizontal (bool, optional): Whether the bars extend horizontally rather than vertically. Defaults to True.
        show_alpha_levels (Union[bool, List[float]], optional): Whether to include alpha level indicators for a p-value significance test on all interaction values. Either True/False with default levels `[0.5, 0.25, 0.1, 0.05, 0.01]` or a list of custom levels. Defaults to False.

    Returns:
        go.Figure: The generated interaction bar plot.
    """

    feature_pairs = get_features(result)

    # get corresponding scores
    scores = np.array([result[f] for f in feature_pairs])

    # select top max_num_bars interacting feature pairs
    if max_num_bars is None:
        max_num_bars = len(feature_pairs)
    else:
        max_num_bars = min(max_num_bars, len(feature_pairs))
    selection = np.argsort(-scores)[:max_num_bars]
    selected_scores = scores[selection][::-1]
    selected_feature_pairs = [feature_pairs[i] for i in selection][::-1]

    feature_labels = [f'{f[0]} × {f[1]}' for f in selected_feature_pairs]

    # create figure
    if horizontal:
        bars = go.Bar(x=selected_scores, y=feature_labels, orientation='h')
    else:
        bars = go.Bar(x=feature_labels, y=selected_scores, orientation='v')
    fig = go.Figure(bars)

    # add confidence level indicator rectangles
    if show_alpha_levels:
        if isinstance(show_alpha_levels, list):
            alpha_levels = show_alpha_levels
        else:
            alpha_levels = [0.5, 0.25, 0.1, 0.05, 0.01]
        for alpha in alpha_levels:
            loc, scale = np.mean(scores), np.std(scores)
            cl = norm.isf(alpha, loc=loc, scale=scale)
            if horizontal:
                fig.add_vrect(0, cl, line_width=0, fillcolor=colors(0), opacity=0.1,
                              annotation_position='bottom right', annotation_text=f'α = {alpha}')
            else:
                fig.add_hrect(0, cl, line_width=0, fillcolor=colors(0), opacity=0.1,
                              annotation_position='top left', annotation_text=f'α = {alpha}')

    # adjust layout
    fig.update_layout(title=title)
    if horizontal:
        fig.update_layout(xaxis_title=score_axis_title)
    else:
        fig.update_layout(yaxis_title=score_axis_title)

    return fig


def interaction_matrix_plot(result: dict, title: str = 'Interaction matrix plot', colorbar_title: str = 'interaction',
                            full_matrix: bool = False) -> go.Figure:
    """Creates a matrix plot for 1D pair interaction data from given results.

    Args:
        result (Dict): An interaction tool's result dictionary with real values for each feature pair.
        title (str, optional): Title for the plot. Defaults to 'Interaction matrix plot'.
        colorbar_title(str, optional): Title for the colorbar. Defaults to 'interaction'.
        full_matrix (bool, optional): Whether to plot the full symmetric feature adjacency matrix as opposed to a reduced triangle version. Defaults to False.

    Returns:
        go.Figure: The generated interaction matrix plot.
    """

    feature_pairs = get_features(result)
    features = get_features(result, no_pairs=True)
    n_features = len(features)

    if full_matrix:
        # initialize score matrix
        scores = np.eye(n_features)
        for i in range(n_features):
            scores[i, i] = None

        # populate score matrix from results
        for f_a, f_b in feature_pairs:
            i = features.index(f_a)
            j = features.index(f_b)
            scores[i, j] = scores[j, i] = result[(f_a, f_b)]

        matrix = go.Heatmap(z=scores, x=features, y=features,
                            hoverongaps=False, colorbar=dict(title=colorbar_title, titleside='right'))

    else:
        # initialize score matrix
        scores = np.eye(n_features - 1)
        for i, j in product(range(n_features - 1), range(n_features - 1)):
            scores[i, j] = None

        # populate score matrix from results
        for f_a, f_b in feature_pairs:
            i = features.index(f_a)
            j = features[::-1].index(f_b)
            scores[i, j] = result[(f_a, f_b)]

        matrix = go.Heatmap(z=scores, x=features[1:][::-1], y=features[:-1],
                            hoverongaps=False, colorbar=dict(title=colorbar_title, titleside='right'))

    fig = go.Figure(matrix)

    fig.update_layout(title=title)

    return fig


def interaction_summary_plot(result: dict, title: str = 'Interaction summary plot') -> go.Figure:
    """Creates a summary plot for 1D pair interaction data from given results, including both a bar plot and matrix plot.

    Args:
        result (Dict): An interaction tool's result dictionary with real values for each feature pair.
        title (str, optional): Title for the plot. Defaults to 'Interaction summary plot'.

    Returns:
        go.Figure: The generated interaction summary plot.
    """

    feature_pairs = get_features(result)
    n_features = int(0.5 + np.sqrt(0.25 + 2 * len(feature_pairs)))  # number of features from number of pairs

    # create plots
    bar_plot = interaction_bar_plot(result, max_num_bars=n_features)
    heatmap_plot = interaction_matrix_plot(result)

    fig = make_subplots(rows=2, vertical_spacing=0.5)
    heatmap_plot.data[0].colorbar.update({
        'y': fig.layout.yaxis2.domain[0],
        'yanchor': 'bottom',
        'len': fig.layout.yaxis2.domain[1] - fig.layout.yaxis2.domain[0]
    })
    fig.add_traces(bar_plot.data, rows=1, cols=1)
    fig.add_traces(heatmap_plot.data, rows=2, cols=1)

    # adjust figure layout
    fig.update_xaxes(title_text='feature interaction', row=1, col=1)
    fig.update_layout(
        title=title,
        height=100 + 100 * n_features
    )

    return fig


def interaction_heatmap_plot(result: dict, title: str = 'Interaction heatmap plot', show_colorbar: bool = True,
                             colorbar_title: str = 'interaction effect', transpose: bool = False, samples: bool = True,
                             legend: bool = True, z_minmax: tuple[float, float] = None) -> go.Figure:
    """Creates a heatmap plot for 3D pair interaction data from ALE or PDP results.

    Args:
        result (Dict): An ALE or PDP interaction tool's result dictionary for a single feature pair.
        title (str, optional): Title for the plot. Defaults to 'Interaction heatmap plot'.
        show_colorbar (bool, optional): Whether to include a colorbar in the plot. Defaults to True.
        colorbar_title (str, optional): Title for the colorbar. Defaults to 'interaction effect'.
        transpose (bool, optional): Whether to transpose the heatmap plot, switching both axes. Defaults to False.
        samples (bool, optional): Whether to include sample indicators. Defaults to True.
        legend (bool, optional): Whether to include a legend. Defaults to True.
        z_minmax (Tuple[float, float], optional): Minimum and maximum values for the z-axis, adjusting the colorbar. Defaults to None.

    Returns:
        go.Figure: The generated interaction heatmap plot.
    """

    f_a, f_b = get_features(result, filter=['scores', 'misc'])

    # retrieve scores
    if transpose:
        x = result[f_b]
        y = result[f_a]
        z = result['scores']
    else:
        x = result[f_a]
        y = result[f_b]
        z = result['scores'].T

    # create plot
    heatmap = go.Heatmap(x=x, y=y, z=z, zsmooth='best', showscale=show_colorbar,
                         colorbar=dict(title=colorbar_title, titleside='right'),
                         zmin=(z_minmax[0] if z_minmax is not None else None),
                         zmax=(z_minmax[1] if z_minmax is not None else None))
    fig = go.Figure(heatmap)

    # add sample indicators
    if samples:
        samples = sample_indicators_2d(
            result['misc']['samples'], flip=transpose, legend=legend
        )
        fig.add_traces([samples])

    # adjust layout
    fig.update_xaxes(range=minmax(x))
    fig.update_yaxes(range=minmax(y))
    fig.update_layout(
        title=title,
        xaxis_title=f_a,
        yaxis_title=f_b
    )

    return fig


def interaction_heatmap_matrix_plot(result: dict, title: str = 'Interaction heatmap matrix plot',
                                    shared_colorbar: bool = True, colorbar_title: str = 'interaction effect',
                                    samples: bool = True, legend: bool = True) -> go.Figure:
    """Creates a matrix of heatmap plots for 3D pair interaction data from ALE or PDP results.

    Args:
        result (Dict): An ALE or PDP interaction tool's result dictionary with a matrix for each feature pair.
        title (str, optional): Title for the plot. Defaults to 'Interaction heatmap grid plot'.
        shared_colorbar (bool, optional): Whether to share the colorbar across all heatmap plots. Defaults to True.
        colorbar_title (str, optional): Title for the colorbar. Defaults to 'interaction effect'.
        samples (bool, optional): Whether to include sample indicators. Defaults to True.
        legend (bool, optional): Whether to include a legend. Defaults to True.

    Returns:
        go.Figure: The generated interaction heatmap matrix plot.
    """

    feature_pairs = get_features(result)

    # get feature numbers and grid cells
    temp_features = [feature_pair[0] for feature_pair in feature_pairs]
    temp_features.extend([feature_pair[1] for feature_pair in feature_pairs])
    features = list(dict.fromkeys(temp_features))
    n_features = len(features)

    # create subplots
    fig = make_subplots(rows=n_features - 1, cols=n_features - 1, shared_xaxes=True, shared_yaxes=True)

    if shared_colorbar:
        values = []
        for f in feature_pairs:
            try:
                values.append(result[f]['scores'])
            except:
                raise ValueError(f"Interaction {f} is not available. Try another ordering of the features.")
        z_minmax = minmax(values)
    else:
        z_minmax = None

    # prefill subplots with empty plots
    for feature_x, feature_y in product(features[:-1], features[1:]):
        col, row = features.index(feature_x) + 1, features.index(feature_y)
        fig.add_traces([{}], rows=row, cols=col)
        if col == 1:
            fig.update_yaxes(title_text=feature_y, row=row, col=col)
        if row == n_features - 1:
            fig.update_xaxes(title_text=feature_x, row=row, col=col)

    for i, feature_pair in enumerate(feature_pairs):
        f_x, f_y = feature_pair
        col, row = features.index(f_x) + 1, features.index(f_y)
        show_colorbar = (shared_colorbar and not i)

        # create and add plot
        heatmap_plot = interaction_heatmap_plot(result[feature_pair], transpose=False, samples=samples,
                                                colorbar_title=colorbar_title, show_colorbar=show_colorbar,
                                                legend=(legend and not i), z_minmax=z_minmax)
        if show_colorbar:
            heatmap_plot.data[0].colorbar.update({
                'y': 0,
                'yanchor': 'bottom',
                'len': 0.95
            })
        fig.add_traces(heatmap_plot.data, rows=row, cols=col)

        fig.update_xaxes(range=minmax(result[feature_pair][f_x]), row=row, col=col)
        fig.update_yaxes(range=minmax(result[feature_pair][f_y]), row=row, col=col)

    fig.update_layout(
        title=title,
        height=100 + 200 * (n_features - 1),
        width=100 + 200 * (n_features - 1)
    )
    fig.update_layout(plot_bgcolor="white")
    return fig
