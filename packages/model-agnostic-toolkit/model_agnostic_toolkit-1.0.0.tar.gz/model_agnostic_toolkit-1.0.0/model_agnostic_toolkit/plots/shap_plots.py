import warnings

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from . import importance_bar_plot
from .utils import get_features, minmax


def shap_bar_plot(result: dict, title: str = 'SHAP bar plot') -> go.Figure:
    """Creates a bar plot for mean SHAP values from given results.

    Args:
        result ([type]): A SHAP importance tool's result dictionary.
        title (str, optional): Title for the plot. Defaults to 'SHAP bar plot'.

    Returns:
        go.Figure: The generated SHAP bar plot.
    """

    return importance_bar_plot(result, title=title, score_axis_title='mean absolute SHAP value')


def shap_beeswarm_plot(result: dict, title: str = 'SHAP beeswarm plot', max_num_samples: int = 250) -> go.Figure:
    """Creates a beeswarm plot for individual SHAP values from given results, including corresponding feature values.
    Plot is adapted from [here](https://github.com/slundberg/shap).

    Args:
        result (Dict): A SHAP importance tool's result dictionary.
        title (str, optional): Title for the plot. Defaults to 'SHAP beeswarm plot'.
        max_num_samples (int, optional): Maximum number of samples to show. Defaults to 250.

    Returns:
        go.Figure: The generated beeswarm plot.
    """

    fig = go.Figure()

    # get features and sample count
    feature_values = result['misc']['values']
    features = list(feature_values.keys())
    n_samples = len(list(feature_values.values())[0])

    if n_samples > max_num_samples:  # only plot a random subset of samples
        i_samples = np.random.choice(n_samples, max_num_samples, replace=False)
        warnings.warn('Not showing all samples, only {max_num_samples} of them.'
                      .format(max_num_samples=max_num_samples), RuntimeWarning)
    else:
        i_samples = np.arange(n_samples)

    for i, (feature, shap_values) in enumerate(result['misc']['shap_values'].items()):
        # jitter along y-axis
        jitter = 0.5 * (np.random.random_sample(len(i_samples)) - 0.5)

        # get feature values and their extrema for the colorbar
        values = feature_values[feature]
        cmin, cmax = minmax(values)

        # point color styling and colorbar
        markers = dict(
            cmin=cmin, cmax=cmax,
            color=values[i_samples],
            opacity=0.5,
            colorscale='Bluered',
            colorbar=dict(title='feature value', titleside='right', tickvals=[cmin, cmax], ticktext=['min', 'max']),
            showscale=(not i)
        )

        # plot the points for one feature
        points = go.Scatter(x=shap_values[i_samples], y=jitter + i, mode='markers',
                            marker=markers, showlegend=False, name=feature)

        fig.add_trace(points)

    # add feature names as ticklabels
    fig.update_yaxes(
        ticktext=features,
        tickvals=list(range(len(features))),
        showgrid=False,
        zeroline=False
    )

    fig.update_layout(
        title=title,
        xaxis_title='SHAP value'
    )

    return fig


def shap_summary_plot(result: dict, title: str = 'SHAP summary plot') -> go.Figure:
    """Creates a summary plot for SHAP values from given results, including both a bar plot and a beeswarm plot.

    Args:
        result (Dict): A SHAP importance tool's result dictionary.
        title (str, optional): Title for the plot. Defaults to 'SHAP summary plot'.

    Returns:
        go.Figure: The generated SHAP summary plot.
    """

    features = get_features(result)
    n_features = len(features)

    # create plots
    importance_plot = importance_bar_plot(result)
    beeswarm_plot = shap_beeswarm_plot(result)

    fig = make_subplots(rows=2, vertical_spacing=0.5)
    beeswarm_plot.data[0].marker.colorbar.update({
        'y': fig.layout.yaxis2.domain[0],
        'yanchor': 'bottom',
        'len': fig.layout.yaxis2.domain[1] - fig.layout.yaxis2.domain[0]
    })
    fig.add_traces(importance_plot.data, rows=1, cols=1)
    fig.add_traces(beeswarm_plot.data, rows=2, cols=1)

    # adjust importance plot
    fig.update_xaxes(title_text='mean absolute SHAP value', row=1, col=1)

    # adjust beeswarm plot
    fig.update_xaxes(title_text='SHAP value', row=2, col=1)
    fig.update_yaxes(
        ticktext=features,
        tickvals=list(range(n_features)),
        showgrid=False,
        zeroline=False,
        row=2, col=1
    )

    # adjust figure layout
    fig.update_layout(
        title=title,
        height=100 + 100 * n_features,
        showlegend=False
    )

    return fig
