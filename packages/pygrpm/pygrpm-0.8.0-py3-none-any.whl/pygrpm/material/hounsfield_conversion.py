"""
Module used to perform a piecewise fit on a HU -> density datatable
Module also allows for direct conversion tools with the performed fits
"""

import os
import warnings
from pathlib import Path
from typing import Union

import numpy as np
import numpy.typing as npt

try:
    import pandas as pd
    from scipy import optimize
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "This module requires the `pandas` and `scipy` optionals dependencies. Install with: "
        "`pip install pygrpm[pandas,scipy]` or `pip install pygrpm[all]`"
    ) from exc


class FitHUCurve:
    """Simple class for conversion from HU to the provided units through a piecewise curve fit"""

    def __init__(self) -> None:
        self.__fit_params = None
        self.dataframe = None

    # Black magic function courtesy of
    # https://stackoverflow.com/a/29384899/1991715
    @staticmethod
    def _piecewise_linear(x, x0, y0, k1, k2):
        """
        Method representing the piecewise function
        """
        # pylint: disable=C0103
        # Disable snake_case variable name rule for this block
        return np.piecewise(
            x,
            [x < x0],
            [lambda a: k1 * a + y0 - k1 * x0, lambda a: k2 * a + y0 - k2 * x0],
        )
        # pylint: enable=C0103

    @staticmethod
    def _validate_csv(dataframe: pd.DataFrame) -> None:
        """
        Internal method to provide some basic validation to the CSV file
        :param dataframe: Pandas dataframe
        :return: None
        """

        # Ensure we have just 2 columns
        assert dataframe.shape[1] == 2, "More than two columns present in the csv file."

        # Ensure there are no nan
        assert (
            not dataframe.isnull().values.any()
        ), "Provided CSV Should not contain null values."

        # Ensure same length of both columns (sort of redundant due to previous checks)
        assert (
            dataframe.iloc[:, 0].shape == dataframe.iloc[:, 0].shape
        ), "Provided CSV data columns are not of the same length"

    def get_fit_params(self) -> tuple:
        """
        Returns a tuple of fit parameters as returned by scipy's curve_fit()
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html
        :return: Tuple
        """
        return self.__fit_params

    def load_curve_csv(self, filepath: Union[str, bytes, os.PathLike]) -> pd.DataFrame:
        """
        Simple method to load csv, acts as a soft wrapper to pandas read_csv
        :param filepath: String
        :return: DataFrame
        """
        if filepath is None:
            raise ValueError("Did not receive a filepath for the curve")

        curve_file = Path(filepath)

        # Raise an error if the file is missing, technically also if it's a directory
        assert curve_file.is_file(), f"{filepath} could not be opened."

        # Read the actual csv
        curve_dataframe = pd.read_csv(curve_file)

        self._validate_csv(curve_dataframe)
        self.dataframe = curve_dataframe

        return curve_dataframe

    def fit_curve(
        self, curve_dataframe: pd.DataFrame = None, plot: bool = False
    ) -> tuple:
        """
        Method used to apply the curve fit on the provided filepath data
        :param curve_dataframe: Dataframe containing the conversion data
        :param plot: Whether to display a preview plot of the fit
        :return :A tuple of 3 tuples
            x and y data from the loaded data
            parameters and covariance of the fit
            x and y labels from the loaded data
        """
        if curve_dataframe is None:
            curve_dataframe = self.dataframe

        assert (
            curve_dataframe is not None
        ), "No dataframe was provided and none exist in cache"

        # Unpack our data frame into x, y and grab labels
        (data_x, data_y) = (
            curve_dataframe.iloc[:, 0].values,
            curve_dataframe.iloc[:, 1].values,
        )
        (x_label, y_label) = curve_dataframe.columns.values

        # Perform the actual curve fitting
        # pylint: disable=unbalanced-tuple-unpacking
        params, covariances = optimize.curve_fit(self._piecewise_linear, data_x, data_y)
        # pylint: enable=unbalanced-tuple-unpacking
        self.__fit_params = (params, covariances)

        # Small subtask for plotting
        if plot is True:
            fit_x = np.linspace(data_x[0], data_x[-1], data_x.shape[0])
            fit_y = self._piecewise_linear(fit_x, *params)

            self.plot_fit((data_x, data_y), (fit_x, fit_y))

        return (data_x, data_y), (params, covariances), (x_label, y_label)

    @staticmethod
    def plot_fit(plot_data: tuple, fit_data: tuple) -> None:
        """
        Internal method to quickly preview the performed fit
        :param plot_data: A tuple/array containing x and y lists/arrays
        :param fit_data: A tuple/array containing the x and y fit parameters
        :return : None
        """
        try:
            # pylint: disable=C0415
            import matplotlib.pyplot as plt
        except ModuleNotFoundError as exc_:
            raise ModuleNotFoundError(
                "This method requires the `matplotlib` optional dependency. Install with: "
                "`pip install pygrpm[matplotlib]` or `pip install pygrpm[all]`"
            ) from exc_

        data_x, data_y = plot_data
        fit_x, fit_y = fit_data

        plt.plot(data_x, data_y, "o")
        plt.plot(fit_x, fit_y)
        plt.show()


class ConvertHUToDensity(FitHUCurve):
    """
    Utility class wrapping FitHUCurve allowing for a direct conversion
    with provided HU to density table
    """

    def __init__(self):
        super().__init__()

        # Set default HU extrema
        self._hu_min = -1000
        self._hu_max = 4000

    def set_extrema(self, hu_min: int, hu_max: int) -> None:
        """
        Method used to set upper and lower bounds for HU value limits. Values present outside
        the provided (or default) range will be set to its nearest extremum
        :param hu_min: Minimum HU value to treat
        :param hu_max: Maximum HU value to treat
        """
        assert hu_min < hu_max, (
            f"Got maximum hu value {hu_max} greater"
            f"or equal to minimum {hu_min}, this is not valid."
        )
        self._hu_min = hu_min
        self._hu_max = hu_max

    def _handle_extreme_hus(self, data: npt.ArrayLike) -> npt.ArrayLike:
        """
        Helper method to "fold in" HU values that go beyond typical limits
        Values outside the default, or user-set, range will be set to their respective limits
        :param data: numpy array with HU values
        :return : numpy array
        """
        if np.amin(data) < self._hu_min:
            warnings.warn(
                f"Found values under {self._hu_min}, these will all be converted to {self._hu_min}"
            )
            data[data < self._hu_min] = self._hu_min

        if np.amax(data) > self._hu_max:
            warnings.warn(
                f"Found values over {self._hu_max}, these will all be converted to {self._hu_max}"
            )
            data[data > self._hu_max] = self._hu_max

        return data

    def apply_fit(
        self, array: npt.ArrayLike, curve_dataframe: pd.DataFrame, plot: bool = False
    ) -> npt.ArrayLike:
        """
        Method to apply the curve fit to a given set of data
        :param array: Data to be converted in array format
        :param curve_dataframe: Dataframe representing the curve
        :param plot: Whether to display a preview plot of the fit
        :return : numpy array of same shape as input converted to density values
        """
        self.fit_curve(curve_dataframe, plot=plot)
        fit_params = self.get_fit_params()

        array = np.asarray(array, dtype=float)

        # Handle cases where HU values are funny
        array = self._handle_extreme_hus(array)

        return self._piecewise_linear(array, *fit_params[0])
