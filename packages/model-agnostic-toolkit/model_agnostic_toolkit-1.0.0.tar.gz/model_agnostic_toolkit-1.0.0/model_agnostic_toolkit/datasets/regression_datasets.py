import numpy as np
import pandas as pd

from ..types import DataType
from .dataset import ArtificialDataset


class RegressionOneDataset(ArtificialDataset):
    """Regression One Dataset containing random base features and artificial interactions for a regression task, generated synthetically.
    Consists of twenty observed random base features with no hidden interactions.
    """

    def __init__(
        self,
        name: str = "Regression One",
        file: str = "./data/regression_one_dataset.hdf5",
        n: int = 1000,
        test_size: float = 0.2,
        weights: list[float] = None,
        noise_variance: float = 0.1,
        force: bool = False,
        random_state: int = 42,
    ) -> None:
        """Initializes Regression One dataset.py.

        Args:
            name (str, optional): Name of dataset.py instance. Defaults to 'Regression One'.
            file (str, optional): Relative or absolute path to dataset.py file. If a dataset.py exists here already and is loaded, the following arguments are ignored. Defaults to './data/regression_one_dataset.hdf5'.
            n (int, optional): Number of samples to create when generating new data. Defaults to 1000.
            test_size (float, optional): Proportion of all samples used for the testing data. Defaults to 0.2.
            weights (List[float], optional): Weighting coefficients for selected interaction and base features. Must have ten entries. Defaults to [1.0, 1.0, 0.8, 0.8, 0.6, 0.6, 0.4, 0.4, 0.2, 0.2].
            noise_variance (float, optional): Variance of Gaussian noise that is added to every base of interaction feature and to the target. Defaults to 0.1.
            force (bool, optional): Whether to force the generation of a new dataset.py and overwrite a possibly existing one in `file`. Defaults to False.

        Raises:
            ValueError: Raised if `weights` does not have the expected number of entries.
        """
        if weights is None:
            weights = [1.0, 1.0, 0.8, 0.8, 0.6, 0.6, 0.4, 0.4, 0.2, 0.2]
        np.random.seed(random_state)
        # set attributes
        if len(weights) == 10:
            self.weights = weights
        else:
            raise ValueError(
                "Passed weights must have 10 entries. Got {n_entries} instead.".format(
                    n_entries=len(weights)
                )
            )

        self.noise_variance = noise_variance

        super().__init__(
            name=name,
            data_type=DataType.REGRESSION,
            file=file,
            n=n,
            test_size=test_size,
            force=force,
            random_state=random_state,
        )

    def _generate(self) -> tuple[pd.DataFrame, pd.Series]:
        """Generates artificial Regression One dataset.py with twenty random base features and no artificial interaction for a regression task.
        Data is generated as follows:

        1. Twenty random base features `b0` to `b19` are sampled i.i.d. from `U(0,1) + N(0,s)` with variance `s` (sigma) for the Gaussian noise.

        2. A target is computed as `y = w * [b0 b1 b2 b3 b4 b5 b6 b7 b8 b9 ]ᵀ + N(0,s)` with weights `w = [w0 w1 w2 w3 w4 w5 w6w w7 w8 w9]`.

        Returns:
            Tuple[pd.DataFrame, pd.Series]: DataFrame of all base features and Series of labels for all samples.
        """

        # setup
        n_features = 20
        feature_names = ["base_{n}".format(n=n) for n in range(n_features)]

        # create random base features
        base = np.random.random_sample((n_features, self.n))
        base += np.random.normal(0, self.noise_variance, base.shape)

        # set coefficients
        weights = np.array(self.weights)  # interaction0, base2, base3, base4

        # compute target labels
        inputs = np.array(
            [
                base[0],
                base[1],
                base[2],
                base[3],
                base[4],
                base[5],
                base[6],
                base[7],
                base[8],
                base[9],
            ]
        )
        target = weights.T @ inputs
        target += np.random.normal(0, self.noise_variance, target.shape)

        # construct data frame and series
        x_all = pd.DataFrame(base.T, columns=feature_names)
        y_all = pd.Series(target, name="target")

        return x_all, y_all


