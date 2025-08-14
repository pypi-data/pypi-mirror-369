import plotly.graph_objects as go

from .utils import get_features


def importance_bar_plot(result: dict, title: str = 'Importance bar plot', score_axis_title: str = 'feature importance',
                        horizontal: bool = True) -> go.Figure:
    """Creates a bar plot for 1D importance data from given results.

    Args:
        result (Dict): An importance tool's result dictionary with real values for each feature.
        title (str, optional): Title for the plot. Defaults to 'Importance bar plot'.
        score_axis_title (str, optional): Title for the score axis (usually x-axis). Defaults to 'feature importance'.
        horizontal (bool, optional): Whether the bars extend horizontally rather than vertically. Defaults to True.

    Returns:
        go.Figure: The generated importance bar plot.
    """

    features = get_features(result)

    # get corresponding scores
    scores = [result[f] for f in features]

    # create figure
    if horizontal:
        bars = go.Bar(x=scores, y=features, orientation='h')
    else:
        bars = go.Bar(x=features, y=scores, orientation='v')
    fig = go.Figure(bars)

    # adjust layout
    fig.update_layout(title=title)
    if horizontal:
        fig.update_layout(xaxis_title=score_axis_title)
    else:
        fig.update_layout(yaxis_title=score_axis_title)

    return fig


def importance_line_plot(result: dict, feature: str, title: str = 'Importance line plot',
                         y_axis_title: str = None) -> go.Figure:
    """Creates a line plot for 2D importance data from given results.

    Args:
        result (Dict): An importance tool's result dictionary with series of real values for both axes.
        feature (str): Name of the feature associated with the plot.
        title (str, optional): Title for the plot. Defaults to 'Importance line plot'.
        y_axis_title (str, optional): Title for the score axis (y-axis). Defaults to None.

    Returns:
        go.Figure: The generated importance line plot.
    """

    line = go.Scatter(x=result[feature], y=result['scores'])

    fig = go.Figure(line)

    fig.update_layout(
        title=title,
        xaxis_title=feature,
        yaxis_title=y_axis_title
    )

    return fig
