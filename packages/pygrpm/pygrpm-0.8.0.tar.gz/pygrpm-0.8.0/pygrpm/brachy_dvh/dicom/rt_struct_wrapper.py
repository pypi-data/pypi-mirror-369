"""
Module: rt_struct_wrapper

This module provides the RtStructWrapper class, which parses a DICOM RT Structure Set
(RTSTRUCT) file and extracts structure definitions including contours and metadata.

It is used to read and represent anatomical structures for further processing,
such as DVH calculation or visualization.
"""

import copy
import logging
from pathlib import Path
from typing import List

import numpy as np
from pydicom import dcmread

from pygrpm.brachy_dvh.contour import Contour
from pygrpm.brachy_dvh.dicom.exceptions import DicomHelperError
from pygrpm.brachy_dvh.structure import Structure
from pygrpm.brachy_dvh.utils import InvalidDataError

logger = logging.getLogger(__name__)


class RtStructWrapper:
    """
    Wraps a DICOM RT Structure Set file (.dcm) and extracts structure data.

    This includes the SOP Instance UID, structure names, ROI numbers, and associated
    contours for each structure.

    Args:
        rt_struct_file_path (Path): Path to the RTSTRUCT DICOM file.

    Raises:
        DicomHelperError: If the file is not a valid .dcm RTSTRUCT file.
    """

    def __init__(self, rt_struct_file_path: Path):
        if rt_struct_file_path.suffix != '.dcm':
            raise DicomHelperError(f'Expected .dcm extension, got {rt_struct_file_path.suffix}')

        if not rt_struct_file_path.exists():
            raise DicomHelperError(f'File {rt_struct_file_path} not found')

        self._rt_struct = dcmread(rt_struct_file_path)

        if self._rt_struct.Modality != 'RTSTRUCT':
            raise DicomHelperError(f'Expected RTSTRUCT, got {self._rt_struct.Modality}')

        self._set_structures()
        self._set_sop_instance_uid()

    def _set_sop_instance_uid(self):
        """
        Extracts the SOP Instance UID from the RT Structure Set.
        """
        self._sop_instance_uid = str(self._rt_struct.SOPInstanceUID)

    def _set_structures(self):
        """
        Extracts the list of anatomical structures and their contours from the RTSTRUCT.
        """
        list_roi_names = []
        list_roi_numbers = []
        for roi in self._rt_struct.StructureSetROISequence:
            list_roi_names.append(roi.ROIName)
            list_roi_numbers.append(roi.ROINumber)

        self._list_structures = []
        for i, roi_contour in enumerate(self._rt_struct.ROIContourSequence):
            roi_name = list_roi_names[i]
            roi_number = list_roi_numbers[i]
            list_contours = []

            if hasattr(roi_contour, 'ContourSequence'):
                for contour in roi_contour.ContourSequence:
                    tmp_contour = []
                    contour_data = contour.ContourData
                    number_of_contours_points = contour.NumberOfContourPoints
                    for p in range(number_of_contours_points):
                        p3 = 3 * p
                        tmp_contour.append(
                            [float(contour_data[p3]), float(contour_data[p3 + 1]),
                             float(contour_data[p3 + 2])]
                        )
                    try:
                        list_contours.append(Contour(np.array(tmp_contour)))
                    except InvalidDataError:
                        logger.warning("Cannot create contour for ROI '%s'", roi_name)
                        continue

            try:
                self._list_structures.append(
                    Structure(list_contours, roi_name=roi_name, roi_number=roi_number)
                )
            except InvalidDataError as e:
                logger.warning("Cannot create structure for '%s': %s", roi_name, e)
                continue

    @property
    def structures(self) -> List[Structure]:
        """
        Returns:
            List[Structure]: A deep copy of the list of structures in the RTSTRUCT.
        """
        return copy.deepcopy(self._list_structures)

    @property
    def sop_instance_uid(self) -> str:
        """
        Returns:
            str: SOP Instance UID of the RTSTRUCT file.
        """
        return self._sop_instance_uid
