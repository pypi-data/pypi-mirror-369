from .vip_utils import compute_vip
from ..pdp import PDPImportance
from ..utils import compute_tool
from ...analyzer import Analyzer
from ...datasets import Dataset
from ...model import Model
from ...plots import importance_bar_plot
from ...tools import ImportanceTool
from ...types import ResultType, DataType


class VIPImportance(ImportanceTool):
    """Tool for determining Variable Importance Plot (VIP) results for single features.
    Implementation follows the original proposal of [Greenwell et al.](https://arxiv.org/pdf/1805.04755.pdf).
    """

    def __init__(self, name: str = 'VIP Importance', grid_size: int = 50,
                 percentiles: tuple[float, float] = (0.0, 1.0)) -> None:
        """Initializes VIP Importance tool.

        Args:
            name (str, optional): Name of the tool. Defaults to 'VIP Importance'.
            grid_size (int, optional): Maximum number of grid points for the PDP analysis. Defaults to 50.
            percentiles (Tuple[float, float], optional): Lower and upper percentiles for the PDP-grid's extreme values. Defaults to (0.0, 1.0).
        """

        super().__init__(name, result_type=ResultType.DIM1)

        # set attributes
        self.grid_size = grid_size
        self.percentiles = percentiles

    def run(self, model: Model, dataset: Dataset, features: list[str], analyzer: Analyzer = None) -> dict[str, float]:

        self.data_type = dataset.data_type
        super()._check_features(features=features, dataset=dataset)

        result = {}
        if self.data_type == DataType.CLASSIFICATION:
            classes = model.classes
            for class_index, class_label in enumerate(classes):
                result[class_index] = {"class_label": class_label, 'result': {}}
                for feature in features:
                    result[class_index]['result'][feature] = {}
        pdp_result = compute_tool(PDPImportance, model, dataset, features, analyzer,
                                  grid_size=self.grid_size, percentiles=self.percentiles)

        # compute scores
        for feature in features:
            if self.data_type == DataType.REGRESSION:
                score = compute_vip(pdp_result[feature]['scores'])
                result[feature] = score
            else:
                for class_index, class_label in enumerate(classes):
                    score = compute_vip(pdp_result[class_index]['result'][feature]['scores'])
                    result[class_index]['result'][feature] = score

        return result

    def plot(self, result: dict, title: str = 'Variable Importance Plot (VIP)', plot_config: dict = None, **kwargs)\
            -> None:

        fig = importance_bar_plot(result, title=title, **kwargs)
        fig.show(config=plot_config)

    @staticmethod
    def export_plot(result: dict, title: str = 'Variable Importance Plot (VIP)', **kwargs):

        return importance_bar_plot(result, title=title, **kwargs)
