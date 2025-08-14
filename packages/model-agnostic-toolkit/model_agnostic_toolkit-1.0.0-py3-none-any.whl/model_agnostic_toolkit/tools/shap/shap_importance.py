import warnings

import numpy as np
import shap

from .. import ImportanceTool
from ...analyzer import Analyzer
from ...datasets import Dataset
from ...model import Model
from ...plots import shap_summary_plot
from ...types import DataType, ResultType


class SHAPImportance(ImportanceTool):
    """Tool for determining Shapley Additive Explanations (SHAP) for single features.
    Using implementation from (https://github.com/slundberg/shap).
    More information on SHAP can be found at https://christophm.github.io/interpretable-ml-book/shap.html.
    """

    def __init__(self, name: str = 'SHAP Importance', **kwargs) -> None:
        """Initializes SHAP Importance tool.

        Keyworded arguments are passed to the `Explainer` object from shap.

        Args:
            name (str, optional): Name of the tool. Defaults to 'SHAP Importance'.
        """

        super().__init__(name, result_type=ResultType.DIM1)

        # set attributes
        self.kwargs = kwargs

    def run(self, model: Model, dataset: Dataset, features: list[str], analyzer: Analyzer = None) -> dict[str, float]:

        self.data_type = dataset.data_type
        super()._check_features(features=features, dataset=dataset)

        # get data
        x_train, _ = dataset.get_train()
        x_test, _ = dataset.get_test()
        x_features = x_train.columns.to_list()
        if self.data_type == DataType.CLASSIFICATION:
            try:
                explainer = shap.Explainer(model.model.predict_proba, masker=x_train, **self.kwargs)
            except:
                warnings.warn('Model does not provide predict_proba function. Using predict function.')
                explainer = shap.Explainer(model.model.predict, masker=x_train, **self.kwargs)
        else:
            # compute scores
            explainer = shap.Explainer(model.model.predict, masker=x_train, **self.kwargs)
        shap_values = explainer(x_test).values

        dimension = shap_values.shape

        no_of_samples = dimension[0]
        res = np.mean(np.abs(shap_values), axis=0)

        result = {}

        if self.data_type == DataType.REGRESSION:
            self._store_regression_results(x_test, x_features, shap_values, features, res, result)

        else:
            self._store_classification_results(x_test, x_features, shap_values, features, model, no_of_samples, res,
                                               result)

        return result

    @staticmethod
    def _store_classification_results(x_test, x_features, shap_values, features, model, no_of_samples, res,
                                      result) -> None:
        classes = model.classes
        for class_index, class_label in enumerate(classes):

            result[class_index] = {"class_label": class_label, 'result': {}}
            result[class_index]['result']['misc'] = {'shap_values': {}, 'values': {}}
            for f in features:
                result[class_index]['result'][f] = res[x_features.index(f)][class_index]

            for f in features:
                result[class_index]['result']["misc"]['shap_values'][f] = []
                arr = np.array([])
                for i in range(no_of_samples):
                    arr = np.append(arr, shap_values[i][x_features.index(f)][class_index])
                    result[class_index]['result']["misc"]['shap_values'][f] = arr

            val = x_test.values
            for f in x_features:
                arr = np.array([])  # Create an empty NumPy array
                for i in range(no_of_samples):
                    arr = np.append(arr, val[i][x_features.index(f)])
                result[class_index]['result']['misc']['values'][f] = arr

    @staticmethod
    def _store_regression_results(x_test, x_features, shap_values, features, res, result) -> None:
        for f in features:
            result[f] = res[x_features.index(f)]
        result['misc'] = {
            'shap_values': {
                f: shap_values[:, x_features.index(f)] for f in features
            },
            'values': {
                f: x_test[f].to_numpy() for f in x_features
            }}

    def plot(self, result: dict, title: str = 'Shapley Additive Explanations (SHAP)', plot_config: dict = None,
             **kwargs) -> None:

        fig = shap_summary_plot(result, title=title)
        fig.show(config=plot_config)

    @staticmethod
    def export_plot(result: dict, title: str = 'Shapley Additive Explanations (SHAP)', **kwargs):

        return shap_summary_plot(result, title=title)
