import warnings
from collections.abc import Iterable
from typing import Union, Generator

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def sample_indicators_1d(x_samples: list[float], y: float = 0, max_num_samples: int = 1000, jitter: float = 0.02,
                         flip: bool = False, legend: bool = False) -> go.Scatter:
    """Creates a 1D scatter plot of markers as sample indicators for ALE or PDP line plots.

    Args:
        x_samples (List[float]): List of 1D samples to indicate the position of.
        y (float, optional): Y-level to plot the indicators at. Defaults to 0.
        max_num_samples (int, optional): Maximum number of samples to indicate. Defaults to 1000.
        jitter (float, optional): Relative amount of jitter to add to the sample indicators. Defaults to 0.02.
        flip (bool, optional): Whether to flip x- and y-axis for the indicators. Defaults to False.
        legend (bool, optional): Whether to include sample indicators in the legend. Defaults to False.

    Returns:
        go.Scatter: The generated scatter trace with sample indicators.
    """

    # prepare array
    x_samples = x_samples.astype(float)

    # add jitter for visibility
    x_min, x_max = minmax(x_samples)
    if len(x_samples) > max_num_samples:  # only plot a random subset of sample indicators
        x_samples = np.random.choice(x_samples, max_num_samples, replace=False)
        warnings.warn('Not showing all sample indicators, only {max_num_samples} of them.'
                      .format(max_num_samples=max_num_samples), RuntimeWarning)
    jitter_samples = (x_max - x_min) * jitter * (np.random.random_sample(len(x_samples)) - 0.5)
    x_samples += jitter_samples

    if not flip:
        x_vals = x_samples
        y_vals = np.full(len(x_vals), y)
    else:
        y_vals = x_samples
        x_vals = np.full(len(y_vals), y)

    marker_symbol = 'line-ew' if flip else 'line-ns'

    return go.Scatter(
        x=x_vals,
        y=y_vals,
        hoverinfo='skip',
        mode='markers',
        marker_symbol=marker_symbol,
        marker_line_width=1,
        marker_line_color='rgba(0,0,0,0.1)',
        showlegend=legend,
        name='samples',
    )


def sample_indicators_2d(xy_samples: list[list[float]], max_num_samples: int = 1000, jitter: float = 0.02,
                         flip: bool = False, legend: bool = False) -> go.Scatter:
    """Creates a 2D scatter plot of markers as sample indicators for ALE or PDP heatmap plots.

    Args:
        xy_samples (List[List[float]]): List of 2D samples to indicate the position of.
        max_num_samples (int, optional): Maximum number of samples to indicate. Defaults to 1000.
        jitter (float, optional): Relative amount of jitter to add to the sample indicators. Defaults to 0.02.
        flip (bool, optional): Whether to flip x- and y-axis for the indicators. Defaults to False.
        legend (bool, optional): Whether to include sample indicators in the legend. Defaults to False.

    Returns:
        go.Scatter: The generated scatter trace with sample indicators.
    """

    # prepare array
    xy_samples = xy_samples.astype(float)

    # add jitter for visibility
    x_min, x_max = minmax(xy_samples[:, 0])
    y_min, y_max = minmax(xy_samples[:, 1])
    if len(xy_samples) > max_num_samples:  # only plot a random subset of sample indicators
        choice = np.random.choice(len(xy_samples), max_num_samples, replace=False)
        xy_samples = xy_samples[choice]
        warnings.warn('Not showing all sample indicators, only {max_num_samples} of them.'
                      .format(max_num_samples=max_num_samples), RuntimeWarning)
    jitter_samples = jitter * (np.random.random_sample((len(xy_samples), 2)) - 0.5)
    jitter_samples[:, 0] *= (x_max - x_min)
    jitter_samples[:, 1] *= (y_max - y_min)
    xy_samples += jitter_samples

    if not flip:
        x_vals = xy_samples[:, 0]
        y_vals = xy_samples[:, 1]
    else:
        y_vals = xy_samples[:, 0]
        x_vals = xy_samples[:, 1]

    return go.Scatter(
        x=x_vals,
        y=y_vals,
        hoverinfo='skip',
        mode='markers',
        marker_symbol='cross-thin',
        marker_line_width=1,
        marker_line_color='rgba(0,0,0,0.1)',
        showlegend=legend,
        name='samples',
    )


