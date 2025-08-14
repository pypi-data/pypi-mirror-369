

from .utils import (_check_model, _check_dataset, _check_feature, _check_memory_limit,
                    _make_list, _calc_memory_usage, _get_grids, _check_classes,
                    _get_string)
from ...datasets import Dataset
from model_agnostic_toolkit.model import Model

from .dsa_calc_utils import _predict_aggregate
from ..GlobalSensitivityAnalysis import dsa_calc_utils
from joblib.parallel import delayed
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from joblib import Parallel, delayed

class DSA(object):
    """Save dsa results

    n_classes: integer or None
        number of classes for classifier, None when it is a regressor
    dsa: dataframe
        sensitivity for each feature in feature_list
    """

    def __init__(self, n_classes, feature_list, dsa, sensitivity_measure):

        self._type = 'DSA_instance'
        self.n_classes = n_classes
        self.feature_list = feature_list
        self.dsa = dsa
        self.sensitivity_measure = sensitivity_measure


def dsa(model: Model, dataset: Dataset, model_features, feature_list, sensitivity_measure, sample_size=100, num_grid_points=5,
        memory_limit=0.5, n_jobs=1, predict_kwds=None):
    """Calculate DSA plot
    Parameters
    ----------
    model: a fitted sklearn model
    dataset: pandas DataFrame
        data set on which the model is trained
    model_features: list or 1-d array
        list of model features
    feature_list: list of features
    sensitivity_measure: string
        sensitivity measure for calculating DSA
    sample_size: int, default=100
        number of datapoints considered for calculation
    num_grid_points: integer, optional, default=5
        number of grid points for numeric feature
    memory_limit: float, (0, 1)
        fraction of memory to use
    n_jobs: integer, default=1
        number of jobs to run in parallel.
        make sure n_jobs=1 when you are using XGBoost model.
        check:
        1. https://pythonhosted.org/joblib/parallel.html#bad-interaction-of-multiprocessing-and-third-party-libraries
        2. https://github.com/scikit-learn/scikit-learn/issues/6627
    predict_kwds: dict, optional, default={}
        keywords to be passed to the model's predict function
    Returns
    -------
    dsa_out: instance of DSA
    """
    if not predict_kwds:
        predict_kwds = {}

    _check_memory_limit(memory_limit=memory_limit)

    # check function inputs
    n_classes, predict = _check_model(model=model)

    # avoid polluting the original dataset
    # copy training data set and get the model features
    # it's extremely important to keep the original feature order
    _check_dataset(df=dataset)
    _dataset = dataset.copy()

    # get random sample if sample size smaller than dataset, else keep dataset
    if sample_size < len(_dataset.index):
        _dataset =_dataset.sample(n=sample_size)

    # Parallel calculate Sensitivity
    true_n_jobs = _calc_memory_usage(
        df=_dataset, total_units=num_grid_points, n_jobs=n_jobs, memory_limit=memory_limit)
    sensitivity_per_feature = Parallel(n_jobs=true_n_jobs)(
        delayed(_dsa_feature)(
            _dataset=_dataset, model=model, model_features=model_features, n_classes=n_classes,
            sensitivity_measure=sensitivity_measure, num_grid_points= num_grid_points, 
            feature=feature, predict_kwds=predict_kwds)
        for feature in feature_list)
    # divide sensitivity response in list of sensitivities and list of features (new list necessary to ensure correct combination of feature and sensitivity)
    sens = [item[0] for item in sensitivity_per_feature]
    feat = [item[1] for item in sensitivity_per_feature]

    # calculate relative senisitiviy (all sensitivity measures add up to 1)
    relative_sensitivity_per_feature = np.divide(sens, np.sum(sens))

    sensitivity = pd.DataFrame(
        {'feature': feat,
         'sensitivity': relative_sensitivity_per_feature}
    )

    sensitivity = sensitivity.sort_values(by='sensitivity', ascending=False)

    pi_params = {'n_classes': n_classes, 'feature_list': feature_list}    
    
    dsa_out = DSA(dsa=sensitivity, sensitivity_measure=sensitivity_measure, **pi_params)

    return dsa_out


def _dsa_feature(model, _dataset, model_features, feature, sensitivity_measure, n_classes, num_grid_points, 
                 predict_kwds=None):

    if not predict_kwds:
        predict_kwds = {}

    feature_type = _check_feature(feature=feature, df=_dataset)

    # feature_grids: grid points to calculate on
    if feature_type == 'binary':
        feature_grids = np.array([0, 1])
    elif feature_type == 'onehot':
        feature_grids = np.array(feature)
    else:
        # calculate grid points for numeric features
        feature_grids = _get_grids(_dataset[feature].values, num_grid_points=num_grid_points)

    # get sensitivity values for each grid point
    grid_results = pd.DataFrame()
    class_frequencies = pd.DataFrame()
    for feature_grid in feature_grids:
        result = _predict_aggregate(
            feature_grid, data=_dataset, model=model, model_features=model_features, n_classes=n_classes,
            sensitivity_measure=sensitivity_measure, feature=feature, feature_type=feature_type, predict_kwds=predict_kwds)
        grid_results[feature_grid] = result[0]
        if result[1]:
            class_frequencies[feature_grid] = result[1]
    # aggregate class frequencies
    if n_classes!=0:
        class_frequencies = np.divide(class_frequencies.sum(axis=1).to_numpy(), len(feature_grids))
    # calculate sensitivity according to selected sensitivity measure    
    if sensitivity_measure == 'variance':
        sensitivity = grid_results.var(axis=1).to_numpy()
    elif sensitivity_measure == 'range':
        value_range = grid_results.max(axis=1) - grid_results.min(axis=1)
        sensitivity = value_range.to_numpy()
    elif sensitivity_measure == 'AAD':
        centered = grid_results.sub(grid_results.median(axis=1), axis=0)
        absolute = centered.apply(lambda x: x.abs())
        sensitivity = np.divide(absolute.sum(axis=1).to_numpy(),len(feature_grids))

    if n_classes==0:
        # aggregate sensitivity of min, mean and max
        sensitivity_aggregated = sensitivity.sum()/3
    else:
        # weight class sensitivities with class frequencies
        sensitivity_aggregated = sum(
            class_frequencies[i] * sensitivity[i]
            for i in range(int(len(class_frequencies)))
        )
    return [sensitivity_aggregated, feature]


def get_dsa(dsa_out):
    return dsa_out.dsa
