"""
TG43 class
Main author: Charles Joachim
Contributor: Marie-Anne Lebel-Cormier
"""
import os
import warnings
from collections.abc import Sequence
from enum import Enum
from typing import Union

import numpy as np
from scipy.interpolate import RegularGridInterpolator

try:
    import xarray as xr
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "tg43 module requires the xarray optional dependency. Install with: "
        "`pip install pygrpm[xarray]` or `pip install pygrpm[all]`"
    ) from exc


class SourceDataNotFound(Exception):
    """
    Implementation for possible future handling of missing source data
    """

    # pylint: disable=unnecessary-pass
    pass


class InvalidSourceException(Exception):
    """
    Implementation for possible mishandling of the source
    """

    # pylint: disable=unnecessary-pass
    pass


class SourceType(Enum):
    Unknown = 0
    Point = 1
    Line = 2


def _coords3d(value: Union[Sequence, float]) -> np.ndarray:
    """
    Converts a scalar value into a 3D numpy array with each entry the value of the scalar
    """
    if np.isscalar(value):
        return np.array((value,) * 3)

    return np.array(value)


# pylint: disable=C0103
# x, y, z are valid names in this context
def _get_sphere_coords(
        x: float, y: float, z: float, orientation: Sequence = (0, 0, 1)
) -> tuple:
    """
    Converts cartesian coordinates to spherical
    """
    r = np.sqrt(x ** 2 + y ** 2 + z ** 2)
    m = x * orientation[0] + y * orientation[1] + z * orientation[2]
    theta = np.degrees(np.arccos(m / r))

    # pylint: disable=E1101
    # pylint confuses parent class here
    if isinstance(theta, xr.core.dataarray.DataArray):
        theta = theta.fillna(0)  # nan where r == 0, replaced with 0
    else:
        theta = np.nan_to_num(theta)
    return r, theta


def domain(fn):
    """
    Decorator for simulation domain
    """

    def wrapper(*args, dom=None):
        a = fn(*args)
        if dom is None:
            return a

        return a.sel(r=slice(dom[0], dom[1]))

    return wrapper


