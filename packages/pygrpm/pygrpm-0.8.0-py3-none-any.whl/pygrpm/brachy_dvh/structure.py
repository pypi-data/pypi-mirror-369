"""Module defining the Structure class used for 3D DVH structure generation and manipulation."""

from __future__ import annotations

import copy
import warnings
from typing import Dict, List, Sequence, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.path import Path
from scipy.interpolate import RegularGridInterpolator
from scipy.ndimage import binary_dilation, binary_erosion, distance_transform_edt
from skimage import measure

from pygrpm.brachy_dvh.contour import Contour, InvalidDataError
from pygrpm.brachy_dvh.utils import Extent, Grid3d, is_uniform_interval, resample_array


# pylint: disable=too-many-instance-attributes,too-many-public-methods,too-many-arguments,too-many-locals
class Structure:
    """Represents a 3D anatomical structure built from contour data."""

    def __init__(self, contours: list[Contour], roi_name: str = "", roi_number: int = -1):
        self.__validate_number_of_contours(contours)
        self._contours = self.__convert_contours_list_to_dict(contours)
        self._roi_name = roi_name
        self._roi_number = roi_number
        self._extent = None
        self._mask = None
        self._signed_distance_map = None
        self._z_slices = None
        self._on_scroll_ind = None
        self._mesh = None
        self._has_missing_slices = False
        self._volume = -1.0
        self.__calculate_extent()

    @staticmethod
    def __validate_number_of_contours(contours: List[Contour]):
        """Validates that the contour list has at least two elements."""
        if len(contours) < 2:
            raise InvalidDataError("At least 2 contours are required")

    @staticmethod
    def __convert_contours_list_to_dict(contours: list[Contour]) -> Dict[float, List[Path]]:
        """Converts a list of Contour objects to a dictionary by z-coordinate."""
        dict_contours = {}
        for contour in contours:
            points = np.round(contour.points, 2)
            z = points[0, 2]
            if not z in dict_contours:
                dict_contours[z] = []
            dict_contours[z].append(Path(points[:, :2]))
        return dict_contours

    @staticmethod
    def find_extent_of_structures(structures: List[Structure], margin: float = 0.0) -> Extent:
        """Finds the bounding extent of a list of structures, with optional margin."""
        large_number = 1e9
        x_min, y_min, z_min = large_number, large_number, large_number
        x_max, y_max, z_max = -large_number, -large_number, -large_number
        for structure in structures:
            extent = structure.extent

            x_min = min(x_min, extent.x_min)

            y_min = min(y_min, extent.y_min)

            z_min = min(z_min, extent.z_min)

            x_max = max(x_max, extent.x_max)

            y_max = max(y_max, extent.y_max)

            z_max = max(z_max, extent.z_max)

        x_min -= margin
        x_max += margin
        y_min -= margin
        y_max += margin
        z_min -= margin
        z_max += margin

        return Extent(x_min, x_max, y_min, y_max, z_min, z_max)

    @property
    def contours(self) -> Dict[float, List[Path]]:
        """Returns the dictionary of contours by slice."""
        return self._contours

    @property
    def extent(self) -> Extent:
        """Returns the bounding box extent of the structure."""
        return self._extent

    @property
    def roi_name(self) -> str:
        """Returns the ROI name."""
        return self._roi_name

    @property
    def roi_number(self) -> int:
        """Returns the ROI number."""
        return self._roi_number

    @property
    def z_slices(self) -> List[float]:
        """Returns the list of z-slice values."""
        return self._z_slices

    @property
    def mask(self) -> Grid3d:
        """Returns the binary mask representing the structure."""
        return self._mask

    @property
    def mesh(self) -> trimesh.Trimesh:
        """Returns the mesh representation of the structure."""
        return self._mesh

    @property
    def volume(self) -> float:
        """Returns the volume of the structure."""
        # estimate the volume if requested
        if self._volume < 0.0:
            self.sample_random_points(20000)
        return self._volume

    @property
    def signed_distance_map(self) -> Grid3d:
        """Returns the signed distance map."""
        return self._signed_distance_map

    def get_points_cloud(self) -> np.ndarray[..., 3]:
        """Returns a 3D point cloud from the contours."""
        list_contours = []
        for z, contours in self.contours.items():
            for contour in contours:
                vertices = contour.vertices
                contour_3d = np.zeros((vertices.shape[0], 3))
                contour_3d[:, :2] = vertices
                contour_3d[:, 2] = z
                list_contours.append(contour_3d)

        concatenated_array = list_contours[0]
        for contour in list_contours[1:]:
            concatenated_array = np.concatenate((concatenated_array, contour), axis=0)
        return concatenated_array

    def __calculate_extent(self):
        """Calculates and stores the extent and z-slices of the structure."""
        all_points = self.get_points_cloud()
        self._extent = Extent(
            np.min(all_points[:, 0]),
            np.max(all_points[:, 0]),
            np.min(all_points[:, 1]),
            np.max(all_points[:, 1]),
            np.min(all_points[:, 2]),
            np.max(all_points[:, 2]),
        )
        self._z_slices = list(sorted(self.contours.keys()))
        if not is_uniform_interval(self._z_slices):
            self._has_missing_slices = True
            warnings.warn("Slice thickness is non uniform, "
                          "inter-slice interpolation should be "
                          "performed for accurate DVH calculations",
                          UserWarning)

    def get_contours_at_z(self, z: float) -> list[Path]:
        """Returns the list of contours at a specific z-slice."""
        contours_at_z = self.contours.get(z, None)
        if contours_at_z is None:
            raise InvalidDataError(f"No contours found at z = {z}")
        return contours_at_z

    def get_contours_closest_to_z(self, z: float) -> Tuple[float, List[Path]]:
        """Finds the slice closest to the provided z and returns its contours."""
        if z < self.z_slices[0] or z > self.z_slices[-1]:
            return np.nan, []
        index_z = np.argmin(abs(z - np.array(self.z_slices)))
        return self.z_slices[index_z], self.get_contours_at_z(self.z_slices[index_z])

    def is_point_inside(self, point: np.array) -> bool:
        """Checks if a given 3D point is inside the structure."""
        if point.shape[0] != 3:
            raise InvalidDataError("Number of coordinates must be 3 (x, y, z)")
        outside_x = point[0] < self.extent.x_min or point[0] > self.extent.x_max
        outside_y = point[1] < self.extent.y_min or point[1] > self.extent.y_max
        outside_z = point[2] < self.extent.z_min or point[2] > self.extent.z_max

        if outside_x or outside_y or outside_z:
            return False

        _, contours = self.get_contours_closest_to_z(point[2])
        c = False
        for contour in contours:
            is_inside = contour.contains_point(point[:2])
            if is_inside:
                c = not c

        return c

    def sample_random_points(self, number_of_points) -> np.ndarray:
        """Samples random points within the volume of the structure."""
        n_points_inside = 0
        n_points_thrown = 0
        x_box = self.extent.x_max - self.extent.x_min
        y_box = self.extent.y_max - self.extent.y_min
        z_box = self.extent.z_max - self.extent.z_min
        sampled_points = []
        while n_points_inside < number_of_points:
            x = self.extent.x_min + np.random.random() * x_box
            y = self.extent.y_min + np.random.random() * y_box
            z = self.extent.z_min + np.random.random() * z_box
            point = np.array([x, y, z])
            if self.is_point_inside(point):
                sampled_points.append(point)
                n_points_inside += 1
            n_points_thrown += 1

        self._volume = x_box * y_box * z_box * n_points_inside / n_points_thrown
        return np.array(sampled_points)

    def create_mask(
            self,
            x_min: float,
            x_max: float,
            n_x: int,
            y_min: float,
            y_max: float,
            n_y: int,
            z_coordinates: Union[None, Sequence[float]] = None
    ):
        """Creates a binary mask of the structure with given XY grid parameters."""
        if z_coordinates is not None:
            local_z_coordinates = np.array(z_coordinates)
        else:
            local_z_coordinates = np.array(self.z_slices)

        self._mask = Grid3d(x_min, x_max, n_x, y_min, y_max, n_y, local_z_coordinates, bool)
        grid_points_2d = self._mask.get_xy_coordinates()
        for _, z in enumerate(local_z_coordinates):
            if z_coordinates is None:
                contours_at_z = self.get_contours_at_z(z)
            else:
                contours_at_z = self.get_contours_closest_to_z(z)[1]

            mask_at_z = np.zeros(grid_points_2d.shape[0], dtype=np.int64)
            for contour in contours_at_z:
                mask_at_z += contour.contains_points(grid_points_2d).astype(np.int64)

            # handles islands of contours or contours within contours
            if len(np.where(mask_at_z > 2)[0]):
                raise InvalidDataError("Too much contour overlap can lead to undefined behavior")
            mask_at_z[np.where(mask_at_z >= 2)[0]] = 0
            mask_at_z = mask_at_z.astype(bool)
            self._mask.set_values_at_z(z, mask_at_z.reshape(n_y, n_x))

    def create_mask_from_extent(self, grid_spacing_x: float, grid_spacing_y: float,
                                margin: float = 0.0):
        """Creates a mask based on the structure's extent and given grid spacing."""
        x_min = self.extent.x_min - margin
        x_max = self.extent.x_max + margin
        y_min = self.extent.y_min - margin
        y_max = self.extent.y_max + margin
        grid_size_x = x_max - x_min
        grid_size_y = y_max - y_min
        n_x = int(np.ceil(grid_size_x / grid_spacing_x))
        n_y = int(np.ceil(grid_size_y / grid_spacing_y))

        self.create_mask(
            x_min,
            x_max,
            n_x,
            y_min,
            y_max,
            n_y,
        )

    def get_eroded_mask(self, iterations: int = 1, axes: tuple[int, ...] = None):
        """Returns an eroded version of the structure's binary mask."""
        return binary_erosion(self.mask.grid, iterations=iterations, axes=axes)

    def get_dilated_mask(self, iterations: int = 1, axes: tuple[int, ...] = None):
        """Returns a dilated version of the structure's binary mask."""
        return binary_dilation(self.mask.grid, iterations=iterations, axes=axes)

    def create_signed_distance_map(self, grid_spacing_xy: float = 1):
        """Creates a signed distance map from the binary mask."""
        if self.mask is None:
            self.create_mask_from_extent(grid_spacing_xy, grid_spacing_xy, margin=10)

        self._signed_distance_map = Grid3d(
            self.mask.x_coordinates[0],
            self.mask.x_coordinates[-1],
            len(self.mask.x_coordinates),
            self.mask.y_coordinates[0],
            self.mask.y_coordinates[-1],
            len(self.mask.y_coordinates),
            self.z_slices,
            np.float64
        )
        outside = distance_transform_edt(~self.mask.grid)
        inside = distance_transform_edt(self.mask.grid)
        signed_distance_map = outside
        signed_distance_map[self.mask.grid] = -inside[self.mask.grid]
        self._signed_distance_map.grid = signed_distance_map * grid_spacing_xy

    def create_mesh(self):
        """Creates a triangular surface mesh from the binary mask using marching cubes."""
        if self.mask is None:
            raise InvalidDataError("Cannot create mesh because mask is None")

        vertices, faces, _, _ = measure.marching_cubes(self.mask.grid, level=0)
        self._mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

    def sample_uniform_points_at_surface(self, number_of_points: int) -> np.ndarray:
        """Samples uniformly distributed points on the surface mesh."""
        if self.mesh is None:
            raise InvalidDataError("Cannot sample points as surface because mesh is None")

        points, _ = trimesh.sample.sample_surface(self.mesh, number_of_points)
        return points

    def show_mesh(self):
        """Displays the structure's mesh using trimesh viewer."""
        if self.mesh is None:
            raise InvalidDataError("Cannot show mesh because mesh is None")

        self.mesh.show()

    def show_mask(self, mask_to_show='binary_mask'):
        """Displays the 2D slice-by-slice mask or signed distance map 
        with interactive scrolling."""

        if mask_to_show == 'binary_mask':
            if self.mask is None:
                raise InvalidDataError("Cannot show mask because mask is None")
            mask = self.mask

        elif mask_to_show == 'signed_distance_map':
            if self.signed_distance_map is None:
                raise InvalidDataError("Cannot show distance map because distance map is None")
            mask = self.signed_distance_map

        else:
            raise InvalidDataError("Cannot show mask, " \
                                   "choose between 'binary_mask' and 'signed_distance_map'")

        self._on_scroll_ind = mask.grid.shape[2] // 2
        fig, ax = plt.subplots()
        ax.set_title(f"z = {mask.z_coordinates[self._on_scroll_ind]} mm")
        ax.imshow(mask.grid[:, :, self._on_scroll_ind],
                  extent=(
                      mask.x_coordinates[0],
                      mask.x_coordinates[-1],
                      mask.y_coordinates[-1],
                      mask.y_coordinates[0])
                  )

        try:
            contours = self.get_contours_at_z(mask.z_coordinates[self._on_scroll_ind])
            for contour in contours:
                contour = contour.vertices
                ax.plot(contour[:, 0], contour[:, 1])
        except InvalidDataError:
            pass

        def onscroll(event, ax=ax):
            ax.clear()
            if event.button == 'up':
                self._on_scroll_ind += 1
            else:
                self._on_scroll_ind -= 1

            self._on_scroll_ind = max(self._on_scroll_ind, 0)

            if self._on_scroll_ind >= mask.grid.shape[2]:
                self._on_scroll_ind = mask.grid.shape[2] - 1

            ax.imshow(mask.grid[:, :, self._on_scroll_ind],
                      extent=(
                          mask.x_coordinates[0],
                          mask.x_coordinates[-1],
                          mask.y_coordinates[-1],
                          mask.y_coordinates[0])
                      )

            try:
                _contours = self.get_contours_at_z(mask.z_coordinates[self._on_scroll_ind])
                for _contour in _contours:
                    _contour = _contour.vertices
                    ax.plot(_contour[:, 0], _contour[:, 1])
            except InvalidDataError:
                pass

            ax.set_title(f"z = {mask.z_coordinates[self._on_scroll_ind]} mm")
            ax.figure.canvas.draw()

        fig.canvas.mpl_connect('scroll_event', onscroll)
        ax.figure.canvas.draw()
        plt.show()

    def get_interpolated_structure(self, grid_spacing_xy: float = 1,
                                   slice_resolution: float = 1) -> Structure:
        """Interpolates a structure on a finer z-resolution using signed distance maps."""
        if self.signed_distance_map is None:
            self.create_signed_distance_map(grid_spacing_xy)
        z_new_slices = resample_array(self.z_slices, slice_resolution)
        x = self.signed_distance_map.x_coordinates
        y = self.signed_distance_map.y_coordinates
        interpolation_function = RegularGridInterpolator(
            (y, x, self.z_slices),
            self.signed_distance_map.grid,
            method='linear'
        )
        x, y, z = np.meshgrid(x, y, 0.0)
        x, y, z = x.flatten(), y.flatten(), z.flatten()
        points = np.vstack((y, x, z)).T
        x_min = self.signed_distance_map.x_coordinates[0]
        x_max = self.signed_distance_map.x_coordinates[-1]
        y_min = self.signed_distance_map.y_coordinates[0]
        y_max = self.signed_distance_map.y_coordinates[-1]
        new_contour_list = []
        for z_new in z_new_slices:
            if np.any(np.isclose(self._z_slices, z_new, atol=1e-4)):
                # copy original contours
                contour_path_list = self.get_contours_at_z(z_new)
                for contour_path in contour_path_list:
                    new_contour = np.zeros((contour_path.vertices.shape[0], 3))
                    new_contour[:, :2] = copy.deepcopy(contour_path.vertices)
                    new_contour[:, 2] = z_new
                    new_contour_list.append(Contour(new_contour))
            else:
                # interpolate contours
                points[:, 2] = z_new
                tmp = interpolation_function(points).reshape(
                    (self.signed_distance_map.grid.shape[0], self.signed_distance_map.grid.shape[1])
                )
                tmp = plt.contour(tmp, levels=[0.0],
                                  extent=[x_min, x_max, y_min, y_max], colors=['r'])

                for segment in tmp.allsegs[0]:
                    if len(segment) > 2:
                        new_contour = np.zeros((segment.shape[0], 3))
                        new_contour[:, :2] = copy.deepcopy(segment)
                        new_contour[:, 2] = z_new
                        new_contour_list.append(Contour(new_contour))

        plt.clf()
        plt.close()
        return Structure(new_contour_list, roi_name=self.roi_name, roi_number=self.roi_number)
