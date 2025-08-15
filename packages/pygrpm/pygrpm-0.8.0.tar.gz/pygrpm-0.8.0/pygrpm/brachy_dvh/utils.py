"""
grid3d.py - Tools for managing 3D spatial grids and extents for medical or scientific data.

This module defines classes and functions used for:
- Representing 3D spatial extents (`Extent`)
- Building and manipulating uniform 3D grids (`Grid3d`)
- Validating spacing and resampling 1D arrays
- Handling precision issues and input consistency
- Raising custom exceptions for invalid data
"""
import copy
from typing import List, Sequence

import numpy as np


class InvalidDataError(Exception):
    """Custom exception raised when input data is invalid."""
    pass


class Precision:
    """Holds numerical precision thresholds."""
    F_TOL = 1e-6


class Extent:
    """Represents a 3D bounding box using min and max values in x, y, and z directions."""

    @staticmethod
    def __check_input(x_min, x_max, y_min, y_max, z_min, z_max):
        """Validates that all min values are less than or equal to corresponding max values."""
        if x_min > x_max:
            raise InvalidDataError(f"x_min {x_min} is greater than x_max {x_max}")

        if y_min > y_max:
            raise InvalidDataError(f"y_min {y_min} is greater than y_max {y_max}")

        if z_min > z_max:
            raise InvalidDataError(f"z_min {z_min} is greater than z_max {z_max}")

    def __init__(self, x_min, x_max, y_min, y_max, z_min, z_max):
        """Initializes an Extent with given boundaries."""
        Extent.__check_input(x_min, x_max, y_min, y_max, z_min, z_max)
        self._x_min = x_min
        self._x_max = x_max
        self._y_min = y_min
        self._y_max = y_max
        self._z_min = z_min
        self._z_max = z_max

    @property
    def x_min(self):
        """Returns the minimum x-coordinate."""
        return self._x_min

    @property
    def x_max(self):
        """Returns the maximum x-coordinate."""
        return self._x_max

    @property
    def y_min(self):
        """Returns the minimum y-coordinate."""
        return self._y_min

    @property
    def y_max(self):
        """Returns the maximum y-coordinate."""
        return self._y_max

    @property
    def z_min(self):
        """Returns the minimum z-coordinate."""
        return self._z_min

    @property
    def z_max(self):
        """Returns the maximum z-coordinate."""
        return self._z_max


def is_uniform_interval(array: Sequence) -> bool:
    """
    Checks whether the intervals in the array are uniform within a tolerance.
    """
    if len(array) <= 2:
        return True
    interval = array[1] - array[0]
    return all(np.isclose((array[i + 1] - array[i]), interval, Precision.F_TOL)
               for i in range(1, len(array) - 1))


def get_intervals_from_array(array: Sequence) -> List:
    """
    Computes the absolute difference between consecutive elements in a sequence.
    """
    intervals = []
    for i in range(len(array) - 1):
        intervals.append(np.abs(array[i + 1] - array[i]))
    return intervals


def resample_array(array: Sequence, min_resolution):
    """
    Resamples an array into a uniform grid using the minimum interval and desired resolution.
    """
    intervals = get_intervals_from_array(array)
    min_interval = np.min(intervals)
    new_interval = min_interval
    if new_interval % min_resolution == 0:
        new_interval = min_resolution
    else:
        while new_interval > min_resolution:
            new_interval /= 2
    min_val = np.min(array)
    max_val = np.max(array)
    new_array = np.arange(min_val, max_val + 1e-6, new_interval)
    return new_array


class Grid3d:
    """
    Represents a 3D volumetric grid with defined spacing and data type.
    """

    def __init__(
            self,
            x_min: float,
            x_max: float,
            n_x: int,
            y_min: float,
            y_max: float,
            n_y: int,
            z_coordinates: Sequence[float],
            dtype
    ):
        """
        Initializes the 3D grid with given spatial bounds,
        resolution, and value type.
        """
        self._x_coordinates = np.linspace(x_min, x_max, n_x)
        self._y_coordinates = np.linspace(y_min, y_max, n_y)
        self._z_coordinates = np.array(z_coordinates)
        self._grid = np.zeros((n_y, n_x, len(self._z_coordinates)), dtype=dtype)

    @property
    def grid(self) -> np.ndarray:
        """Returns the full 3D grid."""
        return self._grid

    @grid.setter
    def grid(self, grid: np.ndarray):
        """Sets the 3D grid with validation of shape consistency."""
        shape = (len(self.y_coordinates), len(self.x_coordinates), len(self.z_coordinates))
        if shape != grid.shape:
            raise InvalidDataError("Cannot match shape of grid")
        self._grid = copy.deepcopy(grid)

    @property
    def x_coordinates(self) -> np.array:
        """Returns the array of x-axis coordinates."""
        return self._x_coordinates

    @property
    def y_coordinates(self) -> np.array:
        """Returns the array of y-axis coordinates."""
        return self._y_coordinates

    @property
    def z_coordinates(self) -> np.array:
        """Returns the array of z-axis coordinates."""
        return self._z_coordinates

    def get_xy_coordinates(self) -> np.ndarray:
        """
        Computes 2D XY coordinate grid (flattened).
        """
        x, y = np.meshgrid(self._x_coordinates, self._y_coordinates)
        x, y = x.flatten(), y.flatten()
        return np.vstack((x, y)).T

    def set_values_at_z(self, z: float, values: np.ndarray):
        """
        Sets the 2D slice values in the grid at a specific z-coordinate.
        """
        if values.dtype != self._grid.dtype:
            raise InvalidDataError("Values type does not match type of grid")

        is_set = False
        for k, z_coordinate in enumerate(self._z_coordinates):
            if np.isclose(z_coordinate, z, Precision.F_TOL):
                self.grid[:, :, k] = values
                is_set = True
                break

        if not is_set:
            raise InvalidDataError("Cannot set values in grid")
