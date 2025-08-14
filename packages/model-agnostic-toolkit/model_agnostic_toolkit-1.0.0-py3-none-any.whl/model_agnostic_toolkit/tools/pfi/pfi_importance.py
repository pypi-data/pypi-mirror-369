import warnings

from alibi.explainers import PermutationImportance
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_squared_log_error, \
    mean_absolute_percentage_error, r2_score, precision_score, recall_score, accuracy_score, log_loss, f1_score, \
    roc_auc_score

from .. import ImportanceTool
from ...analyzer import Analyzer
from ...datasets import Dataset
from ...model import Model
from ...plots import pfi_bar_plot
from ...types import ResultType, DataType


class PFIImportance(ImportanceTool):
    """Tool for determining the Permutation Feature Importance (PFI) for single features.
    Using implementation from [alibi](https://github.com/SeldonIO/alibi/).
    More information regarding PFI can be found at https://christophm.github.io/interpretable-ml-book/feature-importance.html.
    """

    def __init__(self, name: str = 'PFI Importance', n_repeats: int = 50, calculation_method: str = 'estimate',
                 evaluation_metric: str = None, kind: str = 'ratio', **kwargs) -> None:
        """Initializes PFI Importance tool.

        Keyworded arguments are passed to the `permutation_importance` function from sklearn.

        Args:
            name (str, optional): Name of the tool. Defaults to 'PFI Importance'.
            n_repeats (int, optional): Number of times to permute the feature values. Only applies if calculation_method is 'estimate'. Defaults to 50.
            calculation_method (str, optional): Whether to use 'exact' or 'estimate' method For more details see: [alibi](https://github.com/SeldonIO/alibi/blob/master/alibi/explainers/permutation_importance.py). Defaults to 'estimate'
            evaluation_metric (Union[List[str], str]), optional): Loss/score functions to apply.
                                                         Available functions are:
                                                            regression:
                                                                - mean_absolute_error (default)
                                                                - mean_squared_error
                                                                - root_mean_squared_error
                                                                - mean_squared_log_error
                                                                - mean_absolute_percentage_error
                                                                - r2
                                                            classification:
                                                                - log_loss (default)
                                                                - accuracy
                                                                . precision
                                                                - recall
                                                                - f1
                                                                - roc_auc
            kind (str, optional): Whether to report the importance as the loss/score 'ratio' or the loss/score 'difference'. Defaults to 'ratio'.
        """

        super().__init__(name, result_type=ResultType.DIM1)
        if kind not in ['ratio', 'difference']:
            raise ValueError('Kind has to be either "ratio" or "difference".')

        if calculation_method not in ['exact', 'estimate']:
            raise ValueError('Calculation method has to be either "exact" or "estimate".')
        # set attributes
        self.n_repeats = n_repeats
        self.calculation_method = calculation_method
        self.evaluation_metric = evaluation_metric
        self.kind = kind

        self.kwargs = kwargs

    def run(self, model: Model, dataset: Dataset, features: list[str], analyzer: Analyzer = None) -> dict:

        self.data_type = dataset.data_type
        super()._check_features(features=features, dataset=dataset)

        # get training data
        x_train, y_train = dataset.get_train()
        x_test, y_test = dataset.get_test()
        if self.data_type == DataType.REGRESSION:
            return self._pfi_regression(features, model, x_test, x_train, y_test, y_train, self.n_repeats,
                                        self.calculation_method, self.evaluation_metric, self.kind)
        else:
            return self._pfi_classification(features, model, x_test, x_train, y_test, y_train, self.n_repeats,
                                            self.calculation_method, self.evaluation_metric, self.kind)

    def _pfi_regression(self, features, model, x_test, x_train, y_test, y_train, n_repeats, calculation_method,
                        evaluation_metric, kind) -> dict:
        feature_names_res_test, feature_names_res_train, res_test, res_train = self._calculate_pfi(calculation_method,
                                                                                                   evaluation_metric,
                                                                                                   features, kind,
                                                                                                   model, n_repeats,
                                                                                                   x_test, x_train,
                                                                                                   y_test, y_train)
        if calculation_method == 'estimate':
            return self._store_estimate_regression_results(feature_names_res_test, feature_names_res_train, res_test,
                                                           res_train)
        else:
            return self._store_exact_regression_results(feature_names_res_test, feature_names_res_train, res_test,
                                                        res_train)

    @staticmethod
    def _store_exact_regression_results(feature_names_res_test, feature_names_res_train, res_test, res_train) -> dict:
        result = {
            f: res_train.data["feature_importance"][0][feature_names_res_train.index(f)]
            for f in feature_names_res_train
        }
        result['misc'] = {
            'test_importances': {
                f: res_test.data['feature_importance'][0][feature_names_res_test.index(f)] for f in
                feature_names_res_test
            }
        }
        return result

    @staticmethod
    def _store_estimate_regression_results(feature_names_res_test, feature_names_res_train, res_test, res_train) \
            -> dict:
        result = {
            f: res_train.data['feature_importance'][0][feature_names_res_train.index(f)]['mean'] for f in
            feature_names_res_train
        }
        result['misc'] = {
            'test_importances': {
                f: res_test.data['feature_importance'][0][feature_names_res_test.index(f)]['mean'] for f in
                feature_names_res_test
            },
            'train_stds': {
                f: res_train.data['feature_importance'][0][feature_names_res_train.index(f)]['std'] for f in
                feature_names_res_train
            },
            'test_stds': {
                f: res_test.data['feature_importance'][0][feature_names_res_test.index(f)]['std'] for f in
                feature_names_res_test
            }
        }
        return result

    def _calculate_pfi(self, calculation_method, evaluation_metric, features, kind, model, n_repeats, x_test, x_train,
                       y_test, y_train):
        if self.data_type == DataType.REGRESSION:
            score_fn, loss_fn = self._set_regression_metric(evaluation_metric)
        else:
            classes = model.classes
            score_fn, loss_fn = self._set_classification_metric(evaluation_metric, model, len(list(classes)))
        exp = PermutationImportance(model.predict, feature_names=features, score_fns=score_fn, loss_fns=loss_fn)
        try:
            res_train = exp.explain(x_train.to_numpy(), y_train.to_numpy(), method=calculation_method,
                                    kind=kind, n_repeats=n_repeats)
        except:
            warnings.warn(f'Could not generate explanation using calculation method "{calculation_method}"')
            if calculation_method == 'estimate':
                warnings.warn("Retrying with exact calculation.")
                res_train = exp.explain(x_train.to_numpy(), y_train.to_numpy(), method='exact', kind=kind,
                                        n_repeats=n_repeats)
        try:
            res_test = exp.explain(x_test.to_numpy(), y_test.to_numpy(), method=calculation_method, kind=kind,
                                   n_repeats=n_repeats)
        except:
            warnings.warn(
                f'Could not generate explanation using calculation method "{calculation_method}"'
            )
            if calculation_method == 'estimate':
                res_test = exp.explain(x_test.to_numpy(), y_test.to_numpy(), method='exact', kind=kind,
                                       n_repeats=n_repeats)

        feature_names_res_train = res_train.data["feature_names"]
        feature_names_res_test = res_test.data["feature_names"]
        return feature_names_res_test, feature_names_res_train, res_test, res_train

    def _pfi_classification(self, features, model, x_test, x_train, y_test, y_train, n_repeats, calculation_method,
                            evaluation_metric, kind) -> dict:
        feature_names_res_test, feature_names_res_train, res_test, res_train = self._calculate_pfi(calculation_method,
                                                                                                   evaluation_metric,
                                                                                                   features, kind,
                                                                                                   model, n_repeats,
                                                                                                   x_test, x_train,
                                                                                                   y_test, y_train)
        classes = model.classes
        if calculation_method == 'estimate':
            return self._store_estimate_classification_results(classes, feature_names_res_test, feature_names_res_train,
                                                               res_test, res_train)
        else:
            return self._store_exact_classification_results(classes, feature_names_res_test, feature_names_res_train,
                                                            res_test, res_train)

    @staticmethod
    def _store_exact_classification_results(classes, feature_names_res_test, feature_names_res_train, res_test,
                                            res_train) -> dict:
        result = {}
        for class_index, class_label in enumerate(classes):
            result[class_index] = {
                'class_label': class_label,
                'result': {
                    f: res_train.data['feature_importance'][0][
                        feature_names_res_train.index(f)
                    ]
                    for f in feature_names_res_train
                },
            }
            result[class_index]['result']['misc'] = {
                'test_importances': {
                    f: res_test.data['feature_importance'][0][feature_names_res_test.index(f)] for f in
                    feature_names_res_test
                }
            }
        return result

    @staticmethod
    def _store_estimate_classification_results(classes, feature_names_res_test, feature_names_res_train, res_test,
                                               res_train) -> dict:
        result = {}
        for class_index, class_label in enumerate(classes):
            result[class_index] = {
                'class_label': class_label,
                'result': {
                    f: res_train.data['feature_importance'][0][
                        feature_names_res_train.index(f)
                    ]['mean']
                    for f in feature_names_res_train
                },
            }
            result[class_index]['result']['misc'] = {
                'test_importances': {
                    f: res_test.data['feature_importance'][0][feature_names_res_test.index(f)]['mean'] for f in
                    feature_names_res_test
                },
                'train_stds': {
                    f: res_train.data['feature_importance'][0][feature_names_res_train.index(f)]['std'] for f in
                    feature_names_res_train
                },
                'test_stds': {
                    f: res_test.data['feature_importance'][0][feature_names_res_test.index(f)]['std'] for f in
                    feature_names_res_test
                }
            }
        return result

    def plot(self, result: dict, title: str = 'Permutation Feature Importance (PFI)', plot_config: dict = None,
             **kwargs) -> None:

        fig = pfi_bar_plot(result, title=title, **kwargs)
        fig.show(config=plot_config)

    @staticmethod
    def export_plot(result: dict, title: str = 'Permutation Feature Importance (PFI)', **kwargs):

        return pfi_bar_plot(result, title=title, **kwargs)

    @staticmethod
    def get_unique_elements(list1, list2) -> list:
        """
        check the elements of two list and make a list of all unique elements of both lists
        """
        combined_list = list1 + list2
        unique_list = []

        for element in combined_list:
            if element not in unique_list:
                unique_list.append(element)
        return unique_list

    @staticmethod
    def _set_regression_metric(evaluation_metric):
        # returns (score_fn, loss_fn). One will be set, the other will be None
        if not evaluation_metric or evaluation_metric == 'mean_absolute error':
            return None, mean_absolute_error
        elif evaluation_metric == 'mean_squared_error':
            return None, mean_squared_error
        elif evaluation_metric == 'root_mean_squared_error':
            metric = mean_squared_error
            metric.__kwdefaults__['squared'] = False
            return None, metric
        elif evaluation_metric == 'mean_squared_log_error':
            return None, mean_squared_log_error
        elif evaluation_metric == 'mean_absolute_percentage_error':
            return None, mean_absolute_percentage_error
        elif evaluation_metric == 'r2':
            return r2_score, None
        else:
            return NotImplementedError('The selected metric is not implemented. Select one of: mean_absolute_error '
                                       '(default), mean_squared_error, root_mean_squared_error, '
                                       'mean_squared_log_error, mean_absolute_percentage_error, r2')

    def _set_classification_metric(self, evaluation_metric, model, n_classes):
        # returns (score_fn, loss_fn). One will be set, the other will be None
        if not evaluation_metric or evaluation_metric == 'log_loss':
            model.set_class_index = -1
            return None, log_loss
        elif evaluation_metric == 'accuracy':
            model.set_class_index = -2
            return accuracy_score, None
        elif evaluation_metric == 'f1':
            model.set_class_index = -2
            metric = f1_score
            metric.__kwdefaults__['average'] = 'weighted'
            return metric, None
        elif evaluation_metric == 'precision':
            model.set_class_index = -2
            metric = precision_score
            metric.__kwdefaults__['average'] = 'weighted'
            return metric, None
        elif evaluation_metric == 'recall':
            model.set_class_index = -2
            metric = recall_score
            metric.__kwdefaults__['average'] = 'weighted'
            return metric, None
        elif evaluation_metric == 'roc_auc':
            if n_classes == 2:
                model.set_class_index = -2
                metric = roc_auc_score
            else:
                model.set_class_index = -1
                metric = roc_auc_score
                metric.__kwdefaults__['average'] = 'weighted'
                metric.__kwdefaults__['multi_class'] = 'ovr'
            return metric, None
        else:
            raise NotImplementedError('The selected metric is not implemented. Select one of: log_loss, accuracy, '
                                      'precision, recall, f1, roc_auc.')
