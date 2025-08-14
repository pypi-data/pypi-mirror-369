import pandas as pd

from . import Dataset
from ..types import DataType


class PreloadedDataset(Dataset):
    """Preloaded dataset containing data from another source.

    Attributes:
        n (int): Number of samples of training and testing set combined.
        test_size (float): Fraction of samples in testing set.
    """

    def __init__(self, x_train: pd.DataFrame, y_train: pd.Series, x_test: pd.DataFrame, y_test: pd.Series, data_type:
    DataType, name: str = 'Preloaded', verbose: bool = True) -> None:
        """Initializes a preloaded dataset, storing the given data and setting attributes.

        Args:
            x_train (pd.DataFrame): Dataframe containing training samples.
            y_train (pd.Series): Series containing training labels.
            x_test (pd.DataFrame): Dataframe containing testing samples.
            y_test (pd.Series): Series containing testing labels.
            data_type (DataType): Type of labelled data (either classification or regression).
            name (str, optional): Name of the dataset. Defaults to 'Preloaded'.
            verbose (bool, optional): Whether status messages should be printed or not. Defaults to True.
        """

        super().__init__(name=name, data_type=data_type)

        if verbose:
            print('Creating dataset from preloaded data ...', end=' ')

        # store training and testing data
        self._x_train = x_train
        self._x_test = x_test
        self._y_train = y_train
        self._y_test = y_test

        # determine dataset sizes
        self.n = len(self._y_train) + len(self._y_test)
        self.test_size = len(self._y_test) / self.n
        if data_type == DataType.CLASSIFICATION:
            # using train data as model cannot predict classes it is not trained on, check that no additional classes are in test data
            self.n_classes = y_train.nunique()
            if set(y_test.unique().flatten()).difference(set(y_train.unique().flatten())):
                raise ValueError('There are classes present in the test set that are not present in the train set.')

        if verbose:
            print('done.')

    def get_train(self) -> tuple[pd.DataFrame, pd.Series]:

        return self._x_train, self._y_train

    def get_test(self) -> tuple[pd.DataFrame, pd.Series]:

        return self._x_test, self._y_test
