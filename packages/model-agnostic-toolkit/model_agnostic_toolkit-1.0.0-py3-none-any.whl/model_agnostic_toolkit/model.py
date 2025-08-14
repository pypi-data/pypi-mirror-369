import warnings
from typing import Callable

import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.exceptions import NotFittedError
from sklearn.utils.validation import check_is_fitted

from .datasets import Dataset
from .plots import model_scores_plot
from .types import DataType


class Model:
    """Wrapper class for models.
    Instantiates either a model of the provided model class or a gradient boosted tree instead.
    Be aware that the predict function has some special functionality described in its docstring.

    Attributes:
        data_type (DataType): Type of the model, which is either a classifier or a regressor.
        model ([type]): The actual underlying model.
        metrics (List[Callable]): List of callable metrics to use for evaluation.
        name (str): Name of the model.
    """

    def __init__(self, data_type: DataType, model_class: type = None, metrics: list[Callable] = None,
                 verbose: bool = True, name: str = None, *args, **kwargs) -> None:
        """Initializes common model wrapper.
        If no model is explicitly provided, creates a gradient boosted tree from xgboost (for regression) or a random forest from scikit-learn (for classifiction).

        Positional and keyworded arguments are passed to model initializer.

        Args:
            data_type (DataType): Type the data to work with, depending on what kind of output the model is meant to produce (either classification or regression).
            model_class (Type, optional): Model class to initialize and use for fitting and predicting if the gradient boosted tree does not suffice. Should be a class to be instantiated, not the instance itself. Needs to be a sklearn model or otherwise provide `fit(x, y)`, `predict(x)` (additionally `predict_proba(X)` in classification case), `score(x, y)` and `__sklearn_is_fitted__()` methods, in classification case additionally a classes_ attribute containing the class names ordered as in the `predict_proba(X)` result. Needs to adhere to data type, otherwise leads to unexpected behavior. Defaults to None.
            metrics (List[Callable], optional): List of metrics to use for evaluation. Expects callable functions taking target label and predicted label array-likes `y_true` and `y_pred` as `metric(y_true, y_pred)`. Works with `sklearn.metrics`, assuming the metric works for the specified data type (regression or classification). Defaults to None.
            verbose (bool, optional): Whether status messages should be printed or not. Defaults to True.
            name (str, optional): Name of the model. Defaults to None. If underlying model has a name attribute and no name is specified its name is set as the name els the name is set to 'model'.
        Raises:
            TypeError: Raised if metrics is not a list of callable functions.
            TypeError: Raised if data_type is not a DataType.
            TypeError: Raised if model_class is not the class type but an object instead.
        """

        self.data_type = data_type
        self.fitted = False
        self.classes = None
        if self.data_type == DataType.REGRESSION:
            self.class_idx: int = -1
        elif self.data_type == DataType.CLASSIFICATION:
            self.class_idx: int = 0

        # check passed metrics
        if isinstance(metrics, list) or metrics is None:
            self.metrics = metrics
        else:
            raise TypeError('Metrics must be a list of callable functions. Got a {actual_type} instead.'
                            .format(actual_type=type(metrics)))

        if model_class is None:
            # initialize gradient boosted tree or random forest
            if self.data_type == DataType.CLASSIFICATION:
                self.model = RandomForestClassifier(n_estimators=5, random_state=873)
            elif self.data_type == DataType.REGRESSION:
                self.model = xgb.XGBRegressor(*args, **kwargs, verbosity=0)
            else:
                raise TypeError('The data_type has to be a {expected_class}. Got a {actual_class} instead.'
                                .format(expected_class=DataType, actual_class=self.data_type.__class__))
        elif isinstance(model_class, type):
            self.model = model_class(*args, **kwargs)
        else:
            raise TypeError('The model_class should be the uninstantiated class. Got something else instead.')

        self._set_model_name(name)

        if verbose:
            print('Created {model}.'.format(model=self.model.__class__.__name__))

    def _set_model_name(self, name: str):
        """Set the name of the model based on the provided name, model attribute, or model type.

        Args:
            name (str, optional): The name to set for the model. If no name is provided the model name is inferred from the underlying model.

        Returns:
            None
        """

        if name:
            self.name = name
        elif hasattr(self.model, 'name'):
            self.name = self.model.name
        elif hasattr(type(self.model), '__name__'):
            self.name = type(self.model).__name__
        else:
            self.name = 'model'

    @property
    def set_class_index(self):
        """The index of the currently selected class considered for model prediction
        """
        return self.class_idx

    @set_class_index.setter
    def set_class_index(self, value: int):
        self.class_idx = value

    def fit(self, x, y, *args, **kwargs):
        """Calls the `fit(x, y)` method of the underlying model and returns its return.

        Args:
            x (array-like): Training data of shape (n_samples, n_features). May be a DataFrame.
            y (array-like): Target values of shape (n_samples, n_targets). May be a Series.

        Returns:
            Any: Return of model's `fit`-method. Underlying model for sklearn-based models.

        Raises:
            TypeError: If in classification case the model does not have a `classes_` attribute.
        """
        result = self.model.fit(x, y, *args, **kwargs)
        self.fitted = self.model._sklearn_fitted = True
        if self.data_type == DataType.CLASSIFICATION:
            if hasattr(self.model, 'classes_'):
                self.classes = self.model.classes_
            else:
                raise TypeError('The provided classification model has no classes_ attribute')
        return result

    def predict(self, x, *args, **kwargs):
        """Calls the `predict(x)` (regression case) or `predict_proba(x)` (classification case if available,
        else fallback to `predict(x)` method) method of the underlying model and returns the result.

        The instance attribute class_idx is used to trim the return value of the model's predict_proba(x) function.
        It can be set with set_class_index.
            Regression: Not relevant
            Classification: Defaults to -1
        If -1:
            complete results of `predict_proba(x)` are returned
        If -2:
            class index of the class with the highest probability per instance is returned
        Else:
            results of `predict_proba(x)` are trimmed to the class_idx


        Args:
            x (array-like): Sample data of shape (n_samples, n_features). Can be a DataFrame.

        Returns:
            array-like: Predicted target values of shape (n_samples, n_targets).

        Raises:
            ValueError: Raised if class_idx is out of range.
        """
        if self.data_type == DataType.CLASSIFICATION:
            try:
                prediction = self.model.predict_proba(x)
            except:
                warnings.warn('No predict_proba function available. Using predict.')
                warnings.warn('Be careful using the results. Most of the tools need predict_proba functionality to provide meaningful results.')
                print('Be careful using the results. Most of the tools need predict_proba functionality to provide meaningful results.')
                return self.model.predict(x, *args, **kwargs)

            if self.class_idx == -1:
                return prediction
            if self.class_idx == -2:
                return prediction.argmax(axis=1)
            try:
                return prediction[:, self.class_idx]
            except:
                raise ValueError('Given class index is out of range.')

        elif self.data_type == DataType.REGRESSION:
            return self.model.predict(x, *args, **kwargs)

    def score(self, x, y, *args, **kwargs):
        """Calls the `score(x, y)` method of the underlying model and returns the result.

        Args:
            x (array-like): Sample data of shape (n_samples, n_features). May be a DataFrame.
            y (array-like): Target values of shape (n_samples, n_targets). May be a Series.

        Returns
            float: Evaluation metric for the prediction. Usually R² score or mean accuracy.
        """

        return self.model.score(x, y, *args, **kwargs)

    def is_fitted(self):
        """Determines whether the model has already been fitted or not, but only for sklearn-based models.
        Other models need to override this method.
        """

        fitted = True
        try:
            check_is_fitted(self.model)
        except NotFittedError:
            fitted = False

        return fitted

    def evaluate(self, dataset: Dataset) -> dict[str, dict[str, float]]:
        """Evaluates model for every metric specified during initialization on both training and testing data.

        Args:
            dataset (Dataset): Dataset the evaluation is carried out on.

        Returns:
            Dict[str, Dict[str, float]]: Performance metric results for every metric and data split.
        """
        x_train, y_train = dataset.get_train()
        x_test, y_test = dataset.get_test()
        result = {}
        if self.metrics is not None:
            y_train_pred = self.model.predict(x_train)
            y_test_pred = self.model.predict(x_test)

            for metric in self.metrics:
                result[metric.__name__] = {'train': metric(y_train, y_train_pred)}
                result[metric.__name__]['test'] = metric(y_test, y_test_pred)

        else:
            score = _scores_dict[self.data_type]
            result[score] = {'train': self.score(x_train, y_train)}
            result[score]['test'] = self.score(x_test, y_test)
        return result

    @staticmethod
    def plot(result: dict[str, dict[str, float]], plot_config: dict = None) -> None:
        """Plots result of the model evaluation. This encompasses bar plots for every metric on both training and testing data.

        Args:
            result (Dict[str, Dict[str, float]]): Dictionary with performance metric results to plot.
            plot_config (Dict, optional): Configuration dictionary for Plotly's `show()` method ([reference](https://plotly.com/python/configuration-options/)). Defaults to None.
        """

        fig = model_scores_plot(result, title='Model Performance')
        fig.show(config=plot_config)


