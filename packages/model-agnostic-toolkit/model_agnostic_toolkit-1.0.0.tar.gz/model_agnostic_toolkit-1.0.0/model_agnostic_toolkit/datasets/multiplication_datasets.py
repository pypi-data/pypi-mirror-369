import numpy as np
import pandas as pd

from . import ArtificialDataset
from ..types import DataType


class MultiplicationOneDataset(ArtificialDataset):
    """Multiplication One Dataset containing random base features and artificial interactions for a regression task, generated synthetically.
    Consists of five observed random base features with one hidden interaction (multiplication).
    """

    def __init__(self, name: str = 'Multiplication One', file: str = './data/multiplication_one_dataset.hdf5',
                 n: int = 1000, test_size: float = 0.2, weights: list[float] = None,
                 noise_variance: float = 0.1, include_hidden: bool = False, force: bool = False) -> None:
        """Initializes Multiplication One dataset.

        Args:
            name (str, optional): Name of dataset instance. Defaults to 'Multiplication One'.
            file (str, optional): Relative or absolute path to dataset file. If a dataset exists here already and is loaded, the following arguments are ignored. Defaults to './data/multiplication_one_dataset.hdf5'.
            n (int, optional): Number of samples to create when generating new data. Defaults to 1000.
            test_size (float, optional): Proportion of all samples used for the testing data. Defaults to 0.2.
            weights (List[float], optional): Weighting coefficients for selected interaction and base features. Must have four entries. Defaults to [1.0, 1.0, 1.0, 1.0].
            noise_variance (float, optional): Variance of Gaussian noise that is added to every base of interaction feature and to the target. Defaults to 0.1.
            include_hidden (bool, optional): Whether to include the otherwise hidden interaction features in the data when generating it.
            force (bool, optional): Whether to force the generation of a new dataset and overwrite a possibly existing one in `file`. Defaults to False.

        Raises:
            ValueError: Raised if `weights` does not have the expected number of entries.
        """

        # set attributes
        if weights is None:
            weights = [1.0, 1.0, 1.0, 1.0]
        if len(weights) == 4:
            self.weights = weights
        else:
            raise ValueError('Passed weights must have 4 entries. Got {n_entries} instead.'
                             .format(n_entries=len(weights)))

        self.noise_variance = noise_variance
        self.include_hidden = include_hidden

        super().__init__(name=name, data_type=DataType.REGRESSION, file=file, n=n, test_size=test_size, force=force)

    def _generate(self) -> tuple[pd.DataFrame, pd.Series]:
        """Generates artificial Multiplication One dataset with five random base features and an artificial interaction for a regression task.
        Data is generated as follows:

        1. Five random base features `b0` to `b4` are sampled i.i.d. from `U(0,1) + N(0,s)` with variance `s` (sigma) for the Gaussian noise.

        2. An interaction is computed as `i0 = b0 * b1 + N(0,s)`.

        3. A target is computed as `y = w * [i0 b2 b3 b4]ᵀ + N(0,s)` with weights `w = [w0 w1 w2 w3]`.

        Returns:
            Tuple[pd.DataFrame, pd.Series]: DataFrame of all base features and Series of labels for all samples.
        """

        # setup
        n_features = 5
        feature_names = ['base_{n}'.format(n=n) for n in range(n_features)]

        # create random base features
        base = np.random.random_sample((n_features, self.n))
        base += np.random.normal(0, self.noise_variance, base.shape)

        # set coefficients
        weights = np.array(self.weights)  # interaction0, base2, base3, base4

        # compute interaction
        interaction0 = base[0] * base[1]
        interaction0 += np.random.normal(0, self.noise_variance, interaction0.shape)

        # compute target labels
        inputs = np.array([interaction0, base[2], base[3], base[4]])
        target = weights.T @ inputs
        target += np.random.normal(0, self.noise_variance, target.shape)

        # construct data frame and series
        if self.include_hidden:
            interaction_names = ['interaction_0']
            x_all = np.concatenate([base, interaction0[np.newaxis]])
            x_all = pd.DataFrame(x_all.T, columns=feature_names + interaction_names)
        else:
            x_all = pd.DataFrame(base.T, columns=feature_names)
        y_all = pd.Series(target, name='target')

        return x_all, y_all


