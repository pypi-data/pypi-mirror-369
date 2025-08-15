# code: utf-8
# author: Pierre-Luc Asselin, April 2023
# Based on module coded by Samuel Ouellet, March 2022

# pylint raises an error because some function have to many elif.
# pylint: disable=R0912

"""
DICOM tags utility functions for DICOM-SR
creation and format validation.
"""

import logging
from typing import Any, List, Tuple, Union

import pydicom
import pydicom.config
from pydicom.valuerep import validate_value

_logger = logging.getLogger(__name__)


SR_TYPING = [
    "CONTAINER",
    "CODE",
    "COMPOSITE",
    "DATE",
    "DATETIME",
    "IMAGE",
    "NUM",
    "PNAME",
    "SCOORD",
    "TCOORD",
    "TEXT",
    "TIME",
    "UIDREF",
    "WAVEFORM",
]


def make_dicom_tag(
        tag: Union[int, str, Tuple[int, int]],
        visual_representation: str,
        value: Any,
        validation_mode: int = pydicom.config.RAISE) -> pydicom.DataElement:
    """
    Returns a valid dicom tag element, via pydicom
    """
    # This ignores (pydicom.config.IGNORE), logs (pydicom.config.WARN) or
    # raises (pydicom.config.RAISE) depending on `validation_mode` value.
    validate_value(vr=visual_representation, validation_mode=validation_mode, value=value)

    return pydicom.DataElement(tag, visual_representation, value, validation_mode=validation_mode)


def make_value_type(value_type):
    """
    Returns a "Value Type" Tag Element using the parameter given
    """
    assert value_type in SR_TYPING
    return make_dicom_tag((0x0040, 0xA040), "CS", value_type)


def make_text_value(text_value):
    """
    Returns a "Text Type" Tag Element using the parameter given
    """
    return make_dicom_tag((0x0040, 0xA160), "UT", text_value)


def make_person_name(person_name: str):
    """
    Returns a "Person Name" Tag Element using the parameter given
    """
    return make_dicom_tag((0x0040, 0xA123), "PN", person_name)


def make_date(date: str):
    """
    Returns a "Date" Tag Element using the parameter given
    """
    return make_dicom_tag((0x0040, 0xA121), "DA", date)


def make_datetime(date_time: str):
    """
    Returns a "DateTime" Tag Element using the parameter given
    """
    return make_dicom_tag((0x0040, 0xA120), "DT", date_time)


def make_uid_ref(uid: str):
    """
    Returns a "UID" Tag Element using the parameter given
    """
    return make_dicom_tag((0x0040, 0xA124), "UI", uid)


def make_continuity_content(contunuity_of_content):
    """
    Returns a "Continuity Of Content" Tag Element using the parameter given
    """
    return make_dicom_tag((0x0040, 0xA050), "CS", contunuity_of_content)


def make_numeric_value(num_value: str):
    """
    Returns a "Numeric Value" Tag Element using the parameter given
    """
    return make_dicom_tag((0x0040, 0xA30A), "DS", num_value)


def make_floating_point_value(num_value: float):
    """
    Returns a "Floating Point Value" Tag Element using the parameter given
    """
    return make_dicom_tag((0x0040, 0xa161), "FD", num_value)


def make_code_value(code_value: str):
    """
    Returns a "Code Value" Tag Element using the parameter given
    """
    if len(code_value) > 16:
        return make_dicom_tag((0x0008, 0x0119), "UC", code_value)

    return make_dicom_tag((0x0008, 0x0100), "SH", code_value)


def make_code_meaning(code_meaning):
    """
    Returns a "Code Meaning" Tag Element using the parameter given
    """
    return make_dicom_tag((0x0008, 0x0104), "LO", code_meaning)


def make_coding_scheme_designator(code_scheme_designator):
    """
    Returns a "Coding Scheme Designator" Tag Element using the parameter given
    """
    return make_dicom_tag((0x0008, 0x0102), "SH", code_scheme_designator)


