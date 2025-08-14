import warnings

import numpy as np
import pandas as pd

from .. import InteractionTool
from ..ale import ALEImportance, ALEInteraction
from ..pdp import PDPImportance, PDPInteraction
from ..utils import center_1D, center_2D, compute_tool, features_from_pairs, interpolate_1D, interpolate_2D
from ...analyzer import Analyzer
from ...datasets import Dataset
from ...model import Model
from ...plots import interaction_summary_plot
from ...types import ResultType, DataType


class HStatisticInteraction(InteractionTool):
    """Tool for determining Friedman’s H-statistic scores for feature pairs.
    Following the description from [Interpretable Machine Learning](https://christophm.github.io/interpretable-ml-book/interaction.html#theory-friedmans-h-statistic), based on [Predictive Learning via Rule Ensembles](https://arxiv.org/pdf/0811.1679.pdf).

    Note: Depending on the chosen `mode` (PDP or ALE), this tool will account for the differences in 1st order and 2nd order effects for interaction. PDPs include 1st order effects by default while ALEs do not. For the PDP mode this leads to H² = Σ (F_ab - F_a - F_b)² / Σ F_ab² and for the ALE mode to H² = Σ F_ab² / Σ (F_ab + F_a + F_b)² (with sums going over all samples and F being evaluated at all sample points).
    """

    def __init__(self, name: str = 'H-Statistic Interaction', mode: str = 'pdp', pdp_grid_size: int = 50,
                 pdp_percentiles: tuple[float, float] = (0.0, 1.0), ale_grid_size: int = 50,
                 return_square: bool = False) -> None:
        """Initializes H-Statistic Interaction tool.

        Args:
            name (str, optional): Name of the tool. Defaults to 'H-Statistic Interaction'.
            mode (str, optional): Which underlying tool to use for effects on prediction. Either 'pdp' or 'ale'. Defaults to 'pdp'.
            pdp_grid_size (int, optional): Maximum number of grid points for the PDP analysis. Defaults to 50.
            pdp_percentiles (Tuple[float, float], optional): Lower and upper percentiles for the PDP-grid's extreme values. Defaults to (0.0, 1.0).
            ale_grid_size (int, optional): Maximum number of grid points for the ALE analysis. Defaults to 50.
            return_square (bool, optional): Whether to return the H²-score instead of just H. Defaults to False.

        Raises:
            ValueError: Raised if an unexpected mode was passed.
        """

        # set mode
        exp_modes = ['pdp', 'ale']
        if mode in exp_modes:
            self.mode = mode
        else:
            raise ValueError('Mode must be one of {exp_modes}. Got {mode} instead'
                             .format(exp_modes=exp_modes, mode=mode))

        super().__init__(name, result_type=ResultType.DIM1)

        # set attributes
        self.pdp_grid_size = pdp_grid_size
        self.pdp_percentiles = pdp_percentiles
        self.ale_grid_size = ale_grid_size
        self.return_square = return_square

    def run(self, model: Model, dataset: Dataset, features: list[tuple[str, str]], analyzer: Analyzer = None) -> dict[
            tuple[str, str], float]:

        self.data_type = dataset.data_type
        super()._check_features(features=features, dataset=dataset)

        result = {}

        # get data
        x_train, _ = dataset.get_train()

        f_pairs = self._compute_f_pairs(model, dataset, features, analyzer)
        f_feats, grids_feats = self._compute_f_feats(model, dataset, features_from_pairs(features), analyzer)

        if self.data_type == DataType.CLASSIFICATION:
            classes = model.classes
            for class_index, class_label in enumerate(classes):
                result[class_index] = {'class_label': class_label, 'result': {}}
                for feat_pair in features:
                    feat_a, feat_b = feat_pair
                    h_square = self._compute_h_square(x_train[list(feat_pair)],
                                                      f_pairs[feat_pair][class_index]['f_vals'],
                                                      f_feats[feat_a][class_index]['f_vals'],
                                                      f_feats[feat_b][class_index]['f_vals'],
                                                      grids_feats[feat_a], grids_feats[feat_b])
                    result[class_index]['result'][feat_pair] = h_square if self.return_square else np.sqrt(h_square)
        else:
            for feat_pair in features:
                feat_a, feat_b = feat_pair
                h_square = self._compute_h_square(x_train[list(feat_pair)], f_pairs[feat_pair],
                                                  f_feats[feat_a], f_feats[feat_b],
                                                  grids_feats[feat_a], grids_feats[feat_b])
                result[feat_pair] = h_square if self.return_square else np.sqrt(h_square)
        return result

    def _compute_f_pairs(self, model: Model, dataset: Dataset, feature_pairs: list[tuple[str, str]],
                         analyzer: Analyzer) -> dict[tuple[str, str], np.ndarray]:
        """Computes F-values for the H²-score, i.e. the centered partial dependence or ALE results for a feature pairs.

        Args:
            model (Model): Model to evaluate the PD or ALE scores with.
            dataset (Dataset): Dataset to base the computation on.
            feature_pairs (List[Tuple[str, str]]): List of feature pairs to determine F-values for.
            analyzer (Analyzer): Analyzer this tool is run from.

        Returns:
            Dict[Tuple[str, str], np.ndarray]: The computed F-values for feature pairs.
        """

        f_pairs = {}

        if self.mode == 'pdp':  # determine pair PD values
            pair_results = compute_tool(PDPInteraction, model, dataset, feature_pairs, analyzer,
                                        grid_size=self.pdp_grid_size, percentiles=self.pdp_percentiles,
                                        second_order_only=False)

        elif self.mode == 'ale':  # determine pair ALE values
            pair_results = compute_tool(ALEInteraction, model, dataset, feature_pairs, analyzer,
                                        grid_size=self.ale_grid_size, include_first_order=False)

        else:
            raise ValueError(f'{self.mode} is not available. Use ale or pdp mode.')

        # compute F-values by centering
        if self.data_type == DataType.CLASSIFICATION:

            classes = model.classes
            for feat_pair in feature_pairs:
                f_pairs[feat_pair] = {}
                for class_index, class_label in enumerate(classes):
                    scores_pair = pair_results[class_index]['result'][feat_pair]['scores']
                    grid_pair = [pair_results[class_index]['result'][feat_pair][feat_pair[0]],
                                 pair_results[class_index]['result'][feat_pair][feat_pair[1]]]
                    f_pair = center_2D(scores_pair, grid_pair)  # center effects around 0
                    f_pairs[feat_pair][class_index] = {'f_vals': f_pair, 'class_label': class_label}

        else:
            for feat_pair in feature_pairs:
                scores_pair = pair_results[feat_pair]['scores']
                grid_pair = [pair_results[feat_pair][feat_pair[0]], pair_results[feat_pair][feat_pair[1]]]
                f_pair = center_2D(scores_pair, grid_pair)  # center effects around 0
                f_pairs[feat_pair] = f_pair

        return f_pairs

    def _compute_f_feats(self, model: Model, dataset: Dataset, features: list[str], analyzer: Analyzer) -> tuple[
        dict[str, np.ndarray], dict[str, np.ndarray]]:
        """Computes F-values for the H²-score, i.e. the centered partial dependence or ALE results for individual features.
        Also returns the underlying grid points used for PDP or ALE computation.

        Args:
            model (Model): Model to evaluate the PD or ALE scores with.
            dataset (Dataset): Dataset to base the computation on.
            features (List[str]): List of features to determine F-values for.
            analyzer (Analyzer): Analyzer this tool is run from.

        Returns:
            Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray]]: The computed F-values and the underlying grid points for individual features.
        """

        f_feats = {}
        grids_feats = {}

        if self.mode == 'pdp':  # determine individual PD values
            feat_results = compute_tool(PDPImportance, model, dataset, features, analyzer,
                                        grid_size=self.pdp_grid_size, percentiles=self.pdp_percentiles)

        elif self.mode == 'ale':  # determine individual ALE values
            feat_results = compute_tool(ALEImportance, model, dataset, features, analyzer,
                                        grid_size=self.ale_grid_size)

        else:
            raise ValueError(f'{self.mode} is not available. Use ale or pdp mode.')

        # compute F-values by centering
        if self.data_type == DataType.CLASSIFICATION:
            classes = model.classes
            for feat in features:
                f_feats[feat] = {}
                for class_index, class_label in enumerate(classes):
                    scores_feat = feat_results[class_index]['result'][feat]['scores']
                    grid_feat = feat_results[class_index]['result'][feat][feat]
                    f_feat = center_1D(scores_feat, grid_feat)  # center effects around 0
                    f_feats[feat][class_index] = {'f_vals': f_feat, 'class_label': class_label}
                grids_feats[feat] = grid_feat
        else:
            for feat in features:
                scores_feat = feat_results[feat]['scores']
                grid_feat = feat_results[feat][feat]
                f_feat = center_1D(scores_feat, grid_feat)  # center effects around 0
                f_feats[feat] = f_feat
                grids_feats[feat] = grid_feat

        return f_feats, grids_feats

    def _compute_h_square(self, x: pd.DataFrame, f_pair: np.ndarray, f_feat_a: np.ndarray, f_feat_b: np.ndarray,
                          grid_feat_a: np.ndarray, grid_feat_b: np.ndarray) -> float:
        """Computes the H²-score from centered partial dependence or ALE results for a given feature pair and the features individually.

        Args:
            x (pd.DataFrame): Data samples to base the analysis on.
            f_pair (np.ndarray): F-values for the feature pair.
            f_feat_a (np.ndarray): F-values for the first feature individually.
            f_feat_b (np.ndarray): F-values for the second feature individually.
            grid_feat_a (np.ndarray): Underlying grid points for the first feature.
            grid_feat_b (np.ndarray): Underlying grid points for the second feature.

        Returns:
            float: H²-score for the given feature pair.
        """

        feat_a, feat_b = x.columns

        # evaluate F-value samples for all data points
        f_samples_pair = interpolate_2D(x.to_numpy(), f_pair, [grid_feat_a, grid_feat_b])
        f_samples_a = interpolate_1D(x[feat_a].to_numpy(), f_feat_a, grid_feat_a)
        f_samples_b = interpolate_1D(x[feat_b].to_numpy(), f_feat_b, grid_feat_b)

        if self.mode == 'pdp':  # preparations for H² score with PDP
            # pair PDP shows 2nd order + 1st order effects, diff reduces to 2nd order effects only
            pdp_diff = f_samples_pair - f_samples_a - f_samples_b
            nominator = np.square(pdp_diff).sum()
            denominator = np.square(f_samples_pair).sum()

        elif self.mode == 'ale':  # preparations for H² score with ALE
            # pair ALE shows 2nd order effects only, sum extends to 2nd order + 1st order effects
            nominator = np.square(f_samples_pair).sum()
            ale_sum = f_samples_pair + f_samples_a + f_samples_b
            denominator = np.square(ale_sum).sum()

        else:
            raise ValueError(f'{self.mode} is not available. Use ale or pdp mode.')

        # calculate H² score
        if denominator != 0:
            h_square = nominator / denominator
        else:
            h_square = np.NaN
            warnings.warn('Encountered denominator of H²-score equal to 0. Setting H²-score to NaN.',
                          RuntimeWarning)

        if h_square > 1:
            warnings.warn('Encountered H²-score larger than 1. Be careful with interpretation.',
                          RuntimeWarning)

        return h_square

    def plot(self, result: dict, title: str = 'Friedman’s H-Statistics', plot_config: dict = None, **kwargs) -> None:

        fig = interaction_summary_plot(result, title=title)
        fig.show(config=plot_config)

    @staticmethod
    def export_plot(result: dict, title: str = 'Friedman’s H-Statistics', **kwargs):

        return interaction_summary_plot(result, title=title)
