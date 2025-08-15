# code: utf-8
# author: Pierre-Luc Asselin, April 2023
# Based on module coded by Samuel Ouellet, March 2022

"""
Core class used for DICOM-SR Generation
Contains all methods used in this way
"""

import logging
from datetime import datetime
from typing import Dict, List, Union

import pydicom
from pydicom.dataset import FileMetaDataset
from pydicom.filebase import DicomBytesIO
from pydicom.uid import PYDICOM_IMPLEMENTATION_UID

from pygrpm.dicom.uid import generate_uid

from .sr_tags import (
    SR_TYPING,
    make_concept_name_code_sequence,
    make_content_sequence,
    make_referenced_instance_sequence,
)
from .utils import read_dicom

_logger = logging.getLogger(__name__)


class SRBuilder:
    """
    This allows the creation of a DICOM SR file from scratch. Lots of dummy values are added
    to the produced DICOMSR in order to fully follow the DICOM standard while allowing the
    user to save data that may not be related to a treatment. The steps for the basic usage
    of this class are simply to create a DICOMSRBuilder object, add content sequences with the
    method add_content_sequence and build the DICOMSR with the method build (which applies metadata
    with the method _apply_metadata_to_sr).
    """

    def __init__(
            self,
            dicom_to_refer: Union[str, pydicom.FileDataset,
                                  List[Union[str, pydicom.FileDataset]]] = None,
            purpose_of_reference_code: Union[Dict, List[Dict]] = None,
            completion_flag: bool = True
    ):
        """
        :param dicom_to_refer: File path or pydicom.FileDataset object or list of those objects of
         the source DICOM file to use to assemble the DICOMSR
         object Dicom files directly are also accepted
        :param purpose_of_reference_code: Dictionary or list of directory with information tags on
         why the target file is used to generate the DICOM SR. For example:
         {
            "CodeValue": "SEG",
            "CodeMeaning": "Segmentation",
            "CodingSchemeDesignator": "DCM",
         }
        completion_flag: Boolean indicating if the dicom SR contains all relevant information
        about its content, as requested by the DICOM standard. The completion flag should
        always be COMPLETE, but this parameter allows users to choose UNCOMPLETE if
        the SR isn't exhaustive.
        """
        if dicom_to_refer is not None:
            # Ensure that the dicom_to_refer is a list, and that the purpose_of_reference_code is
            # also a list of the same length
            if isinstance(dicom_to_refer, list) and isinstance(purpose_of_reference_code, list):
                assert len(dicom_to_refer) == len(purpose_of_reference_code), \
                    "dicom_to_refer and purpose_of_reference_code don't have the same length"

                self.dicom_to_refer = [read_dicom(d) for d in dicom_to_refer]
                self.purpose_of_reference_code = purpose_of_reference_code

            elif not isinstance(dicom_to_refer, list) and \
                    not isinstance(purpose_of_reference_code, list):
                self.dicom_to_refer = [read_dicom(dicom_to_refer)]
                self.purpose_of_reference_code = [purpose_of_reference_code]

            else:
                raise TypeError(
                    "dicom_to_refer and purpose_of_reference_code both have to be a list "
                    "or neither of them should be a list."
                )

        else:
            self.dicom_to_refer = None
            self.purpose_of_reference_code = None

        self.dicom_sr = None
        self.content_sequence = None
        self.completion_flag = completion_flag

    def add_content_sequence(self, content_sequence) -> None:
        """
        This method allow the user to add a content sequence before building the DICOMSR.

        It contains:

        ***Required Elements***
        - A single Concept Name Code Sequence (0040,A043)
        - A Value
        - The ValueType (text, codes, etc.)

        ***Optionnal Elements***
        - References to images, waveforms or other composite objects
        - Relationships to other Items (by nested content sequences or by reference)


        Format Example:
        {
            "ValueType": "TEXT",
            "Value": "This is some text",
            "ConceptNameCodeSequence": {
                "CodeValue": "1233",
                "CodeMeaning": "Test",
                "CodingSchemeDesignator": "DCM",
            },
            "SomeOtherTag" : "Some additionnal information"
        }

        :param content_sequence: List containing the content_sequence in the appropriate format.
        """
        if self._is_content_sequence_valid(content_sequence):
            self.content_sequence = content_sequence

    def build(self) -> None:
        """
        This method builds the actual DICOMSR. In here, all the information
        related to the DICOM file format is set before actually adding the content
        of the DICOM using _apply_metadata_to_sr().
        """
        if self.content_sequence is None:
            raise ValueError('Empty content sequence')

        # Inspired by https://pydicom.github.io/pydicom/stable/auto_examples/
        # input_output/plot_write_dicom.html
        basic_text_sr_class_uid = "1.2.840.10008.5.1.4.1.1.88.11"
        # Radiation therapy dose storage class
        instance_uid = str(generate_uid())

        self.dicom_sr = pydicom.FileDataset(
            None, {}, file_meta=None, preamble=b"\0" * 128
        )

        # Set the transfer syntax
        self.dicom_sr.is_little_endian = True
        self.dicom_sr.is_implicit_VR = True

        self.dicom_sr.SOPClassUID = basic_text_sr_class_uid
        self.dicom_sr.SOPInstanceUID = instance_uid

        self._apply_metadata_to_sr()

        # Apply file meta
        file_meta = FileMetaDataset()
        file_meta.FileMetaInformationVersion = b"\x00\x01"
        file_meta.MediaStorageSOPClassUID = basic_text_sr_class_uid
        file_meta.MediaStorageSOPInstanceUID = instance_uid
        file_meta.ImplementationClassUID = PYDICOM_IMPLEMENTATION_UID
        file_meta.TransferSyntaxUID = "1.2.840.10008.1.2"

        file_meta.is_little_endian = True
        file_meta.is_implicit_VR = False

        pydicom.dataset.validate_file_meta(file_meta, enforce_standard=True)

        # file_meta.FileMetaInformationGroupLength = 0
        # Write the File Meta Information Group elements
        # first write into a buffer to avoid seeking back, that can be
        # expansive and is not allowed if writing into a zip file
        buffer = DicomBytesIO()
        buffer.is_little_endian = True
        buffer.is_implicit_VR = False
        pydicom.filewriter.write_dataset(buffer, file_meta)

        # CODE FROM THE PYDICOM LIB:
        # If FileMetaInformationGroupLength is present it will be the first written
        #   element and we must update its value to the correct length.
        # Update the FileMetaInformationGroupLength value, which is the number
        #   of bytes from the end of the FileMetaInformationGroupLength element
        #   to the end of all the File Meta Information elements.
        # FileMetaInformationGroupLength has a VR of 'UL' and so has a value
        #   that is 4 bytes fixed. The total length of when encoded as
        #   Explicit VR must therefore be 12 bytes.
        file_meta.FileMetaInformationGroupLength = buffer.tell() - 12
        del buffer

        self.dicom_sr.file_meta = file_meta

    def _first_level_check_validity(self, content_sequence):
        """
        Submethod used for content_sequence validation
        when on tag's first level
        """
        if content_sequence["ValueType"] != "CONTAINER":
            _logger.warning("First level ValueType should be CONTAINER")
            raise ValueError
        if content_sequence["ContinuityOfContent"] not in [
            "SEPARATE",
            "CONTINUOUS",
        ]:
            _logger.warning(
                "First level ContinuityOfContent should be SEPARATE or CONTINUOUS"
            )
            raise ValueError
        if not isinstance(content_sequence["Value"], list):
            _logger.warning("%s Value should be a CONTAINER (list)", content_sequence)
            raise ValueError
        if "RelationshipType" in content_sequence.keys():
            _logger.warning("First level should not have a RelationshipType")
            raise ValueError

        for container in content_sequence["Value"]:
            if not self._is_content_sequence_valid(container, False):
                return False

        return True

    def _check_container_validity(self, content_sequence):
        """
        Submethod used for content_sequence validation
        when it matches the CONTAINER type
        """
        if content_sequence["ContinuityOfContent"] not in [
            "SEPARATE",
            "CONTINUOUS",
        ]:
            _logger.warning(
                "%s ContinuityOfContent must be SEPARATE or CONTINUOUS",
                content_sequence,
            )
            raise ValueError

        if not isinstance(content_sequence["Value"], list):
            _logger.warning("%s Value should be a CONTAINER (list)", content_sequence)
            raise ValueError

        for container in content_sequence["Value"]:
            if not self._is_content_sequence_valid(container, False):
                return False

        return True

    def _check_code_validity(self, content_sequence):
        """
        Submethod used for content_sequence validation
        when it matches the CODE type
        """
        if not self._is_code_sequence_valid(content_sequence["ConceptCodeSequence"]):
            return False

        if "Value" in content_sequence.keys():
            if not isinstance(content_sequence["Value"], list):
                _logger.warning(
                    "%s Value should be a CONTAINER or a Code (list)",
                    content_sequence,
                )
                raise ValueError

            for container in content_sequence["Value"]:
                if not self._is_content_sequence_valid(container, False):
                    return False

        return True

    @staticmethod
    def _is_code_sequence_valid(concept_name_code_sequence):
        """
        Submethod used for content_sequence validation
        Considers code_sequence requirements
        """
        try:
            if not isinstance(concept_name_code_sequence, dict):
                _logger.warning(
                    """\
                    %s should be a dict with keys: CodeValue,\
                    CodeMeaning and CodingSchemeDesignator
                    """,
                    concept_name_code_sequence,
                )
                raise ValueError
            if not isinstance(concept_name_code_sequence["CodeValue"], str):
                _logger.warning(
                    "%s CodeValue should be a int in str", concept_name_code_sequence
                )
                raise ValueError
            if not isinstance(concept_name_code_sequence["CodeMeaning"], str):
                _logger.warning(
                    "%s CodeMeaning should be a string", concept_name_code_sequence
                )
                raise ValueError

            if not isinstance(
                    concept_name_code_sequence["CodingSchemeDesignator"], str
            ):
                _logger.warning(
                    "%s CodingSchemeDesignator should be a string",
                    concept_name_code_sequence,
                )

                raise ValueError

            return True
        except (ValueError, KeyError, TypeError):
            return False

    def _is_content_sequence_valid(self, content_sequence, first_level=True):
        """
        General method for content_sequence's structure validation
        TODO - Currently untreated Value_Types:
        - NUM
        - PNAME
        - DATE
        - DATETIME
        - UIDREF
        - IMAGE
        - COMPOSITE
        - SCOORD
        - TCOORD
        """
        check_value = True

        try:
            if first_level:
                check_value = self._first_level_check_validity(content_sequence)

            else:
                if not isinstance(content_sequence["RelationshipType"], str):
                    _logger.warning(
                        "%s RelationshipType should be a string", content_sequence
                    )
                    raise ValueError

                if content_sequence["ValueType"] not in SR_TYPING:
                    _logger.warning(
                        "%s CodeValue should be in {SR_TYPING}", content_sequence
                    )
                    raise ValueError

                value_type = content_sequence["ValueType"]
                if value_type == "TEXT":
                    if not isinstance(content_sequence["Value"], str):
                        _logger.warning("%s Value should be a string", content_sequence)
                        raise ValueError

                elif value_type == "CONTAINER":
                    check_value = self._check_container_validity(content_sequence)

                elif value_type == "CODE":
                    check_value = self._check_code_validity(content_sequence)

            if not self._is_code_sequence_valid(
                    content_sequence["ConceptNameCodeSequence"]
            ):
                check_value = False

            return check_value

        except (KeyError, ValueError):
            return False

    def _apply_metadata_to_sr(self) -> None:
        """
        TODO: Add Referenced Request Sequence
        TODO: Add Performed ProcedureCode Sequence

        This method adds all the content to the DICOM. Here is a list of all the tags that
        were filled with default value:

        PatientID = "Dose%date%_%time" +
        PatientName = "Unknown^Unknown"
        PatientBirthDate = current_date
        PatientSex = "O"
        StudyDate = current_date
        StudyTime = current_time
        ReferringPhysicianName = "Unknown^Unknown"
        StudyID = ""
        StudyDescription = ''
        InstitutionName = ""

        SeriesDescription = ""
        SeriesDate = current_date
        SeriesTime = current_time
        OperatorsName = "Unknown^Unknown"
        SeriesNumber = 1

        InstanceCreationDate = current_date
        InstanceCreationTime = current_time

        Manufacturer = '"
        InstanceNumber = 1
        ContentDate = current_date
        ContentTime = current_time
        PhotometricInterpretation = 'MONOCHROME2'

        See https://dicom.innolitics.com/ciods/rt-dose/
        """
        current_date = datetime.now()

        # Patient Layer
        self.dicom_sr.PatientID = (
                "SR"
                + current_date.strftime("%Y%m%d")
                + "_"
                + current_date.strftime("%H%M%S.%f")
        )
        self.dicom_sr.PatientName = "Unknown^Unknown"
        self.dicom_sr.PatientBirthDate = current_date.strftime("%Y%m%d")
        self.dicom_sr.PatientSex = "O"

        # Study layer

        self.dicom_sr.StudyDate = current_date.strftime("%Y%m%d")
        self.dicom_sr.StudyTime = current_date.strftime("%H%M%S.%f")
        self.dicom_sr.AccessionNumber = ""
        self.dicom_sr.ReferringPhysicianName = "Unknown^Unknown"
        self.dicom_sr.StudyInstanceUID = generate_uid()
        self.dicom_sr.StudyID = ""
        self.dicom_sr.StudyDescription = ""
        self.dicom_sr.InstitutionName = ""

        # Series Layer

        self.dicom_sr.SeriesDescription = ""
        self.dicom_sr.SeriesDate = current_date.strftime("%Y%m%d")
        self.dicom_sr.SeriesTime = current_date.strftime(
            "%H%M%S.%f"
        )  # long format with micro seconds
        self.dicom_sr.Modality = "SR"
        self.dicom_sr.SeriesInstanceUID = generate_uid()
        self.dicom_sr.SeriesNumber = 1

        # Instance Layer

        self.dicom_sr.ContentDate = current_date.strftime("%Y%m%d")
        self.dicom_sr.ContentTime = current_date.strftime("%H%M%S.%f")
        self.dicom_sr.InstanceNumber = 1
        self.dicom_sr.InstanceCreationDate = current_date.strftime("%Y%m%d")
        self.dicom_sr.InstanceCreationTime = current_date.strftime(
            "%H%M%S.%f"
        )  # long format with micro seconds

        if self.dicom_to_refer is not None:
            self._make_referenced_instances()
            self._adapt_sr_to_existing_study()

        if self.completion_flag:
            self.dicom_sr.CompletionFlag = "COMPLETE"
        else:
            self.dicom_sr.CompletionFlag = "UNCOMPLETE"

        self.dicom_sr.VerificationFlag = "UNVERIFIED"
        self.dicom_sr.ValueType = self.content_sequence["ValueType"]
        self.dicom_sr.ContinuityOfContent = self.content_sequence["ContinuityOfContent"]
        self.dicom_sr.add(
            make_concept_name_code_sequence(
                self.content_sequence["ConceptNameCodeSequence"]["CodeValue"],
                self.content_sequence["ConceptNameCodeSequence"]["CodeMeaning"],
                self.content_sequence["ConceptNameCodeSequence"][
                    "CodingSchemeDesignator"
                ],
            )
        )
        for content in self.content_sequence["Value"]:
            try:
                self.dicom_sr.ContentSequence += [make_content_sequence(content)]

            except AttributeError:
                self.dicom_sr.add(
                    pydicom.DataElement(
                        (0x0040, 0xA730), "SQ", [make_content_sequence(content)]
                    )
                )

    def _make_referenced_instances(self):
        self.dicom_sr.add(
            make_referenced_instance_sequence(
                [dicom.SOPClassUID for dicom in self.dicom_to_refer],
                [dicom.SOPInstanceUID for dicom in self.dicom_to_refer],
                [purpose["CodeValue"] for purpose in self.purpose_of_reference_code],
                [purpose["CodeMeaning"] for purpose in self.purpose_of_reference_code],
                [purpose["CodingSchemeDesignator"] for purpose in self.purpose_of_reference_code],
            )
        )

    def _adapt_sr_to_existing_study(self):
        """
        Retrieve the Patient and Study level information from the
        first referenced instance (dicom_to_refer) and apply it to this SR.
        """
        dicom_to_refer = self.dicom_to_refer[0]

        # Patient Layer
        self.dicom_sr.PatientID = dicom_to_refer.PatientID
        self.dicom_sr.PatientName = dicom_to_refer.PatientName
        self.dicom_sr.PatientBirthDate = dicom_to_refer.PatientBirthDate
        self.dicom_sr.PatientSex = dicom_to_refer.PatientSex

        # Study layer
        self.dicom_sr.StudyDate = getattr(dicom_to_refer, "StudyDate", "")
        self.dicom_sr.StudyTime = getattr(dicom_to_refer, "StudyTime", "")
        self.dicom_sr.AccessionNumber = getattr(dicom_to_refer, "AccessionNumber", "")

        if hasattr(dicom_to_refer, 'InstitutionName'):
            self.dicom_sr.InstitutionName = dicom_to_refer.InstitutionName

        if hasattr(dicom_to_refer, 'InstitutionalDepartmentalName'):
            self.dicom_sr.InstitutionalDepartmentalName = \
                dicom_to_refer.InstitutionalDepartmentalName

        self.dicom_sr.ReferringPhysicianName = getattr(dicom_to_refer, "ReferringPhysicianName", "")
        self.dicom_sr.StudyInstanceUID = dicom_to_refer.StudyInstanceUID
        self.dicom_sr.StudyID = dicom_to_refer.StudyID

        if hasattr(dicom_to_refer, 'StudyDescription'):
            self.dicom_sr.StudyDescription = dicom_to_refer.StudyDescription
