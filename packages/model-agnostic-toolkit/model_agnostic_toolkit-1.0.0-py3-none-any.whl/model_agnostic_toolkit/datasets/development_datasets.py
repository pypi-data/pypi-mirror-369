import numpy as np
import pandas as pd

from . import ArtificialDataset
from ..types import DataType


class DevelopmentDataset(ArtificialDataset):
    """Development dataset containing random features and artificial interactions for a classification task, generated synthetically.
    Consists of five random base features without any interaction and three additional features containing interactions of base features.
    """

    def __init__(self, name: str = 'Development', file: str = './data/development_dataset.hdf5', n: int = 10000,
                 n_classes: int = 2, test_size: float = 0.2, force: bool = False) -> None:
        """Initializes Development dataset.

        Args:
            name (str, optional): Name of dataset instance. Defaults to 'Development'.
            file (str, optional): Relative or absolute path to dataset file. If a dataset exists here already and is loaded, the following arguments are ignored. Defaults to './data/development_dataset.hdf5'.
            n (int, optional): Number of samples to create when generating new data. Defaults to 10000.
            n_classes (int, optional): Number of classes to create when generating new data. Defaults to 2.
            test_size (float, optional): Proportion of all samples used for the testing data. Defaults to 0.2.
            force (bool, optional): Whether to force the generation of a new dataset and overwrite a possibly existing one in `file`. Defaults to False.
        """

        super().__init__(name=name, data_type=DataType.CLASSIFICATION, file=file,
                         n=n, n_classes=n_classes, test_size=test_size, force=force)

    def _generate(self) -> tuple[pd.DataFrame, pd.Series]:
        """Generates artificial Development dataset, containing random features and artificial interactions for a classification task.
        Data is generated according to the following procedure:

        1. Generate five base features with uniformly distributed random values in [0,1].
        These features do not interact.

        2. Compute three interaction features containing interactions between base features, then add Gaussian noise.
        Interactions are based on the concept of interaction proposed in [A Simple and Effective Model-Based Variable Importance Measure](https://arxiv.org/abs/1805.04755).
        The different interactions are computed as follows:

            a) `f(x,y) = x^y + N(0,0.1)`
            is interaction 0 using the base features 0 and 1.

            b) `f(x,y) = x * y + N(0,0.1)`
            is interaction 1 using the base features 2 and 4.

            c) `f(x,y) = e^x * y + N(0,0.1)`
            is interaction 2 using the base features 0 and 3.

        3. Compute a categorial target feature with the specified number of classes.
        Target features are computed as follows:

            i) For each target class, create a set of weights for the features.
            This yields a weight matrix of shape (n_features, n_classes)

            ii) For each target class, apply a softmax to the weights.
            This results in positive weights that add up to 1.0 for each class.

            iii) Calculate the weighted average of all features for each class.
            The resulting final class is obtained by finding the argmax of these values.

        Returns:
            Tuple[pd.DataFrame, pd.Series]: DataFrame of all features and Series of labels for all samples.
        """

        # setup
        n_base_features = 5
        n_interaction_features = 3
        n_features = n_base_features + n_interaction_features
        feature_names = ['base_{n}'.format(n=i) for i in range(n_base_features)] + \
                        ['interaction_{n}'.format(n=i) for i in range(n_interaction_features)]

        # create base features
        x_all = np.empty((self.n, n_features))
        x_all[:, :5] = np.random.random_sample((self.n, n_base_features))  # random base features

        # compute interactions
        x_all[:, 5] = x_all[:, 0] ** x_all[:, 1]  # interaction a) x^y
        x_all[:, 6] = x_all[:, 2] * x_all[:, 4]  # interaction b) x * y
        x_all[:, 7] = np.exp(x_all[:, 0]) * x_all[:, 3]  # interaction c) e^x * y
        x_all[:, 5:] += np.random.normal(loc=0.0, scale=0.1, size=(self.n, n_interaction_features))  # additional noise

        # compute target labels
        w = np.random.random_sample((n_features, self.n_classes))  # random base weights
        w = np.exp(w) / np.sum(np.exp(w), axis=0, keepdims=True)  # softmax for sum(w)=1.0 for each class
        result = np.matmul(x_all, w)
        y_all = np.argmax(result, axis=1)

        # construct data frame and series
        x_all = pd.DataFrame(x_all, columns=feature_names)
        y_all = pd.Series(y_all, name='class')

        return x_all, y_all


class DevelopmentBaseDataset(DevelopmentDataset):
    """Development Base dataset containing random features for a classification task, generated synthetically.
    Consists of five random base features, with the target variable being dependent on these features directly as well as specific interactions between them, as derived from the Development dataset.
    """

    def __init__(self, name: str = 'Development Base', *args, **kwargs) -> None:
        """Initializes Development Base dataset, inheriting from Development dataset but dropping interaction features.

        Positional and keyworded arguments are passed to the Development dataset initializer.

        Args:
            name (str, optional): Name of dataset instance. Defaults to 'Development Base'.
        """

        super().__init__(name=name, *args, **kwargs)

        # get interaction features
        interaction_features = list(filter(lambda c: c.startswith('interaction_'), self._x_train.columns))

        # drop interaction features from data
        self._x_train.drop(columns=interaction_features, inplace=True)
        self._x_test.drop(columns=interaction_features, inplace=True)