class MultiplicationTwoDataset(ArtificialDataset):
    """Multiplication Two Dataset containing random base features and artificial interactions for a regression task, generated synthetically.
    Consists of five observed random base features with two hidden interactions (multiplications).
    """

    def __init__(self, name: str = 'Multiplication Two', file: str = './data/multiplication_two_dataset.hdf5',
                 n: int = 1000, test_size: float = 0.2, weights: list[float] = None,
                 noise_variance: float = 0.1, include_hidden: bool = False, force: bool = False) -> None:
        """Initializes Multiplication Two dataset.

        Args:
            name (str, optional): Name of dataset instance. Defaults to 'Multiplication Two'.
            file (str, optional): Relative or absolute path to dataset file. If a dataset exists here already and is loaded, the following arguments are ignored. Defaults to './data/multiplication_two_dataset.hdf5'.
            n (int, optional): Number of samples to create when generating new data. Defaults to 1000.
            test_size (float, optional): Proportion of all samples used for the testing data. Defaults to 0.2.
            weights (List[float], optional): Weighting coefficients for selected interaction and base features. Must have four entries. Defaults to [1.0, 1.0, 1.0, 1.0].
            noise_variance (float, optional): Variance of Gaussian noise that is added to every base of interaction feature and to the target. Defaults to 0.1.
            include_hidden (bool, optional): Whether to include the otherwise hidden interaction features in the data when generating it.
            force (bool, optional): Whether to force the generation of a new dataset and overwrite a possibly existing one in `file`. Defaults to False.

        Raises:
            ValueError: Raised if `weights` does not have the expected number of entries.
        """

        # set attributes
        if weights is None:
            weights = [1.0, 1.0, 1.0, 1.0]
        if len(weights) == 4:
            self.weights = weights
        else:
            raise ValueError('Passed weights must have 4 entries. Got {n_entries} instead.'
                             .format(n_entries=len(weights)))

        self.noise_variance = noise_variance
        self.include_hidden = include_hidden

        super().__init__(name=name, data_type=DataType.REGRESSION, file=file, n=n, test_size=test_size, force=force)

    def _generate(self) -> tuple[pd.DataFrame, pd.Series]:
        """Generates artificial Multiplication Two dataset with five random base features and two artificial interactions for a regression task.
        Data is generated as follows:

        1. Five random base features `b0` to `b4` are sampled i.i.d. from `U(0,1) + N(0,s)` with variance `s` (sigma) for the Gaussian noise.

        2. Two interactions are computed as

            a) `i0 = b0 * b1 + N(0,s)`.

            b) `i1 = b3 * b4 + N(0,s)`.

        3. A target is computed as `y = w * [i0 b2 i1 b4]ᵀ + N(0,s)` with weights `w = [w0 w1 w2 w3]`.

        Returns:
            Tuple[pd.DataFrame, pd.Series]: DataFrame of all base features and Series of labels for all samples.
        """

        # setup
        n_features = 5
        feature_names = ['base_{n}'.format(n=n) for n in range(n_features)]

        # create random base features
        base = np.random.random_sample((n_features, self.n))
        base += np.random.normal(0, self.noise_variance, base.shape)

        # set coefficients
        weights = np.array(self.weights)  # interaction0, base2, interaction1, base4

        # compute interactions
        interaction0 = base[0] * base[1]
        interaction1 = base[3] * base[4]
        interaction0 += np.random.normal(0, self.noise_variance, interaction0.shape)
        interaction1 += np.random.normal(0, self.noise_variance, interaction1.shape)

        # compute target labels
        inputs = np.array([interaction0, base[2], interaction1, base[4]])
        target = weights.T @ inputs
        target += np.random.normal(0, self.noise_variance, target.shape)

        # construct data frame and series
        if self.include_hidden:
            interaction_names = ['interaction_{n}'.format(n=n) for n in range(2)]
            x_all = np.concatenate([base, interaction0[np.newaxis], interaction1[np.newaxis]])
            x_all = pd.DataFrame(x_all.T, columns=feature_names + interaction_names)
        else:
            x_all = pd.DataFrame(base.T, columns=feature_names)
        y_all = pd.Series(target, name='target')

        return x_all, y_all


