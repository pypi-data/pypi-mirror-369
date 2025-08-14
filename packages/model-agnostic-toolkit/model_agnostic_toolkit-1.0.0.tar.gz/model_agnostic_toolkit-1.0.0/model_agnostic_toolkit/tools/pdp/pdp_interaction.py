from functools import partial
from ray.util.multiprocessing import Pool

import numpy as np
import pandas as pd
from pdpbox import pdp
from sklearn.inspection import partial_dependence

from . import PDPImportance
from .. import InteractionTool
from ..utils import center_1D, center_2D, compute_tool, features_from_pairs
from ...analyzer import Analyzer
from ...datasets import Dataset
from ...model import Model
from ...plots import interaction_heatmap_matrix_plot
from ...types import ResultType, DataType


class PDPInteraction(InteractionTool):
    """Tool for determining Partial Dependence Plot (PDP) results for feature pairs.
    Using implementation from [scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.inspection.partial_dependence.html).
    More information regarding PDP can be found at https://christophm.github.io/interpretable-ml-book/pdp.html.

    Note: If `second_order_only` is True, this tool only computes the 2nd order interaction effects and 1st order effects are removed. PDPs are usually not doing this but for interaction analysis, including 1st order effects may make interactions less obvious and more difficult to interpret. The 2nd order effects are also centered around zero, as opposed to the predictions usually obtained with PDPs. The original PDP behaviour is kept by default by setting `second_order_only` to False.
    """

    def __init__(self, name: str = 'PDP Interaction', grid_size: int = 50,
                 percentiles: tuple[float, float] = (0.0, 1.0), second_order_only: bool = False, **kwargs) -> None:
        """Initialize PDP Interaction tool.

        Keyworded arguments are passed to the `partial_dependence` function from sklearn.

        Args:
            name (str, optional): Name of the tool. Defaults to 'PDP Interaction'.
            grid_size (int, optional): Maximum number of grid points for the PDP analysis. Defaults to 50.
            percentiles (Tuple[float, float], optional): Lower and upper percentiles for the grid's extreme values. Defaults to (0.0, 1.0).
            second_order_only (bool, optional): Whether to compute 2nd order effects only and remove 1st oder effects. Defaults to False.
        """

        super().__init__(name, result_type=ResultType.DIM3)

        # set attributes
        self.grid_size = grid_size
        self.percentiles = percentiles
        self.second_order_only = second_order_only
        self.kwargs = kwargs

    def run(self, model: Model, dataset: Dataset, features: list[tuple[str, str]], analyzer: Analyzer = None) \
            -> dict[tuple[str, str], dict[str, list]]:

        self.data_type = dataset.data_type
        super()._check_features(features=features, dataset=dataset)

        result = {}

        # get data
        x_train, y_train = dataset.get_train()

        # get data
        if self.data_type == DataType.CLASSIFICATION:
            classes, _ = np.unique(y_train, return_inverse=True)
            # if second order only: calculates results with first order effects and subtracts them afterward
            if self.second_order_only:
                single_features = features_from_pairs(features)
                first_order_pdp_effects = self._calculate_first_order_effects_classification(analyzer, dataset, model,
                                                                                             single_features)
                feat_pair_pdp = compute_tool(PDPInteraction, model, dataset, features, analyzer,
                                             grid_size=self.grid_size, percentiles=self.percentiles,
                                             second_order_only=False)
                result = feat_pair_pdp.copy()
                self._subtract_first_order_effects_classification(classes, feat_pair_pdp, features,
                                                                  first_order_pdp_effects, result)

            else:
                # Perform one-hot encoding
                one_hot_encoded = pd.get_dummies(y_train)
                # Concatenate the one-hot encoded columns with the original DataFrame
                df_encoded = pd.concat([y_train, one_hot_encoded], axis=1)
                df_final = pd.concat([x_train, df_encoded], axis=1)
                # result template creation
                classes = model.classes
                if not hasattr(model.model, 'n_classes_'):
                    model.model.n_classes_ = len(classes)
                for class_index, class_label in enumerate(classes):
                    result[class_index] = {"class_label": class_label, 'result': {}}
                for feature_pair in features:
                    # percentile info
                    maxf1 = x_train[feature_pair[0]].quantile(self.percentiles[1])
                    minf1 = x_train[feature_pair[0]].quantile(self.percentiles[0])
                    maxf2 = x_train[feature_pair[1]].quantile(self.percentiles[1])
                    minf2 = x_train[feature_pair[1]].quantile(self.percentiles[0])
                    feat_pair_pdp = pdp.PDPInteract(model=model.model, df=df_final, model_features=dataset.features,
                                                    features=list(feature_pair), feature_names=list(features),
                                                    num_grid_points=[self.grid_size, self.grid_size],
                                                    grid_types=['equal', 'equal'],
                                                    grid_ranges=[(minf1, maxf1), (minf2, maxf2)])

                    classes = model.classes
                    self._store_result_classification(classes, feat_pair_pdp, feature_pair, result, x_train)

        elif self.second_order_only:  # remove 1st order effects
            single_features = features_from_pairs(features)
            first_order_pdp = compute_tool(PDPImportance, model, dataset, single_features, analyzer,
                                           grid_size=self.grid_size, percentiles=self.percentiles)
            first_order_pdp_effects = {
                feature_pair: center_1D(value['scores'], value[feature_pair])
                for feature_pair, value in first_order_pdp.items()
            }
            feat_pair_pdp = compute_tool(PDPInteraction, model, dataset, features, analyzer,
                                         grid_size=self.grid_size, percentiles=self.percentiles,
                                         second_order_only=False)

            self._subtract_first_order_effects_regression(feat_pair_pdp, features, first_order_pdp_effects, result,
                                                          x_train)

        else:  # keep 1st order effects
            # parallelized partial dependence computation
            with Pool() as pool:
                mapfunc = partial(partial_dependence, model.model, x_train,
                                  grid_resolution=self.grid_size, percentiles=self.percentiles,
                                  kind='average', **self.kwargs)
                feat_pair_pdps = pool.map(mapfunc, [list(f) for f in features])

            for i, feature_pair in enumerate(features):
                feat_pair_pdp = feat_pair_pdps[i]
                feat_pair_grid = feat_pair_pdp['values']

                feat_pair_scores = feat_pair_pdp['average'][0]
                res = feat_pair_scores
                self._store_result_regression(result, res, feature_pair, feat_pair_grid, x_train)

        return result

    def _calculate_first_order_effects_classification(self, analyzer: Analyzer, dataset: Dataset, model: Model,
                                                      single_features: list[str]) -> dict:
        first_order_pdp = compute_tool(PDPImportance, model, dataset, single_features, analyzer,
                                       grid_size=self.grid_size, percentiles=self.percentiles)
        return {
            class_index: {
                feature: center_1D(value['scores'], value[feature])
                for feature, value in first_order_result['result'].items()
            }
            for class_index, first_order_result in first_order_pdp.items()
        }

    def _subtract_first_order_effects_regression(self, feat_pair_pdp, features, first_order_pdp_effects, result,
                                                 x_train) -> None:
        for feature_pair in features:
            feat_a, feat_b = feature_pair
            feat_a_effects = first_order_pdp_effects[feat_a]
            feat_b_effects = first_order_pdp_effects[feat_b]

            feat_pair_scores = feat_pair_pdp[feature_pair]['scores']
            feat_pair_grid = [feat_pair_pdp[feature_pair][feature_pair[0]],
                              feat_pair_pdp[feature_pair][feature_pair[1]]]
            feat_pair_effects = center_2D(feat_pair_scores, feat_pair_grid)

            res = feat_pair_effects - feat_a_effects.reshape(-1, 1) - feat_b_effects.reshape(1, -1)

            self._store_result_regression(result, res, feature_pair, feat_pair_grid, x_train)

    @staticmethod
    def _subtract_first_order_effects_classification(classes, feat_pair_pdp, features, first_order_pdp_effects, result)\
            -> None:
        for feature_pair in features:
            for class_index, _ in enumerate(classes):
                feat_a_effects = first_order_pdp_effects[class_index][feature_pair[0]]
                feat_b_effects = first_order_pdp_effects[class_index][feature_pair[1]]

                feat_pair_scores = feat_pair_pdp[class_index]['result'][feature_pair]['scores']
                feat_pair_grid = [feat_pair_pdp[class_index]['result'][feature_pair][feature_pair[0]],
                                  feat_pair_pdp[class_index]['result'][feature_pair][feature_pair[1]]]

                feat_pair_effects = center_2D(feat_pair_scores, feat_pair_grid)

                result[class_index]['result'][feature_pair]['scores'] = (feat_pair_effects -
                                                                         feat_a_effects.reshape(-1, 1) -
                                                                         feat_b_effects.reshape(1, -1))

    def _store_result_classification(self, classes, feat_pair_pdp, feature_pair, result, x_train) -> None:
        for class_index, class_label in enumerate(classes):
            result[class_index]['class_label'] = class_label
            result[class_index]['result'][feature_pair] = {
                feature_pair[0]: feat_pair_pdp.pdp_isolate_objs[
                    0
                ].feature_info.grids,
                feature_pair[1]: feat_pair_pdp.pdp_isolate_objs[
                    1
                ].feature_info.grids,
            }
            pdpvalues = (
                1 - feat_pair_pdp.results[0].pdp
                if len(classes) == 2 and class_index != 0
                else feat_pair_pdp.results[class_index].pdp
            )
            val = np.reshape(pdpvalues, (self.grid_size, self.grid_size))
            result[class_index]['result'][feature_pair]['scores'] = val
            result[class_index]['result'][feature_pair]['misc'] = {}
            result[class_index]['result'][feature_pair]['misc']['samples'] = x_train[list(feature_pair)].to_numpy()

    @staticmethod
    def _store_result_regression(result: dict, pdp_scores: np.array, feature_pair: tuple[str, str], grid: np.array,
                                 samples: pd.DataFrame) -> None:
        """Stores individual PDP results in the common result dictionary of this tool.

        Args:
            result (Dict): The common result dictionary.
            pdp_scores (np.array): PDP result scores of a feature pair to be stored.
            feature_pair (Tuple[str, str]): Feature pair to store results for.
            grid (np.array): PDP grid values for both features.
            samples (pd.DataFrame): Data frame with all training samples.
        """
        result[feature_pair] = {
            feature_pair[0]: grid[0],  # grid points of feature 0
            feature_pair[1]: grid[1],  # grid points of feature 1
            'scores': pdp_scores,
            'misc': {
                'samples': samples[list(feature_pair)].to_numpy()
            }
        }

    def plot(self, result: dict, title: str = 'Partial Dependence Plots (PDP)', plot_config: dict = None, **kwargs)\
            -> None:

        cbar_title = 'interaction effect' if self.second_order_only else 'prediction'
        fig = interaction_heatmap_matrix_plot(result, title=title, colorbar_title=cbar_title, **kwargs)
        fig.show(config=plot_config)

    def export_plot(self, result: dict, title: str = 'Partial Dependence Plots (PDP)', **kwargs):

        cbar_title = 'interaction effect' if self.second_order_only else 'prediction'
        return interaction_heatmap_matrix_plot(result, title=title, colorbar_title=cbar_title, **kwargs)
