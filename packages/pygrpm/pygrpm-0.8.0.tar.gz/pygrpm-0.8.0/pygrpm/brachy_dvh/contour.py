"""
Module: contour

This module defines the `Contour` class, representing a 2D contour of points 
lying in a single axial (z-constant) plane. It performs shape and geometric 
validation to ensure the contour meets structural requirements.

Units are assumed to be in millimeters.
"""

import numpy as np

from pygrpm.brachy_dvh.utils import InvalidDataError, Precision


# units shall be in mm
# TODO: add way to handle units
class Contour:
    """
    Represents a single axial-plane contour defined by a sequence of 3D points.
    """

    @staticmethod
    def __validate_shape(points: np.ndarray[..., 3]):
        """
        Validates that the point array has correct shape and minimum number of points.
        """
        if points.shape[1] != 3:
            raise InvalidDataError("Number of coordinates must be 3 (x, y, z)")
        if points.shape[0] < 3:
            raise InvalidDataError("At least 3 points are required to create contour")

    @staticmethod
    def __validate_contour_is_in_axial_plane(points: np.ndarray[..., 3]):
        """
        Validates that all points lie in the same axial plane (constant z-value).
        """
        z_value_ref = points[0, 2]
        for point in points:
            if not np.isclose(z_value_ref, point[2], atol=Precision.F_TOL):
                raise InvalidDataError("Points must be in axial plane")

    @staticmethod
    def __validate_points(points: np.ndarray[..., 3]):
        """
        Runs all validation checks on the point array.
        """
        Contour.__validate_shape(points)
        Contour.__validate_contour_is_in_axial_plane(points)

    def __init__(self, points: np.ndarray[..., 3]):
        """
        Initializes a Contour instance after validating the input points.
        """
        self.__validate_points(points)
        self._points = points

    @property
    def points(self):
        """
        Returns the original array of contour points.
        """
        return self._points
