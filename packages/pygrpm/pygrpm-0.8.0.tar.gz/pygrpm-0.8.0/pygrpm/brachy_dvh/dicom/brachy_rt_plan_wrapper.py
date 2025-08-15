"""
Module: brachy_rt_plan_wrapper

This module provides classes and utilities to parse and extract relevant information
from a DICOM RT Plan file for brachytherapy treatments (HDR and LDR).

It includes:
- BrachyTreatmentType enum to classify treatment type.
- BrachyRtPlanWrapper class to read, validate, and extract source-related parameters 
  from the DICOM RTPLAN file.
"""
import copy
import datetime
from enum import Enum
from pathlib import Path
from typing import List

import numpy as np
from pydicom import dcmread

from pygrpm.brachy_dvh.dicom.exceptions import DicomHelperError
from pygrpm.brachy_dvh.source_position import SourcePosition


class BrachyTreatmentType(Enum):
    """Types of brachytherapy treatment."""
    Unknown = 0
    LDR = 1
    HDR = 2


class BrachyRtPlanWrapper:
    """
    Wraps a DICOM RTPLAN file for brachytherapy and extracts source and treatment parameters.
    """
    def __init__(self, rt_plan_file_path: Path):
        if rt_plan_file_path.suffix != '.dcm':
            raise DicomHelperError(f'Expected .dcm extension, got {rt_plan_file_path.suffix}')

        if not rt_plan_file_path.exists():
            raise DicomHelperError(f'File {rt_plan_file_path} not found')

        self._rt_plan = dcmread(rt_plan_file_path)

        if self._rt_plan.Modality != 'RTPLAN':
            raise DicomHelperError(f'Expected RTPLAN, got {self._rt_plan.Modality}')

        self._set_air_kerma_strength()
        self._set_prescription()
        self._set_source_isotope_name()
        self._set_brachy_treatment_type()
        self._set_source_manufacturer()
        self._set_treatment_machine_manufacturer_model_name()
        self._set_source_strength_reference_date()
        self._set_referenced_structure_set_sop_instance_uid()
        self._set_source_positions()

    def __str__(self):
        """
        Returns a string representation of the extracted treatment plan details.
        """
        output_str = f'BrachyTreatmentType: {self.brachy_treatment_type}\n'
        output_str += f'Prescription: {self.prescription}\n'
        output_str += f'IsotopeName: {self.source_isotope_name}\n'
        output_str += f'SourceManufacturer: {self.source_manufacturer}\n'
        output_str += \
            f'TreatmentMachineManufacturerModelNane: {self.treatment_machine_manufacturer_model_name}\n'
        output_str += f'AirKermaStrength: {self.air_kerma_strength}\n'
        output_str += f'SourceStrengthReferenceDate: {self.source_strength_reference_date}'
        return output_str

    def _set_air_kerma_strength(self):
        """
        Extracts air kerma strength from the DICOM RT plan.
        """
        self._air_kerma_strength = -1.0
        for source in self._rt_plan.SourceSequence:
            if not hasattr(source, 'ReferenceAirKermaRate'):
                continue
            self._air_kerma_strength = float(source.ReferenceAirKermaRate)
            break

        if self._air_kerma_strength <= 0.0:
            raise DicomHelperError('Cannot set air kerma strength, attribute missing')

    def _set_prescription(self):
        """
        Extracts the prescribed dose from the RT plan.
        """
        self._prescription = -1.0
        for item_fgs in self._rt_plan.FractionGroupSequence:
            for item in item_fgs.ReferencedBrachyApplicationSetupSequence:
                self._prescription = float(item.BrachyApplicationSetupDose)

        if self._prescription <= 0.0:
            raise DicomHelperError(f'Prescription value of {self._prescription} is not valid')

    def _set_brachy_treatment_type(self):
        """
        Determines the type of brachytherapy treatment (HDR, LDR, or Unknown) 
        given the RT plan info.
        """
        if self._rt_plan.BrachyTreatmentType == 'LDR':
            self._brachy_treatment_type = BrachyTreatmentType.LDR
        elif self._rt_plan.BrachyTreatmentType == 'HDR':
            self._brachy_treatment_type = BrachyTreatmentType.HDR
        else:
            self._brachy_treatment_type = BrachyTreatmentType.Unknown

    def _set_source_isotope_name(self):
        """
        Extracts the source isotope name used in the plan.
        """
        self._source_isotope_name = 'Unknown'
        for source in self._rt_plan.SourceSequence:
            if not hasattr(source, 'SourceIsotopeName'):
                continue
            self._source_isotope_name = str(source.SourceIsotopeName)
            break

        if self._source_isotope_name == 'Unknown':
            raise DicomHelperError('Source isotope name is unknown')

    def _set_source_manufacturer(self):
        """
        Extracts the name of the source manufacturer in the plan.
        """
        self._source_manufacturer = 'Unknown'
        for source in self._rt_plan.SourceSequence:
            if hasattr(source, 'SourceManufacturer'):
                self._source_manufacturer = str(source.SourceManufacturer)
                break
        if self.source_manufacturer == 'Unknown' :
            raise DicomHelperError('Source manufacturer is unknown')

    def _set_treatment_machine_manufacturer_model_name(self):
        """
        Extracts the model name of the treatment machine.
        """
        self._treatment_machine_manufacturer_model_name = 'Unknown'
        for treatment_machine in self._rt_plan.TreatmentMachineSequence:
            if hasattr(treatment_machine, 'ManufacturerModelName'):
                self._treatment_machine_manufacturer_model_name = \
                    str(treatment_machine.ManufacturerModelName)
                break

    def _set_source_strength_reference_date(self):
        """
        Extracts the source strength reference date from the plan.
        """
        self._source_strength_reference_date = None
        for source in self._rt_plan.SourceSequence:
            self._source_strength_reference_date = \
                datetime.datetime.strptime(source.SourceStrengthReferenceDate, "%Y%m%d").date()

    def _set_referenced_structure_set_sop_instance_uid(self):
        """
        Extracts the SOP Instance UID of the referenced structure set.
        """
        self._referenced_structure_set_sop_instance_uid = "Unknown"
        for referenced_structure_set in self._rt_plan.ReferencedStructureSetSequence:
            self._referenced_structure_set_sop_instance_uid = \
                str(referenced_structure_set.ReferencedSOPInstanceUID)
        if self._referenced_structure_set_sop_instance_uid == "Unknown":
            raise DicomHelperError("Cannot find referenced structure set")

    def _set_source_directions(self):
        """
        Computes and assigns direction vectors to each source position based on their 
        neighboring positions.
        """
        # based on available source positions, might not be accurate for source positions
        # one source within one catheter and/or missing consecutive source positions
        catheter_index = self.source_positions[0].catheter_index
        dict_catheter_source_positions = {catheter_index: []}
        for source_position in self.source_positions:
            if catheter_index != source_position.catheter_index:
                catheter_index = source_position.catheter_index
                dict_catheter_source_positions[catheter_index] = []
            dict_catheter_source_positions[catheter_index].append(
                np.array(source_position.position))

        dict_catheter_source_directions = {}
        for catheter_index, source_positions in dict_catheter_source_positions.items():
            dict_catheter_source_directions[catheter_index] = []
            n_source_positions = len(source_positions)
            if n_source_positions == 1:
                dict_catheter_source_directions[catheter_index].append((0, 0, 1))
            elif n_source_positions == 2:
                direction = source_positions[0] - source_positions[1]
                direction /= np.linalg.norm(direction)
                direction = (direction[0], direction[1], direction[2])
                dict_catheter_source_directions[catheter_index].append(direction)
                dict_catheter_source_directions[catheter_index].append(direction)
            else:
                for i in range(n_source_positions):
                    if i == 0:
                        direction = source_positions[0] - source_positions[1]
                        direction /= np.linalg.norm(direction)
                        direction = (direction[0], direction[1], direction[2])
                        dict_catheter_source_directions[catheter_index].append(direction)
                    elif i == n_source_positions - 1:
                        direction = source_positions[-2] - source_positions[-1]
                        direction /= np.linalg.norm(direction)
                        direction = (direction[0], direction[1], direction[2])
                        dict_catheter_source_directions[catheter_index].append(direction)
                    else:
                        direction = source_positions[i + 1] - source_positions[i - 1]
                        direction /= np.linalg.norm(direction)
                        direction = (direction[0], direction[1], direction[2])
                        dict_catheter_source_directions[catheter_index].append(direction)

        i_source = 0
        for catheter_index, source_directions in dict_catheter_source_directions.items():
            for direction in source_directions:
                self._source_positions[i_source].direction = direction
                i_source += 1

    def _set_source_positions(self):
        """
        Extracts source dwell positions and associated parameters from the DICOM RT plan.
        """
        self._source_positions = []
        number_of_catheters = 0
        for applicator_setup in self._rt_plan.ApplicationSetupSequence:
            if hasattr(applicator_setup, 'ChannelSequence') :
                for _, channel in enumerate(applicator_setup.ChannelSequence):
                    weight_0 = 0.
                    control_point_relative_position_0 = -1
                    channel_total_time = channel.ChannelTotalTime
                    final_cumulative_time_weight = channel.FinalCumulativeTimeWeight
                    if channel_total_time != 0:
                        number_of_catheters += 1
                    for control_point in channel.BrachyControlPointSequence:
                        weight = control_point.CumulativeTimeWeight
                        if weight is None:
                            continue
                        control_point_relative_position = control_point.ControlPointRelativePosition
                        if control_point_relative_position_0 != control_point_relative_position:
                            control_point_relative_position_0 = control_point_relative_position
                            continue
                        #In LDR case for post-treatment, ignore some source position
                        # that appear to be useless (CDT = 0) after the main one
                        if weight - weight_0 < 0 :
                            break
                        source_weight = (weight - weight_0) * channel_total_time / \
                        final_cumulative_time_weight
                        control_point_3d_position = control_point.ControlPoint3DPosition
                        x = float(control_point_3d_position[0]) / 10.0 # mm -> cm
                        y = float(control_point_3d_position[1]) / 10.0
                        z = float(control_point_3d_position[2]) / 10.0
                        catheter_index = channel.ChannelNumber
                        weight_0 = weight
                        source_position = SourcePosition(
                            position=(x, y, z),
                            direction=(0, 0, 1),
                            weight=source_weight,
                            catheter_index=catheter_index,
                            relative_position=control_point_relative_position_0
                            )
                        self._source_positions.append(source_position)
                #In the case of HDR or pre-treament LDR, we only want to consider the first
                # application setup, which have a undefined type
                if applicator_setup.ApplicationSetupType == 'UNDEFINED' :
                    break

        if len(self._source_positions) == 0:
            raise DicomHelperError('No source positions found in plan')
        self._set_source_directions()

    @property
    def air_kerma_strength(self) -> float:
        """Returns the air kerma strength of the source."""
        return self._air_kerma_strength

    @property
    def prescription(self) -> float:
        """Returns the prescribed dose."""
        return self._prescription

    @property
    def brachy_treatment_type(self) -> BrachyTreatmentType:
        """Returns the type of brachytherapy treatment."""
        return self._brachy_treatment_type

    @property
    def source_positions(self) -> List[SourcePosition]:
        """Returns source positions."""
        return copy.deepcopy(self._source_positions)

    @property
    def source_manufacturer(self) -> str:
        """Returns the name of the source manufacturer."""
        return self._source_manufacturer

    @property
    def source_isotope_name(self) -> str:
        """Returns the name of the source isotope."""
        return self._source_isotope_name

    @property
    def treatment_machine_manufacturer_model_name(self) -> str:
        """Returns the treatment machine's model name."""
        return self._treatment_machine_manufacturer_model_name

    @property
    def source_strength_reference_date(self) -> datetime.datetime:
        """Returns the reference date for the source strength."""
        return self._source_strength_reference_date

    @property
    def referenced_structure_set_sop_instance_uid (self) -> str:
        """Returns the SOP Instance UID of the referenced structure set."""
        return self._referenced_structure_set_sop_instance_uid
