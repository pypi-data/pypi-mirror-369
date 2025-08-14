import numpy as np


def _calculate_i(pd: np.ndarray, continuous: bool) -> float:
    """Calculates the importance score for a feature's given partial dependence values.
    Computation differs depending on whether the feature is continuous or categorical.

    Args:
        pd (np.ndarray): 1D partial dependence values for the feature.
        continuous (bool): Whether the feature is continuous or not.

    Returns:
        float: The computed importance score.
    """

    if continuous:
        return np.std(pd, ddof=1)
    x_max = np.max(pd)
    x_min = np.min(pd)
    return (x_max - x_min) / 4


def compute_vip(pdp: np.ndarray, continuous: bool = True) -> float:
    """Computes the VIP score for a particular feature or feature pair from given partial depencence values.

    Args:
        pdp (np.ndarray): 1D partial dependence values for the single feature or matrix of partial dependence values for the feature pair (a, b).
        continuous (bool, optional): Whether the feature or feature pair is continuous or not. Defaults to True.

    Returns:
        float: The computed VIP score.
    """

    if len(pdp.shape) == 1:
        return _calculate_i(pdp, continuous)

    i_values_a = [_calculate_i(pd, continuous) for pd in pdp]
    i_values_b = [_calculate_i(pd, continuous) for pd in pdp.T]
    return (np.std(i_values_a) + np.std(i_values_b)) / 2