class RegressionTwoDataset(ArtificialDataset):
    """Regression Two Dataset containing random base features and artificial interactions for a regression task, generated synthetically.
    Consists of twenty observed random base features with ten hidden interactions.
    """

    def __init__(
        self,
        name: str = "Regression Two",
        file: str = "./data/regression_two_dataset.hdf5",
        n: int = 1000,
        test_size: float = 0.2,
        weights: list[float] = None,
        noise_variance: float = 0.1,
        include_hidden: bool = False,
        force: bool = False,
        random_state: int = 42,
    ) -> None:
        """Initializes Interaction One dataset.

        Args:
            name (str, optional): Name of dataset instance. Defaults to 'Regression Two'.
            file (str, optional): Relative or absolute path to dataset file. If a dataset exists here already and is loaded, the following arguments are ignored. Defaults to './data/regression_two_dataset.hdf5'.
            n (int, optional): Number of samples to create when generating new data. Defaults to 1000.
            test_size (float, optional): Proportion of all samples used for the testing data. Defaults to 0.2.
            weights (List[float], optional): Weighting coefficients for selected interaction and base features. Must have ten entries. Defaults to [1.0, 1.0, 1.0, 1.0, 0.8, 0.8, 0.6, 0.6, 0.4, 0.4].
            noise_variance (float, optional): Variance of Gaussian noise that is added to every base of interaction feature and to the target. Defaults to 0.1.
            include_hidden (bool, optional): Whether to include the otherwise hidden interaction features in the data when generating it.
            force (bool, optional): Whether to force the generation of a new dataset and overwrite a possibly existing one in `file`. Defaults to False.

        Raises:
            ValueError: Raised if `weights` does not have the expected number of entries.
        """
        if weights is None:
            weights = [1.0, 1.0, 1.0, 1.0, 0.8, 0.8, 0.6, 0.6, 0.4, 0.4]
        np.random.seed(random_state)
        # set attributes
        if len(weights) == 10:
            self.weights = weights
        else:
            raise ValueError(
                "Passed weights must have 10 entries. Got {n_entries} instead.".format(
                    n_entries=len(weights)
                )
            )

        self.noise_variance = noise_variance
        self.include_hidden = include_hidden

        super().__init__(
            name=name,
            data_type=DataType.REGRESSION,
            file=file,
            n=n,
            test_size=test_size,
            force=force,
            random_state=random_state,
        )

    def _generate(self) -> tuple[pd.DataFrame, pd.Series]:
        """Generates artificial Regression Two dataset with twenty random base features and ten artificial interaction for a regression task.
        Data is generated as follows:

        1. Twenty random base features `b0` to `b19` are sampled i.i.d. from `U(0,1) + N(0,s)` with variance `s` (sigma) for the Gaussian noise.

        2. Ten interaction are computed as
            `i0 = b0 * b1 + N(0,s)`
            `i1 = b0 * b2 + N(0,s)`
            `i2 = b1 * b2 + N(0,s)`
            `i3 = b3 * b4 + N(0,s)`
            `i4 = b5 * b6 + N(0,s)`
            `i5 = b7 * b8 + N(0,s)`
            `i6 = b3 * b5 + N(0,s)`
            `i7 = b3 * b6 + N(0,s)`
            `i8 = b3 * b7 + N(0,s)`
            `i9 = b3 * b8 + N(0,s)`

        3. A target is computed as `y = w * [i0 i1 i2 i3 i4 i5 i6 i7 i8 i9]ᵀ + N(0,s)` with weights `w = [w0 w1 w2 w3 w4 w5 w6 w7 w8 w9]`.

        Returns:
            Tuple[pd.DataFrame, pd.Series]: DataFrame of all base features and Series of labels for all samples.
        """

        # setup
        n_features = 20
        feature_names = ["base_{n}".format(n=n) for n in range(n_features)]

        # create random base features
        base = np.random.random_sample((n_features, self.n))
        base += np.random.normal(0, self.noise_variance, base.shape)

        # set coefficients
        weights = np.array(self.weights)  # interaction0, base2, base3, base4

        # compute interaction
        interaction0 = base[0] * base[1]
        interaction0 += np.random.normal(0, self.noise_variance, interaction0.shape)

        interaction1 = base[0] * base[2]
        interaction1 += np.random.normal(0, self.noise_variance, interaction0.shape)

        interaction2 = base[1] * base[2]
        interaction2 += np.random.normal(0, self.noise_variance, interaction0.shape)

        interaction3 = base[3] * base[4]
        interaction3 += np.random.normal(0, self.noise_variance, interaction0.shape)

        interaction4 = base[5] * base[6]
        interaction4 += np.random.normal(0, self.noise_variance, interaction0.shape)

        interaction5 = base[7] * base[8]
        interaction5 += np.random.normal(0, self.noise_variance, interaction0.shape)

        interaction6 = base[3] * base[5]
        interaction6 += np.random.normal(0, self.noise_variance, interaction0.shape)

        interaction7 = base[3] * base[6]
        interaction7 += np.random.normal(0, self.noise_variance, interaction0.shape)

        interaction8 = base[3] * base[7]
        interaction8 += np.random.normal(0, self.noise_variance, interaction0.shape)

        interaction9 = base[3] * base[8]
        interaction9 += np.random.normal(0, self.noise_variance, interaction0.shape)

        # compute target labels
        inputs = np.array(
            [
                interaction0,
                interaction1,
                interaction2,
                interaction3,
                interaction4,
                interaction5,
                interaction6,
                interaction7,
                interaction8,
                interaction9,
            ]
        )
        target = weights.T @ inputs
        target += np.random.normal(0, self.noise_variance, target.shape)

        # construct data frame and series
        if self.include_hidden:
            interaction_names = [
                "interaction_0",
                "interaction1",
                "interaction2",
                "interaction3",
                "interaction4",
                "interaction5",
                "interaction6",
                "interaction7",
                "interaction8",
                "interaction9",
            ]
            x_all = np.concatenate(
                [base, interaction0[np.newaxis]],
                interaction1[np.newaxis],
                interaction2[np.newaxis],
                interaction3[np.newaxis],
                interaction4[np.newaxis],
                interaction5[np.newaxis],
                interaction6[np.newaxis],
                interaction7[np.newaxis],
                interaction8[np.newaxis],
                interaction9[np.newaxis],
            )
            x_all = pd.DataFrame(x_all.T, columns=feature_names + interaction_names)
        else:
            x_all = pd.DataFrame(base.T, columns=feature_names)
        y_all = pd.Series(target, name="target")

        return x_all, y_all