class Seed:
    """
    Class defining the TG43 simulation based on the selected brachy seed
    """

    def __init__(self, dirname: str, source_type: SourceType = SourceType.Line,
                 use_xarray=True) -> None:
        """
        Construct a TG43 source object.

        The two top level functions are `line` and `point` that implement the
        line-formalism and point-formalism TG43.

        Some sources are already defined in the sources.py file. A new source
        can be initialized with the datafile, the source length and the dose
        rate constant.

        `dirname`: the datafile directory name
        'source_type': the type of source needed for calculation
        """
        # find the absolute path of the data directory
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", dirname)
        if not os.path.isdir(path):
            raise SourceDataNotFound(path)

        self._use_xarray = use_xarray

        # source type
        self._source_type = source_type

        # The length of the source
        self.L = np.loadtxt(os.path.join(path, "L.dat"))

        # The dose rate constant of the source
        self.Lambda = np.loadtxt(os.path.join(path, "Lambda.dat"))

        # The function gL
        gL = np.loadtxt(os.path.join(path, "gL.dat")).T

        if self._use_xarray:
            self.gL = xr.DataArray(gL[1], dims=["r"], coords=[gL[0]])
        else:
            self.gL = gL

        # The function F
        F = np.loadtxt(os.path.join(path, "F.dat"))
        if self._use_xarray:
            self.F = xr.DataArray(
                F[1:, 1:].T, dims=["r", "theta"], coords=[F[0, 1:], F[1:, 0]]
            )
        else:
            # for now, points far from the source will have a dose rate of 0 (fill_value = 0)
            self.F = RegularGridInterpolator(
                points=(F[0, 1:], F[1:, 0]), values=F[1:, 1:].T, bounds_error=False, fill_value=0.0
            )

        # the function phi
        if os.path.isfile(os.path.join(path, "phi.dat")):
            phi = np.loadtxt(os.path.join(path, "phi.dat")).T
            if self._use_xarray:
                self.phi = xr.DataArray(phi[1], dims=["r"], coords=[phi[0]])
            else:
                self.phi = phi
        else:
            if self._use_xarray:
                self.phi = self.F.mean(dim="theta")
            else:
                if self._source_type == SourceType.Point:
                    raise SourceDataNotFound('Missing phi.dat')

        # half life
        self._half_life = np.loadtxt(os.path.join(path, "HalfLife.dat"))

        self._GL0 = self._beta(1, np.radians(90)) / self.L
        self.decimals_r = 1

    @property
    def half_life(self):
        return self._half_life

    def _beta(self, r, theta):
        """
        Implementation of the beta function used in the geometric function (GL).
        """
        L = self.L
        L24 = (L ** 2) / 4
        theta1 = np.pi - theta
        beta = np.arcsin(
            (L / 2) * np.sin(theta) / np.sqrt(r ** 2 + L24 - r * L * np.cos(theta))
        ) + np.arcsin(
            (L / 2) * np.sin(theta1) / np.sqrt(r ** 2 + L24 - r * L * np.cos(theta1))
        )
        return beta

    def _GL(self, r, theta):
        rad_theta = np.radians(theta)
        GL_array = self._beta(r, rad_theta) / (self.L * r * np.sin(rad_theta))

        if self._use_xarray:
            GL_array = GL_array.where(theta != 0, 1 / (r ** 2 - (self.L ** 2) / 4))
            GL_array = GL_array.where(theta != 180, 1 / (r ** 2 - (self.L ** 2) / 4))
            GL_array = GL_array.where(r != 0, np.nan)
        else:
            where_r_0 = np.where(r == 0)[0]
            if len(where_r_0) != 0:
                GL_array[where_r_0] = 0.0

            where_theta_0 = np.where(theta == 0)[0]
            if len(where_theta_0) != 0:
                GL_array[where_theta_0] = 1 / (r[where_theta_0] ** 2 - (self.L ** 2) / 4)

            where_theta_180 = np.where(theta == 180)[0]
            if len(where_theta_180) != 0:
                GL_array[where_theta_180] = 1 / (r[where_theta_180] ** 2 - (self.L ** 2) / 4)

        return GL_array

    def _dose(self, r, theta=None):
        """
        Internal method to perform dose calculation at the given point
        """
        if theta is not None:
            # Line source
            if self._source_type != SourceType.Line:
                raise InvalidSourceException(
                    f"Request line source calculation with type {self._source_type}"
                )

            if self._use_xarray:
                ret_dose = (
                        self.Lambda
                        * (self._GL(r, theta) / self._GL0)
                        * self.gL.interp(r=r)
                        * self.F.interp(r=r, theta=theta)
                )
            else:
                points = np.zeros((len(r), 2))
                points[:, 0] = r
                points[:, 1] = theta
                ret_dose = (
                        self.Lambda
                        * (self._GL(r, theta) / self._GL0)
                        * np.interp(r, self.gL[0], self.gL[1])
                        * self.F(points)
                )
        else:
            # Point source
            if self._source_type != SourceType.Point:
                raise InvalidSourceException(
                    f"Request point source calculation with type {self._source_type}"
                )

            if self._use_xarray:
                ret_dose = (
                        self.Lambda *
                        self._GL(r, 90) / self._GL0 *
                        self.gL.interp(r=r) *
                        self.phi.interp(r=r)
                )
            else:
                theta = np.full(r.shape, 90)
                ret_dose = (
                        self.Lambda
                        * self._GL(r, theta) / self._GL0
                        * np.interp(r, self.gL[0], self.gL[1])
                        * np.interp(r, self.phi[0], self.phi[1])
                )

        return ret_dose

    def dose(
            self, r: Union[Sequence, float], theta: Union[Sequence, float] = None
    ) -> xr.DataArray:
        """
        Returns the dose for each given point. If multiple points of r and theta are
        provided all cross values wil be returned.

        :param Union[Sequence, float] r: A sequence or scalar of radius values
        :param Union[Sequence, float] theta: A sequence or scalar of angle values

        :return DataArray: A DataArray of doses for each provided points
        """
        r_arr = np.array(r, ndmin=1)
        if self._use_xarray:
            r_arr = xr.DataArray(r_arr, dims=["r"], coords=[r_arr])

        if theta is not None:
            theta_arr = np.array(theta, ndmin=1)
            if self._use_xarray:
                theta_arr = xr.DataArray(theta_arr, dims=["theta"], coords=[theta_arr])
        else:
            theta_arr = None

        return self._dose(r_arr, theta_arr)

    # pylint: disable=R0913
    # pylint: disable=too-many-positional-arguments
    # Can't really bypass this many arguments
    def grid(
            self,
            boxmin: Union[Sequence, float] = -10,
            boxmax: Union[Sequence, float] = 10,
            voxsize=0.1,
            sourcepos: Union[Sequence, float] = 0,
            orientation: Sequence = (0, 0, 1),
    ) -> xr.DataArray:
        """
        Method to compute a 3D dosimetric grid for this brachy seed

        :param Union[Sequence, float] boxmin: Minimum coordinate value (along all axes)
        of the container box
        :param Union[Sequence, float] boxmax: Maximum coordinate value (along all axes)
        of the container box
        :param float voxsize: Voxel size of the container box
        :param Union[Sequence, float] sourcepos: Position of the source within the container box
        :param Sequence orientation: Sequence of float detailing source orientation in the box

        :return DataArray: A dataArray with the 3D dosimetric grid information
        """
        boxmin = _coords3d(boxmin)
        boxmax = _coords3d(boxmax)
        voxsize = _coords3d(voxsize)
        sourcepos = _coords3d(sourcepos)
        orientation = _coords3d(orientation)

        # np.arange accumulates the floating point error. Here, the error is
        # kept as small as possible.
        x = (
                boxmin[0]
                - sourcepos[0]
                + np.arange(0, boxmax[0] - boxmin[0] + voxsize[0], voxsize[0])
        )
        y = (
                boxmin[1]
                - sourcepos[1]
                + np.arange(0, boxmax[1] - boxmin[1] + voxsize[1], voxsize[1])
        )
        z = (
                boxmin[2]
                - sourcepos[2]
                + np.arange(0, boxmax[2] - boxmin[2] + voxsize[2], voxsize[2])
        )

        x = xr.DataArray(x, dims=["x"], coords=[x])
        y = xr.DataArray(y, dims=["y"], coords=[y])
        z = xr.DataArray(z, dims=["z"], coords=[z])

        r, theta = _get_sphere_coords(x, y, z, orientation)
        grid = self._dose(r, theta)
        grid = grid.drop_vars(["r", "theta"])
        grid = grid.assign_coords(
            x=(grid.x + sourcepos[0]),
            y=(grid.y + sourcepos[1]),
            z=(grid.z + sourcepos[2]),
        )

        return grid

    def dose_at_points(
            self,
            points: Sequence,
            sourcepos: Sequence,
            orientation: Union[Sequence, None] = None):

        points = _coords3d(points)
        sourcepos = _coords3d(sourcepos)
        if orientation is not None:
            orientation = _coords3d(orientation)

        x = points[:, 0] - sourcepos[0]
        y = points[:, 1] - sourcepos[1]
        z = points[:, 2] - sourcepos[2]

        if orientation is not None:
            r, theta = _get_sphere_coords(x, y, z, orientation)
        else:
            r = np.sqrt(x ** 2 + y ** 2 + z ** 2)
            theta = None

        return self.dose(r, theta)

    @domain
    def get_mean(self, array: xr.DataArray) -> xr.DataArray:
        """
        For a given dosimetric grid, obtain an array of mean values along the radius
        :param DataArray array: DataArray representing the dosimetric grid, such as that
        obtained from Seed.grid()
        :return DataArray: Mean dose value for values of radius
        """
        array90 = array.interp(z=0)
        r, _ = _get_sphere_coords(array90.x, array90.y, array90.z)
        array90["r"] = r.round(decimals=self.decimals_r)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            a = array90.groupby("r").mean()
        return a

    @domain
    def get_std(self, array: xr.DataArray) -> xr.DataArray:
        """
        For a given dosimetric grid, obtain an array of standard deviation values along the radius
        :param DataArray array: DataArray representing the dosimetric grid, such as that
        obtained from Seed.grid()
        :return DataArray: Standard deviation of dose value for values of radius
        """
        array90 = array.interp(z=0)
        r, _ = _get_sphere_coords(array90.x, array90.y, array90.z)
        array90["r"] = r.round(decimals=self.decimals_r)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            a = array90.groupby("r").std()
        return a

    @domain
    def get_cv(self, array: xr.DataArray) -> xr.DataArray:
        """
        For a given dosimetric grid, obtain an array of coefficients of variation
        values along the radius
        :param DataArray array: DataArray representing the dosimetric grid, such as that
        obtained from Seed.grid()
        :return DataArray: Standard deviation of dose value for values of radius
        """
        array90 = array.interp(z=0)
        r, _ = _get_sphere_coords(array90.x, array90.y, array90.z)
        array90["r"] = r.round(decimals=self.decimals_r)
        array90_groupby_r = array90.groupby("r")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            mean = array90_groupby_r.mean()
            std = array90_groupby_r.std()
        return std / abs(mean)

    @domain
    def get_gL(self, array: xr.DataArray) -> xr.DataArray:
        """
        For a given dosimetric grid, obtain an array of Geometry function (for line source)
        values along the radius
        :param DataArray array: DataArray representing the dosimetric grid, such as that
        obtained from Seed.grid()
        :return DataArray: Standard deviation of dose value for values of radius
        """
        array90 = array.interp(z=0)
        r, theta = _get_sphere_coords(array90.x, array90.y, array90.z)
        array90 *= self._GL0 / self._GL(r, theta)
        array90["r"] = r.round(decimals=self.decimals_r)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            a = array90.groupby("r").mean()
        return a / a.sel(r=1)

    @domain
    def get_F(self, array: xr.DataArray, R: float) -> xr.DataArray:
        """
        Obtain the Anisotropic function in terms of angles for a given radius R.
        Values are normalized by F(r, theta=90)
        :param DataArray array: DataArray representing the dosimetric grid, such as that
        obtained from Seed.grid()
        :param float R: Radius value for the anisotropic function
        :return DataArray: Anisotropic function in terms of theta (0 to 180)
        """
        r, theta = _get_sphere_coords(array.x, array.y, array.z)
        new_arr = array * self._GL0 / self._GL(r, theta)
        s = np.linspace(-R, R, 101)
        new_arr = new_arr.interp(x=s, y=s, z=s)
        r, theta = _get_sphere_coords(new_arr.x, new_arr.y, new_arr.z)
        new_arr["r"] = r.round(decimals=self.decimals_r)
        new_arr["theta"] = theta.round()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            a = new_arr.where(new_arr.r == R).groupby("theta").mean()
        return a / a.sel(theta=90)

    def get_calibration(
            self, array: xr.DataArray, significant_figures: int = 5
    ) -> float:
        """
        Returns the calibration factor based on internal or provided Lambda values.
        Function returns Lambda divided by the mean value of array at r=1 to the specified
        amount of significant figures
        :param DataArray array: DataArray representing the dosimetric grid, such as that
        obtained from Seed.grid()
        :param float significant_figures: Desired significant figures for returned value
        :return float: The calibration factor to apply to the provided grid
        """
        array90 = array.interp(z=0)
        r, _ = _get_sphere_coords(array90.x, array90.y, array90.z)
        array90["r"] = r.round(decimals=3)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            a = array90.groupby("r").mean()
        print(a.sel(r=1).values)
        C = self.Lambda / a.sel(r=1).values
        C = np.around(C, decimals=significant_figures - int(np.log10(C)))
        return C
