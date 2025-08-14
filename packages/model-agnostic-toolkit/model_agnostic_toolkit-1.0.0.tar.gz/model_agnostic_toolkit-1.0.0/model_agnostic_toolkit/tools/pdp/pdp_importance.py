import pandas as pd
from pdpbox import pdp
from sklearn.inspection import partial_dependence

from .. import ImportanceTool
from ...analyzer import Analyzer
from ...datasets import Dataset
from ...model import Model
from ...plots import pdp_grid_plot
from ...types import ResultType, DataType


class PDPImportance(ImportanceTool):
    """Tool for determining Partial Dependence Plot (PDP) results for single features.
    Using implementation from [scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.inspection.partial_dependence.html).
    More information regarding PDP can be found at https://christophm.github.io/interpretable-ml-book/pdp.html.
    """

    def __init__(self, name: str = 'PDP Importance', grid_size: int = 50, percentiles: tuple[float, float] = (0.0, 1.0),
                 **kwargs) -> None:
        """Initializes PDP Importance tool.

        Keyworded arguments are passed to the `partial_depencence` function from sklearn.

        Args:
            name (str, optional): Name of the tool. Defaults to 'PDP Importance'.
            grid_size (int, optional): Maximum number of grid points for the PDP analysis. Defaults to 50.
            percentiles (Tuple[float, float], optional): Lower and upper percentiles for the grid's extreme values. Defaults to (0.0, 1.0).
        """

        super().__init__(name, result_type=ResultType.DIM2)

        # set attributes
        self.grid_size = grid_size
        self.percentiles = percentiles
        self.kwargs = kwargs

    def run(self, model: Model, dataset: Dataset, features: list[str], analyzer: Analyzer = None) -> dict[
        str, dict[str, list]]:

        self.data_type = dataset.data_type
        super()._check_features(features=features, dataset=dataset)

        result = {}
        # get data
        x_train, y_train = dataset.get_train()

        if self.data_type == DataType.CLASSIFICATION:
            # Perform one-hot encoding
            one_hot_encoded = pd.get_dummies(y_train)
            # Concatenate the one-hot encoded columns with the original DataFrame
            df_encoded = pd.concat([y_train, one_hot_encoded], axis=1)
            df_final = pd.concat([x_train, df_encoded], axis=1)
            classes = model.classes
            for class_index, class_label in enumerate(classes):
                result[class_index] = {"class_label": class_label, 'result': {}}
            for feature in features:
                # additional percentile
                maxv = x_train[feature].quantile(self.percentiles[1])
                minv = x_train[feature].quantile(self.percentiles[0])
                grid_ends = (minv, maxv)
                # compute scores
                if not hasattr(model.model, 'n_classes_'):
                    model.model.n_classes_ = len(classes)
                pdp_feat = pdp.PDPIsolate(model=model.model, df=df_final, model_features=dataset.features,
                                          feature=feature,
                                          feature_name=feature, grid_type='equal', grid_range=grid_ends,
                                          num_grid_points=self.grid_size)
                for class_index, class_label in enumerate(classes):
                    if len(classes) == 2:
                        if class_index == 0:
                            pdp_vals = 1 - pdp_feat.results[0].pdp
                            ice_vals = 1 - pdp_feat.results[0].ice_lines.to_numpy()
                        else:
                            pdp_vals = pdp_feat.results[0].pdp
                            ice_vals = pdp_feat.results[0].ice_lines.to_numpy()
                    else:
                        pdp_vals = pdp_feat.results[class_index].pdp
                        ice_vals = pdp_feat.results[class_index].ice_lines.to_numpy()

                    result[class_index]['result'][feature] = {
                        feature: pdp_feat.feature_info.grids,
                        'scores': pdp_vals,
                        'misc': {
                            'ice': ice_vals
                        },
                    }
                    result[class_index]['result'][feature]['misc']['samples'] = x_train[feature]

        else:
            for feature in features:
                # compute scores
                res = partial_dependence(model.model, x_train, [feature], grid_resolution=self.grid_size,
                                         percentiles=self.percentiles, kind='both', **self.kwargs)
                result[feature] = {
                    feature: res['values'][0],  # grid points
                    'scores': res['average'][0],
                    'misc': {
                        'ice': res['individual'][0],
                        'samples': x_train[feature]
                    }
                }

        return result

    def plot(self, result: dict, title: str = 'Partial Dependence Plots (PDP)', plot_config: dict = None, **kwargs) \
            -> None:

        fig = pdp_grid_plot(result, title=title, **kwargs)
        fig.show(config=plot_config)

    @staticmethod
    def export_plot(result: dict, title: str = 'Partial Dependence Plots (PDP)', **kwargs):

        return pdp_grid_plot(result, title=title, **kwargs)
