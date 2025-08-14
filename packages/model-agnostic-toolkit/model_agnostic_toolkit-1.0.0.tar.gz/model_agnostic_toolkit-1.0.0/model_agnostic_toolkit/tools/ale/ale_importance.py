from PyALE import ale

from .. import ImportanceTool
from ...analyzer import Analyzer
from ...datasets import Dataset
from ...model import Model
from ...plots import ale_grid_plot
from ...types import ResultType, DataType


class ALEImportance(ImportanceTool):
    """Tool for determining Accumulated Local Effects (ALE) for single features.
    Using implementation from [PyALE](https://github.com/DanaJomar/PyALE).
    More details about the ALE at https://christophm.github.io/interpretable-ml-book/ale.html.
    """

    def __init__(self, name: str = 'ALE Importance', grid_size: int = 50, confidence: float = 0.95) -> None:
        """Initializes ALE Importance tool.

        Args:
            name (str, optional): Name of the tool. Defaults to 'ALE Importance'.
            grid_size (int, optional): Maximum number of grid points for the ALE analysis. Defaults to 50.
            confidence (float, optional): Confidence level for confidence intervals. Defaults to 0.95.
        """

        super().__init__(name, result_type=ResultType.DIM2)

        # set attributes
        self.grid_size = grid_size
        self.confidence = confidence

    def run(self, model: Model, dataset: Dataset, features: list[str], analyzer: Analyzer = None)\
            -> dict[str, dict[str, list]]:

        self.data_type = dataset.data_type
        super()._check_features(features=features, dataset=dataset)

        result = {}
        # get data
        x_train, _ = dataset.get_train()
        if self.data_type == DataType.CLASSIFICATION:
            classes = model.classes
            for class_index, class_label in enumerate(classes):
                result[class_index] = {"class_label": class_label, 'result': {}}
        for feature in features:
            # compute scores
            if self.data_type == DataType.REGRESSION:
                res = ale(x_train, model, [feature], grid_size=self.grid_size, feature_type='continuous', plot=False)
                result[feature] = self._store_result(res, x_train, feature)
            else:
                for class_index, class_label in enumerate(classes):
                    model.set_class_index = class_index
                    res = ale(x_train, model, [feature], grid_size=self.grid_size, feature_type='continuous',
                              plot=False)
                    result[class_index]['result'][feature] = self._store_result(res, x_train, feature)
        return result

    def _store_result(self, res, x_train, feature) -> dict:
        return {
            feature: res.index.to_numpy(),
            'scores': res['eff'].to_numpy(),
            'misc': {
                'lower_ci': res[
                    f'lowerCI_{int(100 * self.confidence)}%'
                ].to_numpy(),
                'upper_ci': res[
                    f'upperCI_{int(100 * self.confidence)}%'
                ].to_numpy(),
                'confidence': self.confidence,
                'samples': x_train[feature].to_numpy(),
            },
        }

    def plot(self, result: dict, title: str = 'Accumulated Local Effects (ALE)', plot_config: dict = None, **kwargs)\
            -> None:
        fig = ale_grid_plot(result, title=title, **kwargs)
        fig.show(config=plot_config)

    @staticmethod
    def export_plot(result: dict, title: str = 'Accumulated Local Effects (ALE)', **kwargs):
        return ale_grid_plot(result, title=title, **kwargs)
