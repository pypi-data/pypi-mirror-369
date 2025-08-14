from PyALE import ale

from . import ALEImportance
from .. import InteractionTool
from ..utils import compute_tool, features_from_pairs
from ...analyzer import Analyzer
from ...datasets import Dataset
from ...model import Model
from ...plots import interaction_heatmap_matrix_plot
from ...types import ResultType, DataType


class ALEInteraction(InteractionTool):
    """Tool for determining Accumulated Local Effects (ALE) for feature pairs.
    Using implementation from [PyALE](https://github.com/DanaJomar/PyALE).
    More details about the ALE at https://christophm.github.io/interpretable-ml-book/ale.html.

    Note: By default, this tool only computes the 2nd order interaction effects and 1st order effects are neglected. ALEs are doing this for interaction analysis, as including 1st order effects may make interactions less obvious and more difficult to interpret. The deviating behavior, where 1st order effects are included can be achieved by setting `include_first_order` to True.
    """

    def __init__(self, name: str = 'ALE Interaction', grid_size: int = 50, include_first_order: bool = False) -> None:
        """Initializes ALE Interaction tool.

        Args:
            name (str, optional): Name of the tool. Defaults to 'ALE Interaction'.
            grid_size (int, optional): Maximum number of grid points for the ALE analysis. Defaults to 50.
            include_first_order (bool, optional): Whether to include 1st order effects as well as opposed to only respecting 2nd order effects. Defaults to False.
        """

        super().__init__(name, result_type=ResultType.DIM3)

        # set attributes
        self.grid_size = grid_size
        self.include_first_order = include_first_order

    def run(self, model: Model, dataset: Dataset, features: list[tuple[str, str]], analyzer: Analyzer = None) -> dict[
        tuple[str, str], dict[str, list]]:

        self.data_type = dataset.data_type
        super()._check_features(features=features, dataset=dataset)

        result = {}

        # get data
        x_train, y_train = dataset.get_train()
        if self.include_first_order:
            single_features = features_from_pairs(features)
            first_order_ale = compute_tool(ALEImportance, model, dataset, single_features, analyzer,
                                           grid_size=self.grid_size)
        if self.data_type == DataType.CLASSIFICATION:
            classes = model.classes
            for class_index, class_label in enumerate(classes):
                result[class_index] = {"class_label": class_label, 'result': {}}
        for feature_pair in features:
            # compute scores
            if self.data_type == DataType.CLASSIFICATION:
                for class_index, class_label in enumerate(classes):
                    model.set_class_index = class_index
                    if 'first_order_ale' not in locals():
                        first_order_ale = None
                    feat_pair_grid, res = self._calculate_pair_ale(model, x_train, feature_pair, first_order_ale)
                    result[class_index]['result'][feature_pair] = {
                        feature_pair[0]: feat_pair_grid[0],  # grid points feature 0
                        feature_pair[1]: feat_pair_grid[1],  # grid points feature 1
                        'scores': res,
                        'misc': {
                            'samples': x_train[list(feature_pair)].to_numpy()
                        }}

            else:
                if 'first_order_ale' not in locals():
                    first_order_ale = None
                feat_pair_grid, res = self._calculate_pair_ale(model, x_train, feature_pair, first_order_ale)

                result[feature_pair] = {
                    feature_pair[0]: feat_pair_grid[0],  # grid points feature 0
                    feature_pair[1]: feat_pair_grid[1],  # grid points feature 1
                    'scores': res,
                    'misc': {
                        'samples': x_train[list(feature_pair)].to_numpy()
                    }
                }

        return result

    def _calculate_pair_ale(self, model, x_train, feature_pair, first_order_ale):
        feat_pair_ale = ale(x_train, model, list(feature_pair), grid_size=self.grid_size,
                            feature_type='continuous', plot=False)
        feat_pair_effects = feat_pair_ale.to_numpy()
        feat_pair_grid = [feat_pair_ale.index.to_numpy(), feat_pair_ale.columns.to_numpy()]
        if self.include_first_order:  # add 1st order effects
            feat_a, feat_b = feature_pair
            feat_a_effects = first_order_ale[feat_a]['scores']
            feat_b_effects = first_order_ale[feat_b]['scores']
            res = feat_pair_effects + feat_a_effects.reshape(-1, 1) + feat_b_effects.reshape(1, -1)
        else:  # keep 2nd order effects only
            res = feat_pair_effects
        return feat_pair_grid, res

    def plot(self, result: dict, title: str = 'Accumulated Local Effects (ALE)', plot_config: dict = None, **kwargs)\
            -> None:

        fig = interaction_heatmap_matrix_plot(result, title=title, **kwargs)
        fig.show(config=plot_config)

    @staticmethod
    def export_plot(result: dict, title: str = 'Accumulated Local Effects (ALE)', **kwargs):

        return interaction_heatmap_matrix_plot(result, title=title, **kwargs)