def make_concept_code_sequence(code_value, code_meaning, coding_scheme_designator):
    """
    Returns a "Concept Code Sequence" Tag Element.
    Creates a dataset with the parameters given
    """
    dataset = pydicom.Dataset()
    dataset.add(make_code_value(code_value))
    dataset.add(make_code_meaning(code_meaning))
    dataset.add(make_coding_scheme_designator(coding_scheme_designator))

    return make_dicom_tag((0x0040, 0xA168), "SQ", [dataset])


def make_concept_name_code_sequence(code_value, code_meaning, coding_scheme_designator):
    """
    Returns a "Concept Name Code Sequence" Tag Element.
    Creates a dataset with the parameters given
    """
    dataset = pydicom.Dataset()
    dataset.add(make_code_value(code_value))
    dataset.add(make_code_meaning(code_meaning))
    dataset.add(make_coding_scheme_designator(coding_scheme_designator))

    return make_dicom_tag((0x0040, 0xA043), "SQ", [dataset])


def make_relationship_type(relationship_type):
    """
    Returns a "Relationship Type" Tag Element with the parameter given.
    """
    return make_dicom_tag((0x0040, 0xA010), "CS", relationship_type)


def make_content_sequence(content_sequence_dict):
    """
    Main method giving appropriate content sequence dataset
    using methods above for specific tags.

    TODO - Manipulation of value types COMPOSITE, SCOORD, TCOORD
    :param content_sequence_dict:
    :return: Appropriate content_sequence DICOM dataset
    """
    dataset = pydicom.Dataset()
    dataset.add(make_relationship_type(content_sequence_dict["RelationshipType"]))
    dataset.add(
        make_concept_name_code_sequence(
            content_sequence_dict["ConceptNameCodeSequence"]["CodeValue"],
            content_sequence_dict["ConceptNameCodeSequence"]["CodeMeaning"],
            content_sequence_dict["ConceptNameCodeSequence"]["CodingSchemeDesignator"],
        )
    )
    dataset.add(make_value_type(content_sequence_dict["ValueType"]))
    value_type = content_sequence_dict["ValueType"]
    value = content_sequence_dict.setdefault("Value", None)

    if value_type == "NUM" and "MeasurementUnitsCodeSequence" in content_sequence_dict.keys():
        value_type = "NUM_SEQUENCE"

    if value_type == 'TEXT':
        dataset.add(make_text_value(value))

    elif value_type == 'NUM':
        value_to_str = str(value)
        dataset.add(make_numeric_value(value_to_str[:16]))
        if len(value_to_str) > 16:
            dataset.add(make_floating_point_value(value))

    elif value_type == 'PNAME':
        dataset.add(make_person_name(value))

    elif value_type == 'DATE':
        dataset.add(make_date(value))

    elif value_type == 'DATETIME':
        dataset.add(make_datetime(value))

    elif value_type == 'UIDREF':
        dataset.add(make_uid_ref(value))

    elif value_type == "CODE":
        dataset.add(
            make_concept_code_sequence(
                content_sequence_dict["ConceptCodeSequence"]["CodeValue"],
                content_sequence_dict["ConceptCodeSequence"]["CodeMeaning"],
                content_sequence_dict["ConceptCodeSequence"]["CodingSchemeDesignator"],
            )
        )

        for content_sequence in list(content_sequence_dict["Value"] or []):
            dataset.add(
                make_dicom_tag(
                    (0x0040, 0xA730),  # this is a content sequence
                    "SQ",
                    [make_content_sequence(content_sequence)],
                )
            )

    elif value_type == "NUM_SEQUENCE":
        dataset.add(
            make_measured_value_sequence(
                value,
                content_sequence_dict["MeasurementUnitsCodeSequence"]["CodeMeaning"],
                content_sequence_dict["MeasurementUnitsCodeSequence"]["CodingSchemeDesignator"],
            )
        )

    elif value_type == "IMAGE":
        dataset.add(
            make_referenced_instance_sequence(
                [value["ReferencedSOPClassUID"]],
                [value["ReferencedSOPInstanceUID"]],
                [value["PurposeOfReferenceCodeSequence"]["CodeValue"]],
                [value["PurposeOfReferenceCodeSequence"]["CodeMeaning"]],
                [value["PurposeOfReferenceCodeSequence"]["CodeSchemeDesignator"]],
            )
        )

    elif value_type == "CONTAINER":
        dataset.add(
            make_continuity_content(content_sequence_dict["ContinuityOfContent"])
        )

        if "ContentSequence" not in dataset:
            dataset.ContentSequence = []

        for content_sequence in content_sequence_dict["Value"]:
            try:
                dataset.ContentSequence += [make_content_sequence(content_sequence)]

            except AttributeError:
                dataset.add(
                    make_dicom_tag(
                        (0x0040, 0xA730), "SQ", [make_content_sequence(content_sequence)]
                    )
                )

    return dataset


