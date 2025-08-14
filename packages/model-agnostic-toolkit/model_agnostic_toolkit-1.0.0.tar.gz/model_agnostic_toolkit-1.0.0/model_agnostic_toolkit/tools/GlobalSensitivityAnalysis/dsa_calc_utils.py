
import pandas as pd
import numpy as np
from sklearn import metrics as metrics


def _predict_aggregate(feature_grid, data, model, model_features, n_classes, feature, feature_type,
                    sensitivity_measure, predict_kwds, unit_test=False):
    """Apply predict function on a feature_grid
    Returns
    -------
    Aggregated prediction and class_frequency in classification case
    """


    _data = data.copy()

    predict = model.predict if n_classes == 0 else model.predict_proba
    # modify data according to feature grid
    if feature_type == 'onehot':
        # for onehot encoding feature, need to change all levels together
        other_grids = [grid for grid in feature if grid != feature_grid]
        _data[feature_grid] = 1
        for grid in other_grids:
            _data[grid] = 0
    else:
        _data[feature] = feature_grid

    # get predictions for modified data
    preds = predict(_data[model_features], **predict_kwds)
    # aggregate predictions
    aggregation = _get_aggregation(preds, n_classes=n_classes)
    # calculate relative frequency of classes in dataset
    if n_classes > 0:
        df = pd.DataFrame(preds)
        # for each class get the number of rows where this class has highest probability
        class_frequency = df.idxmax(axis=1).value_counts(normalize=True)
        # if a class is not contained in the preds add it with class frequency 0
        for i in range(n_classes):
            if i not in class_frequency.index.values:
                series = pd.Series([0], index=[i])
                class_frequency = class_frequency.append(series)
        class_frequency = class_frequency.sort_index()
        class_frequency = class_frequency.tolist()
    else:
        class_frequency = None

    return [aggregation, class_frequency]


def _get_aggregation(preds, n_classes):
    return (
        [np.min(preds, axis=0), np.mean(preds, axis=0), np.max(preds, axis=0)]
        if n_classes == 0
        else np.mean(preds, axis=0)
    )
