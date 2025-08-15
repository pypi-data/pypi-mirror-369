"""
Module containing dataclasses to represent and store dicom information
"""
import os
import warnings
from dataclasses import dataclass, field
from typing import List, Union

import numpy as np
import pydicom


# disabling name linting due to UID present in names
# pylint: disable=invalid-name
@dataclass
class DicomSeries:
    """
    Dataclass meant to contain a Dicom series along with easy access to key values
    """

    series_UID: str
    study_UID: str
    patientID: str
    modality: str
    instances: List[pydicom.FileDataset]
    reference_folder_path: Union[str, os.PathLike]

    _numpy: np.ndarray = field(init=False, repr=False)

    @property
    def instances_UID(self) -> List[Union[str, pydicom.uid.UID]]:
        """
        property method to return a list of all instances uid within the series dataclass
        @return: An similarly ordered list of instances UID
        """
        return [instance.SOPInstanceUID for instance in self.instances]

    @property
    def numpy(self) -> Union[np.ndarray, None]:
        """
        Returns the volume represented in the list of Instances' pixel_array
        Volume is in a "slices last" format
        @return: The associated numpy array if found
        """
        # If already generated, return it
        if hasattr(self, "_numpy"):
            return self._numpy

        if "PixelData" not in self.first_instance:
            return None

        # If we have a case like CT images, many 2D arrays making a 3D
        if self.first_instance.pixel_array.ndim == 2 and len(self.instances) > 1:
            self._make_3D_from_2D()

        # If we just have a 3D array
        elif self.first_instance.pixel_array.ndim == 3:
            self._numpy = self.first_instance.pixel_array

        return self._numpy

    def _make_3D_from_2D(self) -> None:
        # Sort by Z
        self.sort_instances_by_tag("ImagePositionPatient", 2)

        volume_stack = []
        for instance in self.instances:
            # Check PixelData and not pixel_array as the latter is a getter, not a property
            if "PixelData" not in instance:
                warnings.warn("Instance within the series has no pixel array.")

            volume_stack.append(instance.pixel_array)

        self._numpy = np.stack(volume_stack, axis=-1)

    @property
    def first_instance(self) -> pydicom.FileDataset:
        """
        Provide a sample dicom file for tag referencing
        @return:
        """
        # Chosen by fair random dice roll
        return self.instances[0]

    def sort_instances_by_tag(self, tag: str, index: int = None) -> None:
        """
        Sort the dicom instance list based on tag
        @param tag: Dicom tag as represented by pydicom
        @param index: Index in the tag's tuple/list if relevent
        @return: None
        """
        if len(self.instances) > 0:
            if index:
                self.instances.sort(key=lambda dcm: dcm[tag].value[index])
            else:
                self.instances.sort(key=lambda dcm: dcm[tag].value)

    def get_instance(self, instance_UID: Union[str, pydicom.uid.UID]):
        """
        Helper method to obtain a Dicom instance (pydicom dataset) from its DicomSeries
        @param series_UID: SeriesInstanceUID
        @return: The DicomSeries dataclass matching the provided UID
        """
        for instance in self.instances:
            if instance.SOPInstanceUID == instance_UID:
                return instance
        return None

@dataclass
class DicomStudy:
    """
    Dataclass to represent a Dicom patient study
    """

    study_UID: str
    patientID: str
    series: List[DicomSeries]
    reference_folder_paths: List[Union[str, os.PathLike]]

    _modalities: List = field(init=False, repr=False)

    @property
    def series_UID(self) -> List[Union[str, pydicom.uid.UID]]:
        """
        property method to return a list of all series uid within the study dataclass
        @return: An similarly ordered list of series UID
        """
        return [series.series_UID for series in self.series]

    def filter_by_modality(self, modality: str) -> List[DicomSeries]:
        """
        Helper method to grab only series of a specific modality from the study
        @param modality: The dicom modality as it appears in pydicom
        @return: List of relevant DicomSeries dataclasses
        """
        return [series for series in self.series if series.modality == modality]

    @property
    def modalities(self) -> List[str]:
        """
        Property method to obtain all modalities present in the study
        @return: List of modalities as they appear in pydicom
        """
        return [series.modality for series in self.series]

    def get_series(self, series_UID: Union[str, pydicom.uid.UID]):
        """
        Helper method to obtain a DicomSeries class from its DicomStudy
        @param series_UID: SeriesInstanceUID
        @return: The DicomSeries dataclass matching the provided UID
        """
        for series in self.series:
            if series.series_UID == series_UID:
                return series
        return None
