"""
Module: dose_interface

Provides high-level utility functions for calculating DVH curves and 3D dose distributions
from DICOM RT Plan and RT Structure files
"""

from pathlib import Path

from pygrpm.brachy_dvh.dose_calculation_service_from_dicom import (
    DoseCalculationServiceFromDicom,
)
from pygrpm.brachy_dvh.dose_parameters import (
    Dose3dControlParameters,
    DvhControlParameters,
)


def calculate_dvh(rt_plan_file_path: Path, rt_struct_file_path: Path,
                  dvh_control_parameters: DvhControlParameters, normalize=True):
    """
    Calculates dose-volume histograms (DVHs) for structures defined in the RT Structure file
    given a set of dvh_control_parameters.
    """
    service = DoseCalculationServiceFromDicom(rt_plan_file_path, rt_struct_file_path,
                                              dvh_control_parameters, None)
    return service.calculate_dvhs(normalize_dvhs=normalize)


def compute_dose(rt_plan_file_path: Path, rt_struct_file_path: Path,
                 dose_3d_control_parameters: Dose3dControlParameters):
    """
    Computes the full 3D dose distribution based on the provided DICOM inputs and voxel configuration.
    """
    service = DoseCalculationServiceFromDicom(rt_plan_file_path, rt_struct_file_path, None,
                                              dose_3d_control_parameters)
    return service.calculate_3d_dose_distribution()
