"""
dose_calculation_service_from_dicom.py

Provides a high-level interface to calculate dose distributions and dose-volume histograms (DVHs)
from DICOM RTSTRUCT and RTPLAN files for brachytherapy using TG43 formalism.
"""
from pathlib import Path
from typing import Dict, Tuple, Union

import numpy as np

from pygrpm.brachy_dvh.dicom.brachy_rt_plan_wrapper import (
    BrachyRtPlanWrapper,
    BrachyTreatmentType,
)
from pygrpm.brachy_dvh.dicom.rt_struct_wrapper import RtStructWrapper
from pygrpm.brachy_dvh.dose_calculation_service import (
    DoseCalculationService,
    DoseCalculationServiceError,
)
from pygrpm.brachy_dvh.dose_parameters import (
    Dose3dControlParameters,
    DoseControlParameters,
    DvhControlParameters,
)
from pygrpm.brachy_dvh.dvh import DVH
from pygrpm.tg43.seed import SourceType


class DoseCalculationServiceFromDicom:
    """Service for calculating dose distributions and DVHs from DICOM RTSTRUCT 
    and RTPLAN files."""

    def __init__(
            self,
            rt_plan_file_path: Path,
            rt_struct_file_path: Path,
            dvh_control_parameters: Union[DvhControlParameters, None],
            dose_3d_control_parameters: Union[Dose3dControlParameters, None]
    ):
        """
        Initializes the service by parsing DICOM RTSTRUCT and RTPLAN files
        and validating their consistency.
        """
        self._rt_struct_wrapper = RtStructWrapper(rt_struct_file_path)
        self._brachy_rt_plan_wrapper = BrachyRtPlanWrapper(rt_plan_file_path)

        # validate dicom files
        if self._rt_struct_wrapper.sop_instance_uid != \
                self._brachy_rt_plan_wrapper.referenced_structure_set_sop_instance_uid:
            raise DoseCalculationServiceError(
                "RTSTRUCT SOPInstanceUID does not match RTPLAN referenced " \
                "structure set SOPInstanceUID"
            )

        # required for tg43 calculations
        self._source_positions = self._brachy_rt_plan_wrapper.source_positions
        self._air_kerma_strength = self._brachy_rt_plan_wrapper.air_kerma_strength
        self._structures = self._rt_struct_wrapper.structures
        self._update_control_parameters(dvh_control_parameters, dose_3d_control_parameters)
        self._dose_calculation_service = DoseCalculationService(
            self._control_parameters,
            self._source_positions,
            self._air_kerma_strength
        )

    def _update_control_parameters(
            self,
            dvh_control_parameters: Union[DvhControlParameters, None],
            dose_3d_control_parameters: Union[Dose3dControlParameters, None]
    ) -> None:
        """
        Prepares control parameters for dose and DVH calculations based on DICOM plan content.
        """
        brachy_treatment_type = self._brachy_rt_plan_wrapper.brachy_treatment_type
        if brachy_treatment_type == BrachyTreatmentType.HDR:
            source_type = SourceType.Line
        elif brachy_treatment_type == BrachyTreatmentType.LDR:
            source_type = SourceType.Point
            for source_position in self._source_positions:
                source_position.direction = None
        else:
            raise DoseCalculationServiceError("Brachy treatment type not found")

        source_name = self._select_source_for_tg43_calculation()

        if dvh_control_parameters is not None:
            if dvh_control_parameters.max_dose is None:
                dvh_control_parameters.max_dose = 4 * self._brachy_rt_plan_wrapper.prescription

        if dose_3d_control_parameters is not None:
            if dose_3d_control_parameters.max_dose is None:
                dose_3d_control_parameters.max_dose = 4 * self._brachy_rt_plan_wrapper.prescription

        self._control_parameters = DoseControlParameters(
            brachy_treatment_type=brachy_treatment_type,
            source_type=source_type,
            source_name=source_name,
            dvh_control_parameters=dvh_control_parameters,
            dose_3d_control_parameters=dose_3d_control_parameters
        )

    def _select_source_for_tg43_calculation(self) -> str:
        """
        Returns the standardized source name based on isotope and manufacturer.
        """
        source_name = "Unknown"
        if self._brachy_rt_plan_wrapper.source_isotope_name == "I-125":
            if self._brachy_rt_plan_wrapper.source_manufacturer == 'Nucletron B.V.':
                source_name = "SelectSeed"
            elif self._brachy_rt_plan_wrapper.source_manufacturer == 'IsoAid':
                source_name = "IsoAid"
        if self._brachy_rt_plan_wrapper.source_isotope_name == "Ir-192":
            source_name = "Flexisource"

        return source_name

    def calculate_dvh(self, roi_name: str, normalize=True) -> DVH:
        """
        Calculates the DVH for a single ROI name.
        """
        for structure in self._structures:
            if structure.roi_name == roi_name:
                dvh = self._dose_calculation_service.calculate_dvh(structure)
                if normalize:
                    dvh._cumulative_dvh = dvh._cumulative_dvh / (structure.volume / 1000) * 100
                    dvh._differential_dvh = dvh._differential_dvh / (structure.volume / 1000) * 100
                return dvh

        raise DoseCalculationServiceError("ROI name could not match any structure")

    def calculate_dvhs(self, normalize_dvhs=True) -> Dict[str, DVH]:
        """
        Calculates DVHs for all structures in the RTSTRUCT.
        """
        dict_dvhs = {}
        for structure in self._structures:
            print(f'Calculating DVHs for {structure.roi_name} ...')
            if not normalize_dvhs:
                dict_dvhs[structure.roi_name] = self.calculate_dvh(structure.roi_name,
                                                                   normalize=False)
            else:
                dict_dvhs[structure.roi_name] = self.calculate_dvh(structure.roi_name)
        return dict_dvhs

    def calculate_3d_dose_distribution(
            self,
    ) -> Tuple[np.ndarray, Tuple[float, float, float]]:
        """
        Computes the full 3D dose distribution.
        """
        return self._dose_calculation_service.calculate_3d_dose_distribution(self._structures)