class RegressionThreeDataset(ArtificialDataset):
    """Regression Three Dataset containing random base features and artificial interactions for a regression task, generated synthetically.
    Consists of twenty observed random base features with five hidden interactions.
    """

    def __init__(
        self,
        name: str = "Regression Three",
        file: str = "./data/regression_three_dataset.hdf5",
        n: int = 1000,
        test_size: float = 0.2,
        weights: list[float] = None,
        noise_variance: float = 0.1,
        include_hidden: bool = False,
        force: bool = False,
        random_state: int = 42,
    ) -> None:
        """Initializes Interaction One dataset.

        Args:
            name (str, optional): Name of dataset instance. Defaults to 'Regression Three'.
            file (str, optional): Relative or absolute path to dataset file. If a dataset exists here already and is loaded, the following arguments are ignored. Defaults to './data/regression_three_dataset.hdf5'.
            n (int, optional): Number of samples to create when generating new data. Defaults to 1000.
            test_size (float, optional): Proportion of all samples used for the testing data. Defaults to 0.2.
            weights (List[float], optional): Weighting coefficients for selected interaction and base features. Must have ten entries. Defaults to [1.0, 0.8, 0.6, 0.4, 0.2, 1.0, 0.8, 0.6, 0.4, 0.2].
            noise_variance (float, optional): Variance of Gaussian noise that is added to every base of interaction feature and to the target. Defaults to 0.1.
            include_hidden (bool, optional): Whether to include the otherwise hidden interaction features in the data when generating it.
            force (bool, optional): Whether to force the generation of a new dataset and overwrite a possibly existing one in `file`. Defaults to False.

        Raises:
            ValueError: Raised if `weights` does not have the expected number of entries.
        """
        if weights is None:
            weights = [1.0, 0.8, 0.6, 0.4, 0.2, 1.0, 0.8, 0.6, 0.4, 0.2]
        np.random.seed(random_state)
        # set attributes
        if len(weights) == 10:
            self.weights = weights
        else:
            raise ValueError(
                "Passed weights must have 10 entries. Got {n_entries} instead.".format(
                    n_entries=len(weights)
                )
            )

        self.noise_variance = noise_variance
        self.include_hidden = include_hidden

        super().__init__(
            name=name,
            data_type=DataType.REGRESSION,
            file=file,
            n=n,
            test_size=test_size,
            force=force,
            random_state=random_state,
        )

    def _generate(self) -> tuple[pd.DataFrame, pd.Series]:
        """Generates artificial Regression Three dataset with twenty random base features and 5 artificial interactions for a regression task.
        Data is generated as follows:

        1. Twenty random base features `b0` to `b19` are sampled i.i.d. from `U(0,1) + N(0,s)` with variance `s` (sigma) for the Gaussian noise.

        2. Five interaction are computed as
            `i0 = b0 * b1 + N(0,s)`
            `i1 = b0 * b2 + N(0,s)`
            `i2 = b1 * b2 + N(0,s)`
            `i3 = b1 * b4 + N(0,s)`
            `i4 = b1 * b5 + N(0,s)`

        3. A target is computed as `y = w * [b0 b1 b2 b3 b4 i0 i1 i2 i3 i4]ᵀ + N(0,s)` with weights `w = [w0 w1 w2 w3 w4 w5 w6 w7 w8 w9]`.

        Returns:
            Tuple[pd.DataFrame, pd.Series]: DataFrame of all base features and Series of labels for all samples.
        """

        # setup
        n_features = 20
        feature_names = ["base_{n}".format(n=n) for n in range(n_features)]

        # create random base features
        base = np.random.random_sample((n_features, self.n))
        base += np.random.normal(0, self.noise_variance, base.shape)

        # set coefficients
        weights = np.array(self.weights)  # interaction0, base2, base3, base4

        # compute interaction
        interaction0 = base[0] * base[1]
        interaction0 += np.random.normal(0, self.noise_variance, interaction0.shape)

        interaction1 = base[0] * base[2]
        interaction1 += np.random.normal(0, self.noise_variance, interaction0.shape)

        interaction2 = base[1] * base[2]
        interaction2 += np.random.normal(0, self.noise_variance, interaction0.shape)

        interaction3 = base[1] * base[4]
        interaction3 += np.random.normal(0, self.noise_variance, interaction0.shape)

        interaction4 = base[2] * base[5]
        interaction4 += np.random.normal(0, self.noise_variance, interaction0.shape)

        # compute target labels
        inputs = np.array(
            [
                base[0],
                base[1],
                base[2],
                base[3],
                base[4],
                interaction0,
                interaction1,
                interaction2,
                interaction3,
                interaction4,
            ]
        )
        target = weights.T @ inputs
        target += np.random.normal(0, self.noise_variance, target.shape)

        # construct data frame and series
        if self.include_hidden:
            interaction_names = [
                "interaction_0",
                "interaction1",
                "interaction2",
                "interaction3",
                "interaction4",
            ]
            x_all = np.concatenate(
                [base, interaction0[np.newaxis]],
                interaction1[np.newaxis],
                interaction2[np.newaxis],
            )
            x_all = pd.DataFrame(x_all.T, columns=feature_names + interaction_names)
        else:
            x_all = pd.DataFrame(base.T, columns=feature_names)
        y_all = pd.Series(target, name="target")

        return x_all, y_all


