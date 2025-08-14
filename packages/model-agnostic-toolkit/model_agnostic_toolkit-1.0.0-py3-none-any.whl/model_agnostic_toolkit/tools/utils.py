import numpy as np
from typing import Generator, Union
from itertools import combinations

from ..analyzer import Analyzer
from ..model import Model
from ..datasets import Dataset
from . import Tool


def compute_tool(tool_class: type[Tool], model: Model, dataset: Dataset, features: list[Union[str, tuple[str, str]]], 
                 analyzer: Analyzer = None, **requirements) -> dict:
    """Computes partial dependence values for the given features.

    Args:
        tool_class (Type[Tool]): Tool class to find or initialize an instance of. Should be a class to be instantiated, not the instance itself.
        model (Model): Model to use for the computation.
        dataset (Dataset): Dataset to use for the computation.
        features (Union[str, Tuple[str, str]]): List of features of feature_pairs to run the computation for.
        analyzer (Analyzer): Analyzer the tool is run from.

    Returns:
        Dict: The computed partial dependence values.
    """

    # look for reusable tool
    try:
        analyzer, tool = analyzer._find_reuse_tool(tool_class, model, dataset, **requirements)
    except AttributeError:  # if analyzer is None
        analyzer, tool = None, None

    if tool is not None:
        # reuse tool
        return analyzer.run_tool(tool, features, temp=True)
    tool = tool_class(**requirements)
    return tool.run(model, dataset, features, analyzer=None)


def center_1D(y_values: np.ndarray, x_grid: np.ndarray) -> np.ndarray:
    """Centers a 1D piecewise linear function to have a mean of zero.

    Args:
        y_values (np.ndarray): Array of function values y_i at grid points x_i.
        x_grid (np.ndarray): Array of grid points x_i. Ascending order assumed. First and last element limit the domain.

    Returns:
        np.ndarray: The centered y-values.
    """

    bin_sizes_x = x_grid[1:] - x_grid[:-1]
    bin_y_avgs = 0.5 * (y_values[:-1] + y_values[1:])

    y_avg = (bin_y_avgs * bin_sizes_x).sum() / (x_grid[-1] - x_grid[0])

    return y_values - y_avg


def center_2D(z_values: np.ndarray, xy_grid: list[np.ndarray]) -> np.ndarray:
    """Centers a 2D piecewise linear function to have a mean of zero.

    Args:
        z_values (np.ndarray): Array of function values z_ij at grid points (x_i, y_j).
        xy_grid (List[np.ndarray]): List of two arrays with grid point x_i and y_i, respectively. Ascending order assumed for both. First and last elements limit the domain.

    Returns:
        np.ndarray: The centered z-values.
    """

    x_grid, y_grid = xy_grid

    bin_sizes_x = (x_grid[1:] - x_grid[:-1]).reshape(-1, 1)
    bin_sizes_y = (y_grid[1:] - y_grid[:-1]).reshape(1, -1)
    bin_areas = bin_sizes_x * bin_sizes_y
    bin_z_avgs = 0.25 * (z_values[:-1, :-1] + z_values[1:, :-1] + z_values[:-1, 1:] + z_values[1:, 1:])

    z_avg = (bin_z_avgs * bin_areas).sum() / ((x_grid[-1] - x_grid[0]) * (y_grid[-1] - y_grid[0]))

    return z_values - z_avg


def interpolate_1D(x_samples: np.ndarray, y_values: np.ndarray, x_grid: np.ndarray) -> np.ndarray:
    """Evaluates a 1D piecewise linear function for a given batch of x-samples.

    Args:
        x_samples (np.ndarray): Array of all x-samples to evaluate the function at.
        y_values (np.ndarray): Array of function values y_i at grid points x_i.
        x_grid (np.ndarray): Array of grid points x_i. Ascending order assumed.

    Returns:
        np.ndarray: Array of all function evaluations y for x-samples in batch.
    """

    y_samples = np.empty(len(x_samples))

    for i, x_sample in enumerate(x_samples):
        # interpolate for x_sample in grid bins, else extrapolate from first or last bin
        x_ge_sample = (x_grid >= x_sample)
        x_bin = max(0, np.argmax(x_ge_sample) - 1) if x_ge_sample.any() else (len(x_grid) - 2)

        p_x = (x_sample - x_grid[x_bin]) / (x_grid[x_bin+1] - x_grid[x_bin])
        y_samples[i] = y_values[x_bin] * (1-p_x) + y_values[x_bin+1] * p_x

    return y_samples


def interpolate_2D(xy_samples: np.ndarray, z_values: np.ndarray, xy_grid: list[np.ndarray]) -> np.ndarray:
    """Evaluates a 2D piecewise linear function for a given batch of (x, y)-samples

    Args:
        xy_samples (np.ndarray): Array of all (x, y)-samples to evaluate the function at.
        z_values (np.ndarray): Array of function values z_ij at grid points (x_i, y_j).
        xy_grid (List[np.ndarray]): List of two arrays with grid point x_i and y_i, respectively. Ascending order assumed for both.

    Returns:
        np.ndarray: Array of all function evaluations z for (x, y)-samples in batch.
    """

    z_samples = np.empty(len(xy_samples))
    x_grid, y_grid = xy_grid

    for i, (x_sample, y_sample) in enumerate(xy_samples):
        # interpolate for xy_sample in grid bins, else extrapolate from first or last bin in either dimension
        x_ge_sample = (x_grid >= x_sample)
        y_ge_sample = (y_grid >= y_sample)
        x_bin = max(0, np.argmax(x_ge_sample) - 1) if x_ge_sample.any() else (len(x_grid) - 2)
        y_bin = max(0, np.argmax(y_ge_sample) - 1) if y_ge_sample.any() else (len(y_grid) - 2)

        p_x = (x_sample - x_grid[x_bin]) / (x_grid[x_bin+1] - x_grid[x_bin])
        p_y = (y_sample - y_grid[y_bin]) / (y_grid[y_bin+1] - y_grid[y_bin])
        z_samples[i] = (z_values[x_bin, y_bin] * (1-p_y) * (1-p_x) +
                        z_values[x_bin+1, y_bin] * (1-p_y) * p_x +
                        z_values[x_bin, y_bin+1] * p_y * (1-p_x) +
                        z_values[x_bin+1, y_bin+1] * p_y * p_x)

    return z_samples


def features_from_pairs(feature_pairs: list[tuple[str, str]]) -> list[str]:
    """Retrieve a list of all individual features given a list of feature pairs.

    Args:
        feature_pairs (List[Tuple[str, str]]): List of feature pair tuples.

    Returns:
        List[str]: List of individual features.
    """

    features = []
    for feature_pair in feature_pairs:
        for feature in feature_pair:
            if feature not in features:
                features.append(feature)

    return features


def pairs_from_features(features: list[str]) -> list[tuple[str, str]]:
    """Retrieve a list of all feature pairs given a list of individual features.

    Args:
        features: (List[str]): List of individual features.

    Returns:
        List[Tuple[str, str]]: List of feature pair tuples.
    """

    return list(combinations(features, 2))


def interaction_name_generator(existing_features: list[str]) -> Generator:
    """Generates names for new interaction features while skipping possibly existing features.

    Args:
        existing_features (List[str]): List of features already existing in the dataset.

    Yields:
        Generator: All non-existing interaction feature names of the form 'interaction_0'.
    """

    n = 0
    while True:
        name = f'interaction_{n}'
        if name not in existing_features:
            yield name
        n += 1
