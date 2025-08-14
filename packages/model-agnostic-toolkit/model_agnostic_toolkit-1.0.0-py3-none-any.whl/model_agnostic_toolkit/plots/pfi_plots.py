import plotly.graph_objects as go

from .utils import get_features


def pfi_bar_plot(result: dict, title: str = 'PFI bar plot', horizontal: bool = True) -> go.Figure:
    """Creates a bar plot for PFI scores from given results, including both training and testing data and standard deviations.

    Args:
        result (Dict): A PFI importance tool's result dictionary.
        title (str, optional): Title for the plot. Defaults to 'PFI bar plot'.
        horizontal (bool, optional): Whether the bars extend horizontally rather than vertically. Defaults to True.

    Returns:
        go.Figure: The generated PFI bar plot.
    """

    features = get_features(result)
    result_selection = {k: v for k, v in result.items() if k in features}

    train_scores = list(result_selection.values())
    test_scores = list(result['misc']['test_importances'].values())

    if 'train_stds' in result['misc']:
        train_stds = list(result['misc']['train_stds'].values())
    else:
        train_stds = [0] * len(train_scores)
    if 'test_stds' in result['misc']:
        test_stds = list(result['misc']['test_stds'].values())
    else:
        test_stds = [0] * len(test_scores)

    if horizontal:
        train_bars = go.Bar(x=train_scores, y=features, error_x_array=train_stds, orientation='h', name='train set')
        test_bars = go.Bar(x=test_scores, y=features, error_x_array=test_stds, orientation='h', name='test set')
    else:
        train_bars = go.Bar(x=train_scores, y=features, error_y_array=train_stds, orientation='v', name='train set')
        test_bars = go.Bar(x=test_scores, y=features, error_y_array=test_stds, orientation='v', name='test set')

    fig = go.Figure([train_bars, test_bars])

    fig.update_layout(
        barmode='group',
        title=title,
        xaxis_title='feature importance'
    )

    return fig
