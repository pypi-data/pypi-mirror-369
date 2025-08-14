import numpy as np
from plotly import graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import gaussian_kde

from .utils import colors, metrics_dict


def model_scores_plot(result: dict[str, dict[str, float]], title: str = 'Model scores plot') -> go.Figure:
    """Creates a group of barplots for every model performance metric in the result dictionary, including scores for both training and testing data.

    Args:
        result (Dict[str, Dict[str, float]]): The result dictionary from a model's evaluation.
        title (str, optional): Title for the plot. Defaults to 'Model scores plot'.

    Returns:
        go.Figure: The generated group of bar plots.
    """

    n_metrics = len(result.keys())
    fig = make_subplots(rows=n_metrics)

    # create barplot for every metric
    for i, (metric, scores) in enumerate(result.items()):
        x = [scores['train'], scores['test']]
        y = ['train', 'test']
        bars = go.Bar(x=x, y=y, orientation='h', name=metrics_dict[metric],
                      showlegend=False, marker=dict(color=[colors(0, 1), colors(1, 1)]))

        fig.add_trace(bars, row=i + 1, col=1)
        fig.update_xaxes(title_text=metrics_dict[metric], row=i + 1, col=1)

    # layout and size adjustments
    fig.update_layout(title=title, height=100 + 250 * n_metrics)

    return fig


def target_distributions_plot(y_true: np.array, y_pred: np.array,
                              title: str = 'Target distributions plot') -> go.Figure:
    """Creates two histogram plots with overlayed line plots, depicting the probability density of the ground truth target variable distribution against the predicted target variable distribution.

    Args:
        y_true (List[float]): Ground truth target samples.
        y_pred (List[float]): Predicted target samples.
        title (str, optional): Title for the plot. Defaults to 'Target distributions plot'.

    Returns:
        go.Figure: The generated distribution plot.
    """

    fig = go.Figure()

    # add histogram plots
    fig.add_trace(go.Histogram(x=y_true, histnorm='probability density', showlegend=False))
    fig.add_trace(go.Histogram(x=y_pred, histnorm='probability density', showlegend=False))
    fig.update_traces(opacity=0.25)
    fig.update_layout(barmode='overlay')

    # fit and sample kernel density estimation
    kde_true = gaussian_kde(y_true)
    kde_pred = gaussian_kde(y_pred)
    kde_true_x = np.linspace(y_true.min(), y_true.max(), 100)
    kde_pred_x = np.linspace(y_pred.min(), y_pred.max(), 100)
    kde_true_y = kde_true(kde_true_x)
    kde_pred_y = kde_pred(kde_pred_x)

    # add KDE line plots
    line_kde_true = go.Scatter(x=kde_true_x, y=kde_true_y, line_color=colors(0), name='target')
    line_kde_pred = go.Scatter(x=kde_pred_x, y=kde_pred_y, line_color=colors(1), name='prediction')
    fig.add_trace(line_kde_true)
    fig.add_trace(line_kde_pred)

    # layout adjustments
    fig.update_layout(title=title)

    return fig
