"""
dose_calculation_service.py

This module defines a service class for computing dose distributions and
Dose-Volume Histograms (DVH) using TG43 formalism for brachytherapy.

It includes input validation for control parameters, physical dose computations
from source positions, and 3D dose distribution over anatomical structures.
"""
from typing import List, Tuple, Union

import numpy as np

from pygrpm.brachy_dvh.dicom.brachy_rt_plan_wrapper import BrachyTreatmentType
from pygrpm.brachy_dvh.dose_parameters import DoseControlParameters
from pygrpm.brachy_dvh.dvh import DVH
from pygrpm.brachy_dvh.source_position import SourcePosition
from pygrpm.brachy_dvh.structure import Structure
from pygrpm.tg43.seed import Seed, SourceType


class DoseCalculationServiceError(Exception):
    """Exception raised for errors in the dose calculation process."""
    pass


class DoseCalculationService:
    """
    Service class for TG43-based dose and DVH calculations in brachytherapy.

    This class uses source positions, control parameters, and source strengths
    to compute point-wise dose, DVH, and 3D dose grids.
    """
    _MIN_NUMBER_OF_POINTS_DVH = 1000
    _MAX_NUMBER_OF_POINTS_DVH = 200000
    _MIN_VOXEL_SIZE = 0.5  # in mm
    _MAX_VOXEL_SIZE = 3.0  # in mm
    _MIN_SLICE_RESOLUTION = 0.5  # mm
    _MAX_SLICE_RESOLUTION = 2.0  # mm

    def __init__(
            self,
            control_parameters: DoseControlParameters,
            source_positions: List[SourcePosition],
            air_kerma_strength: float
    ):
        """Initialize dose calculation parameter"""
        self.__validate_inputs(control_parameters, source_positions, air_kerma_strength)

        self._control_parameters = control_parameters
        self._source_positions = source_positions
        self._air_kerma_strength = air_kerma_strength
        self._tg43_dose_engine = Seed(
            self._control_parameters.source_name,
            source_type=self._control_parameters.source_type,
            use_xarray=False
        )

    @staticmethod
    def __check_range(
            value: Union[int, float],
            min_value: Union[int, float],
            max_value: Union[int, float],
            variable: str
    ):
        """Check if a variable is whitin a given range"""
        if value < min_value or value > max_value:
            raise DoseCalculationServiceError(
                f"{variable} = {value} is out of bounds with allowed range: [{min_value}, {max_value}]")

    @staticmethod
    def __validate_dose_control_parameters(control_parameters: DoseControlParameters):
        """Validates the dose control parameters"""
        if control_parameters.brachy_treatment_type != BrachyTreatmentType.LDR and \
                control_parameters.brachy_treatment_type != BrachyTreatmentType.HDR:
            raise DoseCalculationServiceError("Brachy type should be LDR or HDR")

        if control_parameters.dvh_control_parameters is not None:
            number_of_points = control_parameters.dvh_control_parameters.number_of_points
            DoseCalculationService.__check_range(
                number_of_points,
                DoseCalculationService._MIN_NUMBER_OF_POINTS_DVH,
                DoseCalculationService._MAX_NUMBER_OF_POINTS_DVH,
                "Number of points"
            )

            if control_parameters.dvh_control_parameters.slice_resolution is not None:
                DoseCalculationService.__check_range(
                    control_parameters.dvh_control_parameters.slice_resolution,
                    DoseCalculationService._MIN_SLICE_RESOLUTION,
                    DoseCalculationService._MAX_SLICE_RESOLUTION,
                    "Slice resolution"
                )

        if control_parameters.dose_3d_control_parameters is not None:
            if control_parameters.dose_3d_control_parameters.max_dose < 0.0:
                raise DoseCalculationServiceError("Max dose is negative for dose 3d calculation")

            DoseCalculationService.__check_range(
                control_parameters.dose_3d_control_parameters.voxel_size_x,
                DoseCalculationService._MIN_VOXEL_SIZE,
                DoseCalculationService._MAX_VOXEL_SIZE,
                "Voxel size x"
            )

            DoseCalculationService.__check_range(
                control_parameters.dose_3d_control_parameters.voxel_size_y,
                DoseCalculationService._MIN_VOXEL_SIZE,
                DoseCalculationService._MAX_VOXEL_SIZE,
                "Voxel size y"
            )

            DoseCalculationService.__check_range(
                control_parameters.dose_3d_control_parameters.voxel_size_z,
                DoseCalculationService._MIN_VOXEL_SIZE,
                DoseCalculationService._MAX_VOXEL_SIZE,
                "Voxel size z"
            )

    @staticmethod
    def __validate_inputs(
            control_parameters: DoseControlParameters,
            source_positions: List[SourcePosition],
            air_kerma_strength: float
    ):
        """Validates the input parameter for dose calculation"""
        DoseCalculationService.__validate_dose_control_parameters(control_parameters)

        if len(source_positions) == 0:
            raise DoseCalculationServiceError("No source positions provided")

        if air_kerma_strength < 0.0:
            raise DoseCalculationServiceError("Air kerma strength is negative")

        if control_parameters.source_type == SourceType.Line:
            for source_position in source_positions:
                if source_position.direction is None:
                    raise DoseCalculationServiceError(
                        "Source orientations should be provided for 2D (line) calculation")

    def calculate_dose(self, dose_points: np.array) -> np.array:
        """Calculate the dose with a given dose points sets"""
        cumulative_doses = np.zeros(dose_points.shape[0])
        for source_position in self._source_positions:
            doses = self._tg43_dose_engine.dose_at_points(
                dose_points,
                source_position.position,
                source_position.direction
            )

            if self._control_parameters.brachy_treatment_type == BrachyTreatmentType.HDR:
                doses *= source_position.weight
                doses /= 360000.0  # to have Gy
                doses *= self._air_kerma_strength

            if self._control_parameters.brachy_treatment_type == BrachyTreatmentType.LDR:
                # assumes the same weight (activity) for each seed
                half_life_in_hours = (self._tg43_dose_engine.half_life * 24)
                decay_constant = np.log(2) / half_life_in_hours
                doses /= (100 * decay_constant)  # cGy -> Gy
                doses *= self._air_kerma_strength

            cumulative_doses += doses
        return cumulative_doses

    def calculate_dvh(self, structure: Structure) -> DVH:
        """
        Calculates the Dose-Volume Histogram (DVH) for a given structure.
        """
        if self._control_parameters.dvh_control_parameters is None:
            raise DoseCalculationServiceError("Control parameters for DVH calculation not set")

        number_of_points = self._control_parameters.dvh_control_parameters.number_of_points
        if self._control_parameters.dvh_control_parameters.slice_resolution is not None:
            interpolated_structure = structure.get_interpolated_structure(
                grid_spacing_xy=1.0,
                slice_resolution=self._control_parameters.dvh_control_parameters.slice_resolution
            )
            dose_points = interpolated_structure.sample_random_points(number_of_points)
        else:
            dose_points = structure.sample_random_points(number_of_points)

        dose_points /= 10.0  # mm -> cm
        volume = structure.volume / 1000  # mm3 -> cm3
        voxel_volume = volume / number_of_points

        dose_at_points = self.calculate_dose(dose_points)

        dvh = DVH(
            self._control_parameters.dvh_control_parameters.number_of_bins,
            self._control_parameters.dvh_control_parameters.max_dose
        )
        dvh.calculate(dose_at_points, voxel_volume)

        return dvh

    def calculate_3d_dose_distribution(
            self,
            structures: List[Structure]
    ) -> Tuple[np.ndarray, Tuple[float, float, float]]:
        """
        Computes the 3D dose distribution over the union of a list of structures.
        voxel_size_x, y, and z shall be in mm.
        """
        if self._control_parameters.dose_3d_control_parameters is None:
            raise DoseCalculationServiceError("Control parameters for dose 3d calculation not set")
        extent_of_3d_dose = Structure.find_extent_of_structures(structures, margin=10)
        voxel_size_x = self._control_parameters.dose_3d_control_parameters.voxel_size_x
        voxel_size_y = self._control_parameters.dose_3d_control_parameters.voxel_size_y
        voxel_size_z = self._control_parameters.dose_3d_control_parameters.voxel_size_z
        x = np.arange(extent_of_3d_dose.x_min, extent_of_3d_dose.x_max,
                      voxel_size_x) / 10  # mm -> cm
        y = np.arange(extent_of_3d_dose.y_min, extent_of_3d_dose.y_max,
                      voxel_size_y) / 10  # mm -> cm
        z = np.arange(extent_of_3d_dose.z_min, extent_of_3d_dose.z_max,
                      voxel_size_z) / 10  # mm -> cm
        n_x = len(x)
        n_y = len(y)
        n_z = len(z)
        x, y, z = np.meshgrid(x, y, z)
        x, y, z = x.flatten(), y.flatten(), z.flatten()
        dose_points = np.vstack((y, x, z)).T
        dose_values = self.calculate_dose(dose_points)
        dose_values = dose_values.reshape((n_y, n_x, n_z))
        return dose_values, (extent_of_3d_dose.x_min, extent_of_3d_dose.y_min,
                             extent_of_3d_dose.z_min)