def minmax(*args) -> tuple[float, float]:
    """Evaluates minimum and maximum numerical values over all given list, arrays, etc.

    Returns:
        Tuple[Real, Real]: Minimum and maximum numerical values.
    """

    args = [arg for arg in args if arg is not None]
    values = list(_flatten(args))

    return np.nanmin(values), np.nanmax(values)


def _flatten(iterable: Iterable) -> Generator:
    """Flattens an iterable of lists, arrays, etc. into a single 1D generator.

    Args:
        iterable (Iterable): List of lists, arrays, etc. to flatten.

    Yields:
        Generator: All non-iterable items from given lists, arrays, etc.
    """

    for item in iterable:
        if isinstance(item, Iterable) and not isinstance(item, str):
            yield from _flatten(item)
        else:
            yield item


def colors(i: int, alpha: float = 1.0) -> str:
    """Provides default Plotly colors for a given index `i` and opacity `alpha` as RGBA colors.

    Args:
        i (int): Index of default color to access. Must be in [0, 9], as there are 10 colors.
        alpha (float, optional): Target opacity for the color. Defaults to 1.0.

    Returns:
        str: The RGBA color with given opacity.
    """

    return _hex_to_rgba(default_colors[i], alpha)


def _hex_to_rgba(h: str, alpha: float = 1.0) -> str:
    """Converts a HEX color to an RGBA color with given opacity `alpha`.

    Args:
        h (str): HEX color of the form `'#RRGGBB'`.
        alpha (float): Target opacity for the RGBA color. Must be in [0, 1].

    Returns:
        str: The RGBA color with given opacity.
    """

    values = tuple([int(h.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)] + [alpha])

    return f'rgba{values}'


def get_features(result: dict, filter: list[str] = None, no_pairs: bool = False) -> list[Union[str, tuple[str, str]]]:
    """Retrieves features or feature pairs from a results dictionary without the specified keys.

    Args:
        result (dict): Result dictionary to extract features from.
        filter (List[str], optional): List of keys to filter. Defaults to ['misc'].
        no_pairs (bool, optional): Whether to return single features only and deconstruct pairs. Defaults to False.

    Returns:
        List: The result's features or feature pairs, excluding the specified keys.
    """

    if filter is None:
        filter = ['misc']
    features = list(result.keys())
    for key in filter:
        if key in features:
            features.remove(key)

    if no_pairs:
        features = list(_flatten(features))
        features = list(pd.unique(features))

    return features


# Plotly `show()` configuration for SVG image download
plot_config_svg = {
    'toImageButtonOptions': {
        'format': 'svg'  # one of png, svg, jpeg, webp
    }
}

# Plotly default colors in HEX format
default_colors = px.colors.qualitative.Plotly

# axis labels for different evaluation metrics in model performance plots
metrics_dict = {
    'accuracy_score': 'accuracy',
    'balanced_accuracy_score': 'balanced accuracy',
    'top_k_accuracy_score': 'top-k accuracy',
    'average_precision_score': 'average precision',
    'brier_score_loss': 'Brier score loss',
    'f1_score': 'F₁ score',
    'log_loss': 'log loss',
    'precision_score': 'precision',
    'recall_score': 'recall',
    'jaccard_score': 'Jaccard score',
    'roc_auc_score': 'ROC AUC score',

    'explained_variance_score': 'explained variance',
    'max_error': 'maximum residual error',
    'mean_absolute_error': 'mean absolute error',
    'mean_squared_error': 'mean squared error',
    'mean_squared_log_error': 'mean squared log error',
    'median_absolute_error': 'median absolute error',
    'r2_score': 'R² score',
    'mean_poisson_deviance': 'mean Poisson deviance',
    'mean_gamma_deviance': 'mean gamma deviance',
    'mean_absolute_percentage_error': 'mean absolute percentage error'
}