def make_reference_code_sequence_purpose(code_value, code_meaning, coding_scheme_designator):
    """
    Returns a "Purpose of Reference Code Sequence" Tag Element.
    Creates a dataset with the parameters given
    """
    dataset = pydicom.Dataset()
    dataset.add(make_code_value(code_value))
    dataset.add(make_code_meaning(code_meaning))
    dataset.add(make_coding_scheme_designator(coding_scheme_designator))

    return make_dicom_tag((0x0040, 0xA170), "SQ", [dataset])


def make_referenced_sop_class_uid(referenced_sop_class_uid):
    """
    Returns a "Referenced SOP Class UID" Tag Element with the parameter given.
    """
    return make_dicom_tag((0x0008, 0x1150), "UI", referenced_sop_class_uid)


def make_referenced_sop_instance_uid(referenced_sop_instance_uid):
    """
    Returns a "Referenced SOP Instance UID" Tag Element with the parameter given.
    """
    return make_dicom_tag((0x0008, 0x1155), "UI", referenced_sop_instance_uid)


def make_referenced_instance_sequence(
    referenced_sop_class_uids: List,
    referenced_sop_instance_uids: List,
    code_values: List,
    code_meanings: List,
    coding_scheme_designators: List,
):
    """
    Returns a "Referenced Instance Sequence" Tag Element.
    Creates datasets with the parameters given
    """
    datasets = []
    for i, instance_uid in enumerate(referenced_sop_instance_uids):
        dataset = pydicom.Dataset()
        dataset.add(make_referenced_sop_instance_uid(instance_uid))
        dataset.add(make_referenced_sop_class_uid(referenced_sop_class_uids[i]))
        dataset.add(
            make_reference_code_sequence_purpose(
                code_values[i], code_meanings[i], coding_scheme_designators[i]
            )
        )
        datasets.append(dataset)

    return make_dicom_tag((0x0008, 0x114A), "SQ", datasets)


def make_measured_value_sequence(numeric_value, units, coding_scheme_designator):
    """
    Returns a "Measured Value Sequence" Tag Element.
    Creates a dataset with the parameters given
    """
    dataset = pydicom.Dataset()
    value_to_str = str(numeric_value)

    dataset.add(make_numeric_value(value_to_str[:16]))
    if len(value_to_str) > 16:
        dataset.add(make_floating_point_value(numeric_value))

    dataset.add(make_measurement_units_code_sequence(units, coding_scheme_designator))

    return make_dicom_tag((0x0040, 0xA300), "SQ", [dataset])


def make_measurement_units_code_sequence(units, coding_scheme_designator):
    """
    Returns a "Measurement Units Code Sequence" Tag Element.
    Creates a dataset with the parameters given
    """
    dataset = pydicom.Dataset()
    dataset.add(make_code_value(units))
    dataset.add(make_code_meaning(units))
    dataset.add(make_coding_scheme_designator(coding_scheme_designator))

    return make_dicom_tag((0x0040, 0x08EA), "SQ", [dataset])
