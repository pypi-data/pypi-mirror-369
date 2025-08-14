
import numpy as np
import pandas as pd
import psutil


def _check_feature(feature, df):
    """Make sure feature exists and infer feature type
    Feature types
    -------------
    1. binary
    2. onehot
    3. numeric
    """

    if type(feature) == list:
        if len(feature) < 2:
            raise ValueError('one-hot encoding feature should contain more than 1 element')
        if not set(feature) < set(df.columns.values):
            raise ValueError(f'feature does not exist: {str(feature)}')
        return 'onehot'
    else:
        if feature not in df.columns.values:
            raise ValueError(f'feature does not exist: {feature}')
        return (
            'binary'
            if sorted(list(np.unique(df[feature]))) == [0, 1]
            else 'numeric'
        )


def _check_dataset(df):
    """Make sure input dataset is pandas DataFrame"""
    if type(df) != pd.core.frame.DataFrame:
        raise ValueError('only accept pandas DataFrame')


def _make_list(x):
    """Make list when it is necessary"""
    return x if type(x) == list else [x]


def _check_model(model):
    """Check model input, return class information and predict function"""
    try:
        n_classes = len(model.classes_)
        predict = model.predict_proba
    except:
        n_classes = 0
        predict = model.predict

    return n_classes, predict


def _check_classes(classes_list, n_classes):
    """Makre sure classes list is valid
    Notes
    -----
    class index starts from 0
    """
    if len(classes_list) > 0 and n_classes > 2:
        if np.min(classes_list) < 0:
            raise ValueError('class index should be >= 0.')
        if np.max(classes_list) > n_classes - 1:
            raise ValueError('class index should be < n_classes.')


def _check_memory_limit(memory_limit):
    """Make sure memory limit is between 0 and 1"""
    if memory_limit <= 0 or memory_limit >= 1:
        raise ValueError('memory_limit: should be (0, 1)')


def _calc_memory_usage(df, total_units, n_jobs, memory_limit):
    """Calculate n_jobs to use"""
    unit_memory = df.memory_usage(deep=True).sum()
    free_memory = psutil.virtual_memory()[1] * memory_limit
    num_units = int(np.floor(free_memory / unit_memory))
    true_n_jobs = np.min([num_units, n_jobs, total_units])
    true_n_jobs = max(true_n_jobs, 1)
    return true_n_jobs


def _get_grids(feature_values, num_grid_points):
    """Calculate grid points for numeric feature
    Returns
    -------
    feature_grids: 1d-array
        calculated grid points
    """


    return np.linspace(
        np.min(feature_values), np.max(feature_values), num_grid_points
    )


def _find_onehot_actual(x):
    """Map one-hot value to one-hot name"""
    try:
        value = list(x).index(1)
    except:
        value = np.nan
    return value


def _get_string(x):
    if int(x) == x:
        return str(int(x))
    elif round(x, 1) == x:
        return str(round(x, 1))
    else:
        return str(round(x, 2))

