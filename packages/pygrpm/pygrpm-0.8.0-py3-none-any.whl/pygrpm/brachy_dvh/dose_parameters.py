"""
Module: dose_control_parameters

This module defines Pydantic models to represent control parameters used during
dose calculation and DVH (Dose Volume Histogram) generation for brachytherapy.

It includes:
- DvhControlParameters: Configuration for DVH generation.
- Dose3dControlParameters: Configuration for 3D dose grid generation.
- DoseControlParameters: High-level configuration encompassing both DVH and dose settings.
"""

from typing import Union

# pylint: disable=no-name-in-module
from pydantic import BaseModel, Field

from pygrpm.brachy_dvh.dicom.brachy_rt_plan_wrapper import BrachyTreatmentType
from pygrpm.tg43 import SourceType


class DvhControlParameters(BaseModel):
    """
    Parameters used to control the generation of Dose Volume Histograms (DVH).
    """
    max_dose: Union[float, None] = Field(None, description="Maximum allowable dose value")
    number_of_bins: int = Field(-1, description="The number of bins")
    number_of_points: int = Field(-1, description="The number of points to calculate DVH curves")
    slice_resolution: Union[float, None] = \
        Field(None, description="The inter slice resolution for structure interpolation")

    def update(self, **kwargs):
        """
        Returns a new DvhControlParameters instance with updated fields.
        """
        updated_data = self.model_dump()
        updated_data.update(kwargs)
        return DvhControlParameters(**updated_data)


class Dose3dControlParameters(BaseModel):
    """
    Parameters used to control the generation of the 3D dose grid.
    """
    max_dose: Union[float, None] = Field(None, description="Maximum allowable dose value")
    voxel_size_x: float = Field(-1.0, description="Voxel size in the x direction [mm]")
    voxel_size_y: float = Field(-1.0, description="Voxel size in the y direction [mm]")
    voxel_size_z: float = Field(-1.0, description="Voxel size in the z direction [mm]")

    def update(self, **kwargs):
        """
        Returns a new DvhControlParameters instance with updated fields.
        """
        updated_data = self.model_dump()
        updated_data.update(kwargs)
        return DvhControlParameters(**updated_data)  # returns a new instance


class DoseControlParameters(BaseModel):
    """
    High-level dose calculation parameters, including both DVH and 3D dose settings.
    """
    brachy_treatment_type: BrachyTreatmentType = \
        Field(BrachyTreatmentType.Unknown,
              description="Type of brachytherapy treatment (LDR or HDR)")
    source_type: SourceType = Field(SourceType.Unknown, description="Source type (point or line)")
    source_name: str = Field("Unknown", description="The source source name used for calculation")
    dvh_control_parameters: Union[DvhControlParameters, None] = \
        Field(None, description="Dvh control parameters")

    dose_3d_control_parameters: Union[Dose3dControlParameters, None] = \
        Field(None, description="Dose 3d control parameters")

    def update(self, **kwargs):
        """
        Returns a new DvhControlParameters instance with updated fields.
        """
        updated_data = self.model_dump()
        updated_data.update(kwargs)
        return DvhControlParameters(**updated_data)