class RegressionFourDataset(ArtificialDataset):
    """Regression Four Dataset containing random base features and no artificial interactions for a regression task, generated synthetically.
    Consists of twenty observed random base features with no hidden interactions.
    """

    def __init__(
        self,
        name: str = "Regression Four",
        file: str = "./data/regression_four_dataset.hdf5",
        n: int = 1000,
        test_size: float = 0.2,
        noise_variance: float = 0.1,
        force: bool = False,
        random_state: int = 42,
    ) -> None:
        """Initializes Interaction One dataset.py.

        Args:
            name (str, optional): Name of dataset.py instance. Defaults to 'Regression Four'.
            file (str, optional): Relative or absolute path to dataset.py file. If a dataset.py exists here already and is loaded, the following arguments are ignored. Defaults to './data/regression_four_dataset.hdf5'.
            n (int, optional): Number of samples to create when generating new data. Defaults to 1000.
            test_size (float, optional): Proportion of all samples used for the testing data. Defaults to 0.2.
            noise_variance (float, optional): Variance of Gaussian noise that is added to every base of interaction feature and to the target. Defaults to 0.1.
            force (bool, optional): Whether to force the generation of a new dataset.py and overwrite a possibly existing one in `file`. Defaults to False.
        """

        # set attributes

        self.noise_variance = noise_variance
        np.random.seed(random_state)

        super().__init__(
            name=name,
            data_type=DataType.REGRESSION,
            file=file,
            n=n,
            test_size=test_size,
            force=force,
            random_state=random_state,
        )

    def _generate(self) -> tuple[pd.DataFrame, pd.Series]:
        """Generates artificial Regression Four dataset.py with twenty random base features and no artificial interaction for a regression task.
        The target is independent of the random base features.
        Data is generated as follows:

        1. Twenty random base features `b0` to `b19` are sampled i.i.d. from `U(0,1) + N(0,s)` with variance `s` (sigma) for the Gaussian noise.

        2. A target is computed as `N(0,s)`

        Returns:
            Tuple[pd.DataFrame, pd.Series]: DataFrame of all base features and Series of labels for all samples.
        """

        # setup
        n_features = 20
        feature_names = ["base_{n}".format(n=n) for n in range(n_features)]

        # create random base features
        base = np.random.random_sample((n_features, self.n))
        base += np.random.normal(0, self.noise_variance, base.shape)

        # compute target labels
        target = np.random.normal(0, self.noise_variance, self.n)

        # construct data frame and series
        x_all = pd.DataFrame(base.T, columns=feature_names)
        y_all = pd.Series(target, name="target")

        return x_all, y_all