"""Utility submodule to make SR"""
from typing import Dict, List, Union

import pydicom

from . import utils
from .builder import SRBuilder
from .terminologies import dicom_terminologies


def make_sr(
        content_sequence: Dict,
        dicom_to_refer: Union[
            str, pydicom.FileDataset,
            List[Union[str, pydicom.FileDataset]]
        ] = None,
        purpose_of_reference_code: Union[Dict, List[Dict]] = None,
        completion_flag: bool = True) -> pydicom.FileDataset:
    """Creates a DICOM SR object

    Args:
        content_sequence: Content sequence, ex.
            {'ValueType': ...,
             'Value': 'some text', 'ConceptNameCodeSequence': {
                'CodeValue': '1233',
                'CodeMeaning': 'Test',
                'CodingSchemeDesignator': 'DCM',
            },
            'SomeOtherTag' : 'Some additional information'}
        dicom_to_refer: File path or pydicom.FileDataset object or list of those objects of
            the source DICOM file to use to assemble the DICOMSR object
        purpose_of_reference_code: Dictionary or list of directory with information tags on
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

    Returns:
        A DICOM SR object (pydicom.FileDataset)
    """
    if dicom_to_refer is not None and purpose_of_reference_code is None:
        # If the dicom_to_refer is not None, the purpose_of_reference_code has to be provided.
        # If not provided, use the default

        # Ensure that dicom_to_refer is a list
        if not isinstance(dicom_to_refer, list):
            dicom_to_refer = [dicom_to_refer]

        # Ensure that dicom_to_refer are pydicom.FileDataset
        dicom_to_refer = [utils.read_dicom(dicom) for dicom in dicom_to_refer]

        purpose_of_reference_code = _make_default_purpose_of_reference_codes(dicom_to_refer)

    # Building DICOM SR file based on the study
    sr_builder = SRBuilder(
        dicom_to_refer=dicom_to_refer,
        purpose_of_reference_code=purpose_of_reference_code,
        completion_flag=completion_flag
    )

    # Adding content_sequence, populating DICOM SR file an extracting
    sr_builder.add_content_sequence(content_sequence)
    sr_builder.build()

    finalize_dicom_sr = sr_builder.dicom_sr

    # Returning the DiCOM SR File in DICOM format
    return finalize_dicom_sr


def make_sr_from_text(
        text: Union[str, List[str]],
        dicom_to_refer: [
            str, pydicom.FileDataset,
            List[Union[str, pydicom.FileDataset]]
        ] = None,
        purpose_of_reference_code: Union[Dict, List[Dict]] = None,
        completion_flag: bool = True) -> pydicom.FileDataset:
    """Create a DICOM SR file containing the text given in parameter.

    Args:
        text: string or list of strings of the text to add
        dicom_to_refer: File path or pydicom.FileDataset object or list of those objects of
            the source DICOM file to use to assemble the DICOMSR object
        purpose_of_reference_code: Dictionary or list of directory with information tags on
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

    Returns:
        A DICOM SR object (pydicom.FileDataset)
    """
    # If a string is received, make a list of one string

    if isinstance(text, str):
        text_list = []
        text_list.append(text)
        text = text_list
    # Create the value list of the content sequence
    value_list = []
    for text_item in text:
        value_list.append({
            "RelationshipType": "HAS PROPERTIES",
            "ValueType": "TEXT",
            "ConceptNameCodeSequence": {
                "CodeValue": "113012",
                "CodeMeaning": "Key Object Description",
                "CodingSchemeDesignator": "DCM",
            },
            "Value": text_item,
        })
    # Create the content sequence
    content_sequence = {
        "ValueType": "CONTAINER",
        "ConceptNameCodeSequence": {
            "CodeValue": "DOC",
            "CodeMeaning": "Document",
            "CodingSchemeDesignator": "DCM",
        },
        "ContinuityOfContent": "SEPARATE",
        "Value": value_list,
    }

    return make_sr(
        content_sequence=content_sequence,
        dicom_to_refer=dicom_to_refer,
        purpose_of_reference_code=purpose_of_reference_code,
        completion_flag=completion_flag
    )


def _make_default_purpose_of_reference_codes(
        dicoms_to_refer: List[pydicom.FileDataset]) -> List[Dict]:
    purpose_of_reference_code = []

    for dicom in dicoms_to_refer:
        purpose_of_reference_code.append({
            'CodeValue': dicom.Modality,
            'CodeMeaning': dicom_terminologies.find_code_meaning(dicom.Modality),
            'CodingSchemeDesignator': 'DCM',
        })

    return purpose_of_reference_code
