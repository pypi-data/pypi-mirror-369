from abc import ABC, abstractmethod
from numbers import Real
from typing import Union

import numpy as np

from ..analyzer import Analyzer
from ..datasets import Dataset
from ..model import Model
from ..types import ToolType, ResultType, DataType


class Tool(ABC):
    """Base Class for all tools.
    Each tool executes an analysis for a given model and dataset.
    (abstract base class, derive)

    Attributes:
        name (str): Name of the tool.
        tool_type (ToolType): Type of analysis the tool is used for (either importance or interaction).
        result_type (ResultType): Type of result output by the tool, depending on output data dimensionality.
        data_type (DataType): Type of the problem: regression or classification.
    """

    def __init__(self, name: str, tool_type: ToolType, result_type: ResultType) -> None:
        """Initializes abstract base of tool with given name, tool type and result type.

        Args:
            name (str): Name of the tool.
            tool_type (ToolType): Type of analysis the tool is used for (either importance or interaction).
            result_type (ResultType): Type of result output by the tool, depending on output data dimensionality.
        """

        # set attributes
        self.name = name
        self.tool_type = tool_type
        self.result_type = result_type
        self.data_type = None

    @abstractmethod
    def run(
        self,
        model: Model,
        dataset: Dataset,
        features: Union[list[str], list[tuple[str, str]]],
        analyzer: Analyzer = None,
        **kwargs,
    ) -> dict:
        """Runs the tool on a given model and dataset for the specified target features and returns the computed results.
        (abstract method, override)

        Expected result format is a dictionary with features as keys.
        The format of corresponding values is different for each result type.
        Expected feature result formats for these types are the following:

        1. `ResultType.DIM1`:
        `Real` (for one feature or feature pair only):
        Single scalar real value.

        2. `ResultType.DIM2`:
        `Dict[str, np.ndarray[Real]]` (for one feature only):
        Dictionary with two keys, the feature name and 'score', each with a 1D np.ndarray of real values as their value.
        Arrays have the same length.
        An optional third key 'misc' may have a dictionary with additional information as its value.

        3. `ResultType.DIM3`:
        `Dict[str, np.ndarray[Real]` (for one feature pair only):
        Dictionary with three keys, the two feature names and 'score'.
        The first two feature keys have a 1D np.ndarray of real values as their value.
        The 'score' key has a 2D np.ndarray of real values as its value.
        The number of values in scores is the product of feature array lengths.
        An optional fourth key 'misc' may have a dictionary with additional information as its value.

        In classification case the results of each class are merged into one dictionary using the following structure:
        {
            <class_index>: {'class_label':  <class_label>, 'result':  <one- to three-dimensional result>},
            <class_index>: {'class_label':  <class_label>, 'result':  <one- to three-dimensional result>},
        }

        Args:
            model (Model): Model to use for the analysis.
            dataset (Dataset): Dataset to use for the analysis.
            features (Union[List[str], List[Tuple[str, str]]]): List of features to run the analysis tool for. At least two features are to be given.
            analyzer: (Analyzer, optional): Analyzer the tool is run from. Defaults to None.

        Returns:
            Dict: Dictionary of the computed results, following the format specified above.
        """

        pass

    def plot(
        self, result: dict, title: str = None, plot_config: dict = None, **kwargs
    ) -> None:
        """Creates and shows one or multiple plots of the given results for this tool.
        Plots created here are also included in the analysis report.
        (override)

        Keyworded arguments are passed to the respective plotting functions.

        Args:
            result (Dict): Results saved by the analyzer from running this tool.
            title (str): Title of the plot.
            plot_config (Dict, optional): Configuration dictionary for Plotly's `show()` method (https://plotly.com/python/configuration-options/). Defaults to None.

        Raises:
            NotImplementedError: Raised if plotting is not implemented in derived tools.
        """

        raise NotImplementedError()

    def export_plot(
        self, result: dict, title: str = None, plot_config: dict = None, **kwargs
    ) -> None:
        """Returns one or multiple plots of the given results for this tool.

        Keyworded arguments are passed to the respective plotting functions.

        Args:
            result (Dict): Results saved by the analyzer from running this tool.
            title (str): Title of the plot.
            plot_config (Dict, optional): Configuration dictionary for Plotly's `show()` method (https://plotly.com/python/configuration-options/). Defaults to None.

        Raises:
            NotImplementedError: Raised if plotting is not implemented in derived tools.
        """

        raise NotImplementedError()

    def _check_features(
        self, features: list[Union[str, tuple[str, str]]], dataset: Dataset
    ) -> None:
        """Check if the passed features are within the dataset.

        Args:
            dataset (Dataset): Dataset to use for the analysis.
            features (List[Union[str, Tuple[str, str]]]): Feature to analyze
        Raises:
            ValueError: Raised if the features are not contained in the dataset or do not meet the requirements (not at least two features, ...)
        """

        x_data, _ = dataset.get_all()
        x_features = list(x_data.columns)
        if any(item not in x_data for item in x_features):
            raise ValueError("Not all given features are contained in the dataset")
        if len(features) < 2:
            raise ValueError("At least two features have to be given")

    def _check_result_format(self, result: dict, features: list[Union[str, tuple[str, str]]]) -> None:
        """Checks if the passed result adheres to the expected format for this tool's result type.
        The Analyzer checks the output of the `run`-function here.

        Args:
            result (Dict): Result to check the form of.
            features (List[Union[str, Tuple[str, str]]]): Feature the passed result is the result for.

        Raises:
            AssertionError: Raised if any of the expected result format properties are not met.
            ValueError: Raised if the tool's result type is not expected/supported.
        """
        try:
            assert isinstance(result, dict), f"Result is of type {type(result)}. Expected a dict."

            if self.data_type == DataType.REGRESSION:
                # check regression results
                self._check_result_format_regression(features, result, accepted_result_types=
                                                     [ResultType.DIM1, ResultType.DIM2, ResultType.DIM3])
            else:
                # check classification results
                self._check_result_format_classification(features, result)

        except Exception as e:
            # append tool in error message
            e.args = (f'{e.args[0]} Tool: {self.name}.',)
            raise e

    def _check_result_format_classification(self, features, result) -> None:
        # check that the aggregation of the results of the different classes is correct
        class_indices = list(result.keys())
        assert all(
            isinstance(class_index, int) for class_index in class_indices
        ), 'Not all class indices are of expected type. Expected int'
        for class_index in class_indices:
            class_result = result[class_index]
            class_result_num_keys = len(list(class_result.keys()))
            assert class_result_num_keys == 2, (
                f'Expected exactly two keys for class result. Result of class with index {class_index} has '
                f'{class_result_num_keys} keys.'
            )
            assert (
                'class_label' in class_result
            ), f'Result of class index {class_index} is missing key "class_label".'
            assert (
                'result' in class_result
            ), f'Result of class index {class_index} is missing key "result".'
            # results of one single class are stored as regression results
            self._check_result_format_regression(features, class_result['result'],
                                                 accepted_result_types=[ResultType.DIM1, ResultType.DIM2,
                                                                        ResultType.DIM3])

    def _check_result_format_regression(self, features, result, accepted_result_types) -> None:
        # expected format is a dictionary with features as keys
        # expected feature format is a str for importance tools or a Tuple[str, str] for interaction tools
        # optional additional key is 'misc' and its value a Dict
        assert isinstance(
            result, dict
        ), f'Result is of type {type(result)}. Expected a dict.'
        assert isinstance(
            features, list
        ), f'Features are of type {type(features)}. Expected a list.'
        if self.tool_type == ToolType.IMPORTANCE:

            assert all(
                isinstance(f, str) for f in features
            ), 'Not all passed features for importance tool are of type str.'

        elif self.tool_type == ToolType.INTERACTION:

            assert all(
                isinstance(f, tuple) for f in features
            ), 'Not all passed features for interaction tool are of type tuple.'

            for feature in features:
                assert (
                    len(feature) == 2
                ), f'Length of feature tuple is {len(feature)}. Expected 2.'

                feature_types = [type(f) for f in feature]
                exp_feature_types = [str, str]
                assert (
                    feature_types == exp_feature_types
                ), f'Feature tuple contains types {tuple(feature_types)}. Expected {tuple(exp_feature_types)}.'
        n_keys = len(result.keys())
        exp_n_keys = len(features)
        if 'misc' in result.keys():
            exp_n_keys += 1
        assert (
            n_keys == exp_n_keys
        ), f'Result has {n_keys} keys. Expected exactly {exp_n_keys} keys.'
        keys = set(result.keys())
        if "misc" in keys:
            keys.remove('misc')
        exp_keys = set(features)
        assert keys == exp_keys, f'Result has keys {keys}. Expected keys {exp_keys}.'
        if self.result_type not in accepted_result_types:
            raise ValueError(f'Encountered unexpected result type {self.result_type}.')
        if self.result_type in [ResultType.DIM1, ResultType.DIM2, ResultType.DIM3]:
            self._check_result_format_DIM1_2_3(result)


    def _check_result_format_DIM1_2_3(self, result) -> None:
        # each key has as its value a real value or a dictionary
        # depending on the return type, different formats are possible
        for feature, subresult in result.items():

            try:

                if feature == 'misc':
                    assert isinstance(
                        subresult, dict
                    ), f'Result is of type {type(subresult)}. Expected a dict.'

                elif self.result_type is ResultType.DIM1:
                    self._check_result_format_DIM1(subresult)

                elif self.result_type is ResultType.DIM2:
                    self._check_result_format_DIM2(feature, subresult)

                elif self.result_type is ResultType.DIM3:
                    self._check_result_format_DIM3(feature, subresult)

                else:
                    raise ValueError(f'Encountered unexpected result type {self.result_type}.')

            except Exception as e:
                # append feature in error message
                e.args = (f'{e.args[0]} Feature: {feature}.',)
                raise e

    @staticmethod
    def _check_result_format_DIM3(feature, subresult) -> None:
        # expected format is a dictionary with three or four keys
        # first key is the feature pair's first feature and its value a 1D np.ndarray[Real]
        # second key is the feature pair's second feature and its value a 1D np.ndarray[Real]
        # third key is 'scores' and its value a 2D np.ndarray[Real]:
        # optional fourth key is 'misc' and its value a Dict
        # product of feature array lengths is number of elements in scores
        # expected feature format is a Tuple[str, str]
        assert isinstance(
            subresult, dict
        ), f'Result is of type {type(subresult)}. Expected a dict.'
        assert isinstance(
            feature, tuple
        ), f'Feature is of type {type(feature)}. Expected a tuple.'
        n_keys = len(subresult.keys())
        assert (
            n_keys == 3 or n_keys == 4
        ), f'Result has {n_keys} {"key" if n_keys == 1 else "keys"}. Expected 3 or 4 keys.'
        keys = set(subresult.keys())
        exp_keys = {feature[0], feature[1], 'scores'}
        assert all(
            k in keys for k in exp_keys
        ), f'Result has keys {keys}. Expected keys {exp_keys}.'
        lengths = []
        size = 0
        for key, value in subresult.items():

            if key == 'misc':

                assert isinstance(
                    value, dict
                ), f'Result value for key {key} is of type {type(value)}. Expected a dict.'

            else:

                assert isinstance(
                    value, np.ndarray
                ), f'Result value for key {key} is of type {type(value)}. Expected a np.ndarray.'

                assert np.issubdtype(
                    value.dtype, np.number
                ), f'Result array for {key} has data type {value.dtype}. Expected real values.'

                if key == 'scores':

                    assert (
                        len(value.shape) == 2
                    ), f'Result array for key {key} has dimension {len(value.shape)}. Expected 2.'

                    size = len(value[0]) * len(value)

                else:

                    assert (
                        len(value.shape) == 1
                    ), f'Result array for key {key} has dimension {len(value.shape)}. Expected 1.'

                    lengths.append(len(value))
        scores_key = 'scores'
        exp_size = np.product(lengths)
        assert size == exp_size, (
            f'Number of elements for key {scores_key} is {size}. Expected it to be equal to {exp_size}, '
            f'the product of feature list lengths {lengths}.'
        )

    @staticmethod
    def _check_result_format_DIM2(feature, subresult) -> None:
        # expected format is a dictionary with two or three keys
        # first key is the feature and its value a 1D np.ndarray[Real]
        # second key is 'scores' and its value a 1D np.ndarray[Real]
        # optional third key is 'misc' and its value a Dict
        # all arrays of real values have the same length
        # expected feature format is a str
        assert isinstance(subresult, dict), f'Result is of type {type(subresult)}. Expected a dict.'
        assert isinstance(feature, str), f'Feature is of type {type(feature)}. Expected a str.'
        n_keys = len(subresult.keys())
        assert n_keys in {2, 3}, f'Result has {n_keys} {"key" if n_keys == 1 else "keys"}. Expected 2 or 3 keys.'
        keys = set(subresult.keys())
        exp_keys = {feature, 'scores'}
        assert all(k in keys for k in exp_keys), f'Result has keys {keys}. Expected keys {exp_keys}.'
        lengths = []
        for key, value in subresult.items():

            if key == 'misc':

                assert isinstance(value, dict), f'Result value for key {key} is of type {type(value)}. Expected a dict.'

            else:

                assert isinstance(
                    value, np.ndarray
                ), f'Result value for key {key} is of type {type(value)}. Expected a np.ndarray.'

                assert np.issubdtype(
                    value.dtype, np.number
                ), f'Result array for {key} has data type {value.dtype}. Expected real values.'

                assert (
                    len(value.shape) == 1
                ), f'Result array for key {key} has dimension {len(value.shape)}. Expected 1.'

                lengths.append(len(value))
        assert (
            len(set(lengths)) <= 1
        ), f'Lists of real values have varying lengths {lengths}. Expected equal lengths.'

    @staticmethod
    def _check_result_format_DIM1(subresult) -> None:
        # expected format is a single scalar real value
        assert isinstance(subresult, Real), f'Result is of type {type(subresult)}. Expected a real value.'