class MultiplicationThreeDataset(ArtificialDataset):
    """Multiplication Three Dataset containing random base features and artificial interactions for a regression task, generated synthetically.
    Consists of five observed random base features with two hidden interactions (multiplications).
    """

    def __init__(self, name: str = 'Multiplication Three', file: str = './data/multiplication_three_dataset.hdf5',
                 n: int = 1000, test_size: float = 0.2, weights: list[float] = None,
                 noise_variance: float = 0.1, include_hidden: bool = False, force: bool = False) -> None:
        """Initializes Multiplication Three dataset.

        Args:
            name (str, optional): Name of dataset instance. Defaults to 'Multiplication Three'.
            file (str, optional): Relative or absolute path to dataset file. If a dataset exists here already and is loaded, the following arguments are ignored. Defaults to './data/multiplication_three_dataset.hdf5'.
            n (int, optional): Number of samples to create when generating new data. Defaults to 1000.
            test_size (float, optional): Proportion of all samples used for the testing data. Defaults to 0.2.
            weights (List[float], optional): Weighting coefficients for selected interaction and base features. Must have four entries. Defaults to [1.0, 1.0, 1.0, 1.0].
            noise_variance (float, optional): Variance of Gaussian noise that is added to every base of interaction feature and to the target. Defaults to 0.1.
            include_hidden (bool, optional): Whether to include the otherwise hidden interaction features in the data when generating it.
            force (bool, optional): Whether to force the generation of a new dataset and overwrite a possibly existing one in `file`. Defaults to False.

        Raises:
            ValueError: Raised if `weights` does not have the expected number of entries.
        """

        # set attributes
        if weights is None:
            weights = [1.0, 1.0, 1.0, 1.0]
        if len(weights) == 4:
            self.weights = weights
        else:
            raise ValueError('Passed weights must have 4 entries. Got {n_entries} instead.'
                             .format(n_entries=len(weights)))

        self.noise_variance = noise_variance
        self.include_hidden = include_hidden

        super().__init__(name=name, data_type=DataType.REGRESSION, file=file, n=n, test_size=test_size, force=force)

    def _generate(self) -> tuple[pd.DataFrame, pd.Series]:
        """Generates artificial Multiplication Three dataset with five random base features and two artificial interactions for a regression task.
        Data is generated as follows:

        1. Five random base features `b0` to `b4` are sampled i.i.d. from `U(0,1) + N(0,s)` with variance `s` (sigma) for the Gaussian noise.

        2. Two interactions are computed as

            a) `i0 = b0 * b1 * b2 + N(0,s)`.

            b) `i1 = b1 * b4 + N(0,s)`.

        3. A target is computed as `y = w * [i0 b2 i1 b4]ᵀ + N(0,s)` with weights `w = [w0 w1 w2 w3]`.

        Returns:
            Tuple[pd.DataFrame, pd.Series]: DataFrame of all base features and Series of labels for all samples.
        """

        # setup
        n_features = 5
        feature_names = ['base_{n}'.format(n=n) for n in range(n_features)]

        # create random base features
        base = np.random.random_sample((n_features, self.n))
        base += np.random.normal(0, self.noise_variance, base.shape)

        # set coefficients
        weights = np.array(self.weights)  # interaction0, base2, interaction1, base4

        # compute interactions
        interaction0 = base[0] * base[1] * base[2]
        interaction1 = base[1] * base[4]
        interaction0 += np.random.normal(0, self.noise_variance, interaction0.shape)
        interaction1 += np.random.normal(0, self.noise_variance, interaction1.shape)

        # compute target labels
        inputs = np.array([interaction0, base[2], interaction1, base[4]])
        target = weights.T @ inputs
        target += np.random.normal(0, self.noise_variance, target.shape)

        # construct data frame and series
        if self.include_hidden:
            interaction_names = ['interaction_{n}'.format(n=n) for n in range(2)]
            x_all = np.concatenate([base, interaction0[np.newaxis], interaction1[np.newaxis]])
            x_all = pd.DataFrame(x_all.T, columns=feature_names + interaction_names)
        else:
            x_all = pd.DataFrame(base.T, columns=feature_names)
        y_all = pd.Series(target, name='target')

        return x_all, y_all


