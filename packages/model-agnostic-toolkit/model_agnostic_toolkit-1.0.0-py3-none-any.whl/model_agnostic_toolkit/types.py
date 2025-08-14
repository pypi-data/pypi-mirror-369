from enum import Enum


class DataType(Enum):
    """Type of Data, which has labels for either classification of regression.
    """

    CLASSIFICATION = 'Classification Data'
    REGRESSION = 'Regression Data'


class ToolType(Enum):
    """Type of Tool, which is used to compute either feature importance or interaction.
    """

    IMPORTANCE = 'Feature Importance Tool'
    INTERACTION = 'Feature Interaction Tool'


class ResultType(Enum):
    """Type of result, which represents either a single one-dimensional or multiple two-dimensional or
    three-dimensional values for each feature or feature combination.
    """

    DIM1 = '1D Result'
    DIM2 = '2D Result'
    DIM3 = '3D Result'
