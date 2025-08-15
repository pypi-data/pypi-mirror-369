# code: utf-8
# author: Pierre-Luc Asselin, April 2023
# Based on module coded by Samuel Ouellet, March 2022

"""
Class and subclasses managing content sequence generation
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class DicomCodeSequence:
    """
    Underclass that respects the ConceptNameCodeSequence and ConceptCodeSequence accepted definition
    """

    code_value: str
    coding_scheme_designator: str
    code_meaning: str

    def as_dict(self):
        """
        Assembles a dictionary with:
        - "Code Value" tag
        - "Coding Scheme Designator" tag
        - "Code Meaning" tag
        """
        return {
            "CodeValue": self.code_value,
            "CodingSchemeDesignator": self.coding_scheme_designator,
            "CodeMeaning": self.code_meaning,
        }


@dataclass
class DicomCode:
    """
    Wrapper used to generate the dictionary for SR type CODE
    """

    relationship_type: Any
    concept_name_code_sequence: Any
    concept_code_sequence: Any
    value: Any

    def __post_init__(self):
        self.value_type = "CODE"

        if self.value is not None:
            if not isinstance(self.value, list):
                self.value = [self.value]

    def as_dict(self):
        """
        Assembles a dictionary with:
        - "Relationship Type" tag
        - "Value Type" tag
        - "Value" tag
        - "Concept Name Code Sequence" tag
        - "Concept Code Sequence" tag
        """
        dict_concept_name_code_sequence = (
            self.concept_name_code_sequence.as_dict()
        )
        dictionary = {
            "RelationshipType": self.relationship_type,
            "ValueType": self.value_type,
            "ConceptNameCodeSequence": dict_concept_name_code_sequence,
        }
        if self.concept_code_sequence is not None:
            dict_concept_code_sequence = self.concept_code_sequence.as_dict()
            dictionary["ConceptCodeSequence"] = dict_concept_code_sequence

        if self.value is not None:
            value = []
            for i in self.value:
                temp_dict = i.as_dict()
                value.append(temp_dict)

            dictionary["Value"] = value
        return dictionary


@dataclass
class DicomContainer:
    """
    Wrapper used to generate the dictionary for SR type CONTAINER
    """

    relationship_type: Any
    value: Any
    concept_name_code_sequence: Any
    continuity_content: Any

    def __post_init__(self):
        self.value_type = "CONTAINER"

        if isinstance(self.value, dict):
            self.value = [self.value]

    def as_dict(self):
        """
        Assembles a dictionary with:
        - "Relationship Type" tag
        - "Value Type" tag
        - "Value" tag
        - "Concept Name Code Sequence" tag
        - "Continuity of Content" tag
        """
        if isinstance(self.value, list):
            value = []
            for i in self.value:
                if isinstance(i, dict):
                    value.append(i)
                else:
                    temp_dict = i.as_dict()
                    value.append(temp_dict)
        else:
            if not isinstance(self.value, (float, int, str, list, dict)):
                value = [self.value.as_dict()]
            else:
                value = self.value

        if isinstance(self.concept_name_code_sequence, dict):
            dict_concept_name_code_sequence = self.concept_name_code_sequence
        else:
            dict_concept_name_code_sequence = (
                self.concept_name_code_sequence.as_dict()
            )
        dictionary = {
            "ValueType": self.value_type,
            "Value": value,
            "ConceptNameCodeSequence": dict_concept_name_code_sequence,
            "ContinuityOfContent": self.continuity_content,
        }
        if self.relationship_type is not None:
            dictionary["RelationshipType"] = self.relationship_type
        return dictionary


@dataclass
class DicomText:
    """
    Wrapper used to generate the dictionary for SR type TEXT
    """

    relationship_type: Any
    value: Any
    concept_name_code_sequence: Any

    def __post_init__(self):
        self.value_type = "TEXT"

        if isinstance(self.value, dict):
            self.value = [self.value]

    def as_dict(self):
        """
        Assembles a dictionary with:
        - "Relationship Type" tag
        - "Value Type" tag
        - "Value" tag
        - "Concept Name Code Sequence" tag
        """
        if isinstance(self.value, list):
            value = []
            for i in self.value:
                temp_dict = i.as_dict()
                value.append(temp_dict)
        else:
            if not isinstance(self.value, (float, int, str, list)):
                value = [self.value.as_dict()]
            else:
                value = self.value
        dict_concept_name_code_sequence = (
            self.concept_name_code_sequence.as_dict()
        )
        dictionary = {
            "RelationshipType": self.relationship_type,
            "ValueType": self.value_type,
            "Value": value,
            "ConceptNameCodeSequence": dict_concept_name_code_sequence,
        }
        return dictionary


@dataclass
class DicomNum:
    """
    Wrapper used to generate the dictionary for SR type NUM
    """

    relationship_type: Any
    concept_name_code_sequence: Any
    measurement_units_code_sequence: Any
    value: Any

    def __post_init__(self):
        self.value_type = "NUM"

    def as_dict(self):
        """
        Assembles a dictionary with:
        - "Relationship Type" tag
        - "Value Type" tag
        - "Value" tag
        - "Concept Name Code Sequence" tag
        - "Concept Code Sequence" tag
        """
        dict_concept_name_code_sequence = (
            self.concept_name_code_sequence.as_dict()
        )
        dictionary = {
            "RelationshipType": self.relationship_type,
            "ValueType": self.value_type,
            "ConceptNameCodeSequence": dict_concept_name_code_sequence,
        }
        if self.measurement_units_code_sequence is not None:
            dict_measurement_units_code_sequence = (
                self.measurement_units_code_sequence.as_dict()
            )
            dictionary[
                "MeasurementUnitsCodeSequence"
            ] = dict_measurement_units_code_sequence
        if self.value is not None:
            dictionary["Value"] = self.value

        return dictionary