class MultiplicationFourDataset(ArtificialDataset):
    """Multiplication Four Dataset containing random base features and artificial interactions for a regression task, generated synthetically.
    Consists of five observed random base features with three hidden interactions (multiplications).
    """

    def __init__(self, name: str = 'Multiplication Four', file: str = './data/multiplication_four_dataset.hdf5',
                 n: int = 1000, test_size: float = 0.2, weights: list[float] = None,
                 noise_variance: float = 0.1, include_hidden: bool = False, force: bool = False) -> None:
        """Initializes Multiplication Four dataset.

        Args:
            name (str, optional): Name of dataset instance. Defaults to 'Multiplication Four'.
            file (str, optional): Relative or absolute path to dataset file. If a dataset exists here already and is loaded, the following arguments are ignored. Defaults to './data/multiplication_four_dataset.hdf5'.
            n (int, optional): Number of samples to create when generating new data. Defaults to 1000.
            test_size (float, optional): Proportion of all samples used for the testing data. Defaults to 0.2.
            weights (List[float], optional): Weighting coefficients for selected interaction and base features. Must have four entries. Defaults to [1.0, 1.0, 1.0, 1.0].
            noise_variance (float, optional): Variance of Gaussian noise that is added to every base of interaction feature and to the target. Defaults to 0.1.
            include_hidden (bool, optional): Whether to include the otherwise hidden interaction features in the data when generating it.
            force (bool, optional): Whether to force the generation of a new dataset and overwrite a possibly existing one in `file`. Defaults to False.

        Raises:
            ValueError: Raised if `weights` does not have the expected number of entries.
        """

        # set attributes
        if weights is None:
            weights = [1.0, 1.0, 1.0, 1.0]
        if len(weights) == 4:
            self.weights = weights
        else:
            raise ValueError('Passed weights must have 4 entries. Got {n_entries} instead.'
                             .format(n_entries=len(weights)))

        self.noise_variance = noise_variance
        self.include_hidden = include_hidden

        super().__init__(name=name, data_type=DataType.REGRESSION, file=file, n=n, test_size=test_size, force=force)

    def _generate(self) -> tuple[pd.DataFrame, pd.Series]:
        """Generates artificial Multiplication Four dataset with five random base features and three artificial interactions for a regression task.
        Data is generated as follows:

        1. Five random base features `b0` to `b4` are sampled i.i.d. from `U(0,1) + N(0,s)` with variance `s` (sigma) for the Gaussian noise.

        2. Three interactions are computed as

            a) `i0 = b0 * b1 + N(0,s)`.

            b) `i1 = b1 * b2 * b4 + N(0,s)`.

            c) `i2 = b2 * i0 + N(0,s)`.

        3. A target is computed as `y = w * [i2 b1 i1 b4]ᵀ + N(0,s)` with weights `w = [w0 w1 w2 w3]`.

        Returns:
            Tuple[pd.DataFrame, pd.Series]: DataFrame of all base features and Series of labels for all samples.
        """

        # setup
        n_features = 5
        feature_names = ['base_{n}'.format(n=n) for n in range(n_features)]

        # create random base features
        base = np.random.random_sample((n_features, self.n))
        base += np.random.normal(0, self.noise_variance, base.shape)

        # set coefficients
        weights = np.array(self.weights)  # interaction2, base1, interaction1, base4

        # compute interactions
        interaction0 = base[0] * base[1]
        interaction1 = base[1] * base[2] * base[4]
        interaction2 = base[2] * interaction0
        interaction0 += np.random.normal(0, self.noise_variance, interaction0.shape)
        interaction1 += np.random.normal(0, self.noise_variance, interaction1.shape)
        interaction2 += np.random.normal(0, self.noise_variance, interaction2.shape)

        # compute target labels
        inputs = np.array([interaction2, base[1], interaction1, base[4]])
        target = weights.T @ inputs
        target += np.random.normal(0, self.noise_variance, target.shape)

        # construct data frame and series
        if self.include_hidden:
            interaction_names = ['interaction_{n}'.format(n=n) for n in range(3)]
            x_all = np.concatenate([base, interaction0[np.newaxis], interaction1[np.newaxis], interaction2[np.newaxis]])
            x_all = pd.DataFrame(x_all.T, columns=feature_names + interaction_names)
        else:
            x_all = pd.DataFrame(base.T, columns=feature_names)
        y_all = pd.Series(target, name='target')

        return x_all, y_all