class PreloadedModel(Model):
    """Wrapper class for preloaded models.
    Manages a reference to the provided model.

    Attributes:
        fitted (bool): Whether the model has already been fitted or not.
    """

    def __init__(self, data_type: DataType, model: any, fitted: bool, metrics: list[Callable] = None,
                 verbose: bool = True, name: str = None, *args, **kwargs) -> None:
        """Initializes model wrapper for preloaded models.

        Args:
            data_type (DataType): Type of the data to work with, depending on what kind of output the model is meant to produce (either classification or regression).
            model (Any): The pre-instantiated model object. Needs to provide `fit(x, y)`, `predict(x)` and `score(x, y)` methods. Needs to be a sklearn model or otherwise provide `fit(x, y)`, `predict(x)` (additionally `predict_proba(X)` in classification case), `score(x, y)` and `__sklearn_is_fitted__()` methods, in classification case additionally a classes_ attribute containing the class names ordered as in the `predict_proba(X)` result. Needs to adhere to data type, otherwise leads to unexpected behavior. Needs to adhere to data type, otherwise leads to unexpected behavior.
            fitted (bool): Whether the provided model has already been fitted or not.
            metrics (List[Callable], optional): List of metrics to use for evaluation. Expects callable functions taking target label and predicted label array-likes `y_true` and `y_pred` as `metric(y_true, y_pred)`. Works with `sklearn.metrics`, assuming the metric works for the specified data type (regression or classification). Defaults to None.
            verbose (bool, optional): Whether status messages should be printed or not. Defaults to True.
            name (str, optional): Name of the model. Defaults to None. If underlying model has a name attribute and no name is specified its name is set as the name els the name is set to 'model'.
        Raises:
            TypeError: Raised if metrics is not a list of callable functions.
        """

        # set attributes
        super().__init__(data_type, metrics=metrics, verbose=verbose, *args, **kwargs)
        self.model = model
        self.fitted = fitted
        self.class_idx: int = -1

        # set model name
        if name:
            self.name = name
        elif hasattr(self.model, 'name'):
            self.name = self.model.name
        elif hasattr(type(self.model), '__name__'):
            self.name = type(self.model).__name__
        else:
            self.name = 'model'

        # ensure sklearn compatibility
        self.model._sklearn_fitted = fitted
        self.model.__sklearn_is_fitted__ = _sklearn_is_fitted.__get__(self.model)
        self.model._estimator_type = ('regressor' if data_type == DataType.REGRESSION else 'classifier')

        if self.data_type == DataType.CLASSIFICATION and self.model._sklearn_fitted:
            if hasattr(self.model, 'classes_'):
                self.classes = self.model.classes_
            else:
                raise TypeError('Provided classification model has no classes_ attribute.')
        # check passed metrics
        if isinstance(metrics, list) or metrics is None:
            self.metrics = metrics
        else:
            raise TypeError('Metrics must be a list of callable functions. Got a {actual_type} instead.'
                            .format(actual_type=type(metrics)))

        if verbose:
            print('Created {model}.'.format(model=self.model.__class__.__name__))


    def fit(self, x, y, *args, **kwargs):
        """Calls the `fit(x, y)` method of the underlying model sets the `fitted` attribute and returns its return.

        Args:
            x (array-like): Training data of shape (n_samples, n_features). May be a DataFrame.
            y (array-like): Target values of shape (n_samples, n_targets). May be a Series.

        Returns:
            Any: Return of model's `fit`-method. Underlying model for sklearn-based models.

        Raises:
            TypeError: If in classification case the model does not have a `classes_` attribute.
        """

        result = self.model.fit(x, y, *args, **kwargs)
        self.fitted = self.model._sklearn_fitted = True
        if self.data_type == DataType.CLASSIFICATION:
            if hasattr(self.model, 'classes_'):
                self.classes = self.model.classes_
            else:
                raise TypeError('The provided classification model has no classes_ attribute.')

        return result

    def is_fitted(self):
        """Determines whether the model has already been fitted or not.
        """

        return self.fitted

def _sklearn_is_fitted(self):
    """Makes information about whether a model is fitted available for scikit-learn functions.
    """

    return self._sklearn_fitted


_scores_dict = {
    DataType.CLASSIFICATION: 'accuracy_score',
    DataType.REGRESSION: 'r2_score'
}