class ImportanceTool(Tool, ABC):
    """Tool for feature importance analysis."""

    def __init__(self, name: str, result_type: ResultType) -> None:
        super().__init__(name=name, tool_type=ToolType.IMPORTANCE, result_type=result_type)

    def _check_features(self, features: list[Union[str, tuple[str, str]]], dataset: Dataset) -> None:

        super()._check_features(features=features, dataset=dataset)
        for feature in features:
            if not isinstance(feature, str):
                raise ValueError("Importance tools expect features as string")
        if invalid_features := list(set(features).difference(set(dataset.features))):
            raise ValueError(f'The following features are not available: {invalid_features}')

class InteractionTool(Tool, ABC):
    """Tool for feature interaction analysis."""

    def __init__(self, name: str, result_type: ResultType) -> None:
        super().__init__(name=name, tool_type=ToolType.INTERACTION, result_type=result_type)

    def _check_features(self, features: list[Union[str, tuple[str, str]]], dataset: Dataset) -> None:

        super()._check_features(features=features, dataset=dataset)
        for feature in features:
            if not isinstance(feature, tuple) or len(feature) != 2:
                raise ValueError("Interaction tool expects feature pairs as tuples of exact two features.")
            if not isinstance(feature[0], str) or not isinstance(feature[1], str):
                raise ValueError("Features in feature tuples have to be given as string.")
        if invalid_features := list(set(features).difference(set(dataset.feature_pairs))):
            raise ValueError(f'The following feature pairs are not available: {invalid_features}')


class ToolError(Exception):
    """Exception raised by tools in the feature importance toolkit

    Attributes:
        message (str, optional): The error message
    """

    def __init__(self, message: str = "An error occurred within the tool") -> None:
        self.message = message
        super().__init__(self.message)
