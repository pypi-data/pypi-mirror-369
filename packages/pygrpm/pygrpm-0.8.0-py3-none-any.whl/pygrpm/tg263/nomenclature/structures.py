# coding: utf-8
# author: Gabriel Couture
# revision: Pierre-Luc Asselin
"""Definition of functions associated with structures"""
import re
from typing import Dict, List

from ._dictionary import ALLOWED_STRUCTURES


def is_structure_valid(structure: Dict):
    """Verifies that parameter dictionary is a valid structure.
    Returns a boolean and an error log accordingly.
    Criterias used to determine the validity of structures
    are based on the recommendations of the American Association of Physicists
    in Medicine in the TG263 report.
    Source: https://www.aapm.org/pubs/reports/RPT_263_Supplemental/"""

    # Checks for all required elements in structure
    req_elem = (
        "tg263PrimaryName",
        "tg263ReverseOrderName",
        "targetType",
        "majorCategory",
        "minorCategory",
        "anatomicGroup",
        "description",
        "fmaid",
        "nCharacters",
    )

    if not all(elem in structure for elem in req_elem):
        return False, "Missing requisite element(s)"

    # Verifies types of required elements in structure
    for key in req_elem[:-2]:
        if not isinstance(structure[key], str):
            if structure[key] is not None:
                return False, "Wrong element type. String expected"

    for key in req_elem[-2:]:
        if not isinstance(structure[key], int):
            if structure[key] is not None:
                return False, "Wrong element type. Integer expected"

    # Checks for illegal characters
    chars = set("""<>:"'/'\'|?*#$""")
    for elem in structure.values():
        if any((c in chars) for c in str(elem)):
            return False, """Illegal characters found (<>:"'/'\'|?*#$)"""

    # If all verifications passed, return true
    return True, "Structure is valid"


def is_structure_name_allowed(structure_name: str) -> bool:
    """Finds if parameter structure name is found in tg263 reference
    Returns a boolean accordingly."""
    for allowed_structure in ALLOWED_STRUCTURES:
        if allowed_structure["tg263PrimaryName"] == structure_name:
            return True

    return False


def find_structures(stru_name: str) -> List:
    """Finds if parameter structure name is found in tg263 reference
    Returns all associated names in a list."""

    matches = []

    for allowed_stru in ALLOWED_STRUCTURES:
        if re.search(stru_name, allowed_stru["tg263PrimaryName"]) is not None:
            matches.append(allowed_stru)

    return matches


def print_structure_info(allowed_structure: Dict) -> None:
    """Prints all associated information of the structure,
    only if structure is valid"""
    validation, log = is_structure_valid(allowed_structure)

    if validation:
        print("\n\nFMAID: ", str(allowed_structure["fmaid"]))
        print("\nPrimary Name: ", allowed_structure["tg263PrimaryName"])
        print("Reverse Order Name: ", allowed_structure["tg263ReverseOrderName"])
        print("\nTarget Type: ", allowed_structure["targetType"])
        print("Anatomic Group: ", allowed_structure["anatomicGroup"])
        print("Major Category: ", allowed_structure["majorCategory"])
        print("Minor Category: ", allowed_structure["minorCategory"])
        print("\nDescription: ", allowed_structure["description"])

    else:
        print("Invalid structure! Validation error log:\n", log)
