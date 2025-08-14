from typing import Dict, List

import numpy as np
import pandas as pd

from . import dsa_utils
from .. import ImportanceTool
from ...analyzer import Analyzer
from ...datasets import Dataset
from ...model import Model
from ...plots import importance_bar_plot
from ...types import ResultType, DataType


class DSAImportance(ImportanceTool):
    """Tool for determining the databased sensitivity analysis (DSA) according to:
    Cortez, P.; Embrechts, M.: Opening black box Data Mining models
    using Sensitivity Analysis. In: 2011 IEEE Symposium on Computational
    Intelligence and Data Mining (CIDM). 1. ed., 2011, p. 341–348
    """

    def __init__(self, name: str = 'DSA Importance', sensitivity_measure: str = 'variance', n_jobs: int = 1, sample_size: int = 100, num_grid_points: int = 20, memory_limit: float = 0.5, **kwargs):
        """Initializes DSA Importance tool.

        Keyworded arguments are passed to the `permutation_importance` function from sklearn.

        Args:
            name (str, optional): Name of the tool. Defaults to 'DSA Importance'.
            sensitivity_measure (string, optional): Sensitivity measure for calculating DSA. Defaults to `variance`.
            sample_size (int, optional): Number of datapoints considered for calculation. Defaults to 100.
            num_grid_points (int, optional): Number of grid points for numeric feature. Defaults to 20.
            memory_limit (float, optional): Fraction of memory to use (between 0 and 1). Defaults to 0.5
            n_jobs (int, optional):
                Number of jobs to run in parallel. Defaults to 1 (no parallel computation).
                make sure n_jobs=1 when you are using XGBoost model.
                check:
                1. https://pythonhosted.org/joblib/parallel.html#bad-interaction-of-multiprocessing-and-third-party-libraries
                2. https://github.com/scikit-learn/scikit-learn/issues/6627
        """

        super().__init__(name, result_type=ResultType.DIM1)

        # set attributes
        self.sensitivity_measure = sensitivity_measure
        self.kwargs = kwargs
        self.n_jobs = n_jobs
        self.sample_size = sample_size
        self.num_grid_points = num_grid_points
        self.memory_limit = memory_limit

    def run(self, model: Model, dataset: Dataset, features: List[str], analyzer: Analyzer = None) -> Dict[str, float]:

        self.data_type = dataset.data_type
        super()._check_features(features=features, dataset=dataset)

        # get training data

        x_test, y_test = dataset.get_test()

        if self.data_type == DataType.REGRESSION:
            result = self._dsa_regression(features, model, x_test, y_test, dataset)
        else:
            result = self._dsa_classification(features, model, x_test, y_test, dataset)

        return result

    def _dsa_classification(self, features, model, x_test, y_test, dataset):
        classes = model.classes
        df_test, target = self._encode_target(classes, x_test, y_test)
        result = {
            class_index: {"class_label": class_label, 'result': {}}
            for class_index, class_label in enumerate(classes)
        }
        res = self._calculate_result(dataset, df_test, features, model)
        for class_index, class_label in enumerate(classes):
            for _, row in res.iterrows():
                result[class_index]['result'][row['feature']] = row['sensitivity']
        return result

    def _dsa_regression(self, features, model, x_test, y_test, dataset):
        # compute scores on training data
        df_test = pd.concat([x_test, y_test], axis=1)
        res = self._calculate_result(dataset, df_test, features, model)
        return {row['feature']: row['sensitivity'] for _, row in res.iterrows()}

    def _calculate_result(self, dataset, df_test, features, model):
        res = dsa_utils.dsa(model=model.model, dataset=df_test, feature_list=features, model_features=dataset.features,
                            sensitivity_measure=self.sensitivity_measure, sample_size=self.sample_size,
                            num_grid_points=self.num_grid_points, memory_limit=self.memory_limit, n_jobs=self.n_jobs)
        res = res.dsa
        res.sort_values(by='feature', key=lambda column: column.map(lambda e: features.index(e)), inplace=True)
        res.reset_index(inplace=True)
        return res

    @staticmethod
    def _encode_target(classes, x, y):
        one_hot_encoded = pd.DataFrame(columns=classes)
        for cls in classes:
            one_hot_encoded[cls] = y.where(y==cls, inplace=False).replace(cls, 1).replace(np.NaN, 0)
        # Concatenate the one-hot encoded columns with the original DataFrame
        y_concat = y.rename('target', inplace=False)
        df_encoded = pd.concat([y_concat, one_hot_encoded], axis=1)
        target = df_encoded.columns.to_list()
        return pd.concat([x, df_encoded], axis=1), target

    def plot(self, result: Dict, title: str = 'Data-based Sensitivity Analysis (DSA)', plot_config: Dict = None,
             **kwargs):

        fig = importance_bar_plot(result, title=title, **kwargs)
        fig.show(config=plot_config)

    @staticmethod
    def export_plot(result: Dict, title: str = 'Data-based Sensitivity Analysis (DSA)', **kwargs):

        return importance_bar_plot(result, title=title, **kwargs)
