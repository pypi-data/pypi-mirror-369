import os
from abc import ABC, abstractmethod
from itertools import combinations

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from ..types import DataType


class Dataset(ABC):
    """Base class for all datasets.
    (abstract base class, derive)

    Attributes:
        name (str): Name of the dataset.
        data_type (DataType): Type of labelled data (either classification or regression).
        features (List[str]): All features in the dataset.
        feature_pairs (List[Tuple[str, str]]): All possible pairs of two features in the dataset.
        target (str): The target variable name.
    """

    def __init__(self, name: str, data_type: DataType) -> None:
        """Initializes abstract base of dataset with given name and type.

        Args:
            name (str): Name of the dataset.
            data_type (DataType): Type of labelled data (either classification or regression).
        """

        self.name = name
        self.data_type = data_type

    @abstractmethod
    def get_train(self) -> tuple[pd.DataFrame, pd.Series]:
        """Provides access to training data.
        (abstract method, override)

        Returns:
            Tuple[pd.DataFrame, pd.Series]: DataFrame with training data and Series with training target labels.
        """

        pass

    @abstractmethod
    def get_test(self) -> tuple[pd.DataFrame, pd.Series]:
        """Provides access to testing data.
        If no testing data is present, returns the training data.
        (abstract method, override)

        Returns:
            Tuple[pd.DataFrame, pd.Series]: DataFrame with testing data and Series with testing target labels.
        """

        pass

    def get_all(self) -> tuple[pd.DataFrame, pd.Series]:
        """Provides access to all data by concatenating training a testing data.

        Returns:
            Tuple[pd.DataFrame, pd.Series]: DataFrame with all data and Series with all target labels.
        """

        x_train, y_train = self.get_train()
        x_test, y_test = self.get_test()

        x_all = pd.concat([x_train, x_test])
        y_all = pd.concat([y_train, y_test])

        return x_all, y_all

    @property
    def features(self) -> list[str]:
        """Names of all features in the dataset.

        Returns:
            List[str]: List of all features in the dataset.
        """

        return list(self._x_train.columns)

    @property
    def feature_pairs(self) -> list[tuple[str, str]]:
        """Name tuples for all combinations of two features in the dataset.

        Returns:
            List[Tuple[str, str]]: List of tuples of all feature pairs in the dataset
        """

        return list(combinations(self.features, 2))

    @property
    def target(self) -> str:
        """Name of target variable. 'target' if no name is specified.

        Returns:
            str: Target variable name.
        """

        target_variable = self._y_train.name
        if target_variable is None:
            target_variable = 'target'

        return str(target_variable)


class ArtificialDataset(Dataset):
    """Base class for all artificially generated datasets.
    (abstract base class, derive)

    Attributes:
        file (str): File where data was loaded from or saved to.
        n (int): Number of samples of training and testing set combined.
        n_classes (int): Number of classes for target label.
        test_size (float): Fraction of samples in testing set.
    """

    def __init__(self, name: str, data_type: DataType, file: str, n: int, test_size: float, n_classes: int = None,
                 force: bool = False, verbose: bool = True, random_state: int = None) -> None:
        """Initializes artificial dataset, setting attributes and either loading data or generating it if file does not exist.

        Args:
            name (str, optional): Name of dataset instance.
            file (str, optional): Relative or absolute path to dataset file.
            n (int, optional): Number of samples of training and testing set combined.
            test_size (float, optional): Fraction of samples in testing set.
            n_classes (int, optional): Number of classes for classification datasets. Set to None for regression datasets. Defaults to None.
            force (bool, optional): Whether to force the generation of a new dataset and overwrite a possibly existing one in `file`. Defaults to False.
            verbose (bool, optional): Whether status messages should be printed or not. Defaults to True.
            random_state (int, optional): Specifies the random state. If not set, the generated dataset is random.
        """

        super().__init__(name=name, data_type=data_type)

        if random_state:
            self.random_state = random_state

        self.file = file

        if os.path.exists(self.file) and not force:
            if verbose:
                print('Loading data from {file} ...'.format(file=self.file), end=' ')

            # load data from file
            self._load(self.file)

            # set attributes
            self.n = len(self._y_train) + len(self._y_test)
            self.test_size = len(self._y_test) / self.n
            if self.data_type == DataType.CLASSIFICATION:
                self.n_classes = np.unique(self._y_train).size

        else:
            if verbose:
                print('Generating data ...', end=' ')

            # set attributes
            self.n = n
            self.test_size = test_size
            if self.data_type == DataType.CLASSIFICATION:
                self.n_classes = n_classes

            # generate all data artificially
            x_all, y_all = self._generate()

            # apply train-test-split
            x_train, x_test, y_train, y_test = train_test_split(
                x_all, y_all, test_size=self.test_size,
                stratify=(
                    y_all if self.data_type == DataType.CLASSIFICATION else None))

            # store training and testing data
            self._x_train = x_train
            self._x_test = x_test
            self._y_train = y_train
            self._y_test = y_test

            self._save(self.file)

        if verbose:
            print('done.')

    @abstractmethod
    def _generate(self) -> tuple[pd.DataFrame, pd.Series]:
        """Generates all artificial data samples.
        (abstract method, override)

        Returns:
            Tuple[pd.DataFrame, pd.Series]: DataFrame of all features and Series of target values for all samples.
        """

        pass

    def _save(self, file: str) -> None:
        """Saves training and testing data to specified file.
        If target directory does not exist, creates directory.

        Args:
            file (str): Path to dataset file.
        """

        # create directory if needed
        directory = os.path.split(self.file)[0]
        os.makedirs(directory, exist_ok=True)

        # store HDF5 file
        self._x_train.to_hdf(file, key='train/x', mode='a')
        self._x_test.to_hdf(file, key='test/x', mode='a')
        self._y_train.to_hdf(file, key='train/y', mode='a')
        self._y_test.to_hdf(file, key='test/y', mode='a')

    def _load(self, file: str) -> None:
        """Loads training and testing data from specified file.

        Args:
            file (str): Path to dataset file.
        """

        self._x_train = pd.read_hdf(file, key='train/x')
        self._x_test = pd.read_hdf(file, key='test/x')
        self._y_train = pd.read_hdf(file, key='train/y')
        self._y_test = pd.read_hdf(file, key='test/y')

    def get_train(self) -> tuple[pd.DataFrame, pd.Series]:

        return self._x_train, self._y_train

    def get_test(self) -> tuple[pd.DataFrame, pd.Series]:

        return self._x_test, self._y_test
