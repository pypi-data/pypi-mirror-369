###############
# Note this file was intended to act as a converter
#   between a json and .py enum for the materials
# The json was manually built from the NIST source code
#   of their menu for material selection
# As it stands it may no longer be needed but is kept in
#   case it is needed in the future
###############

"""
Module for internal use only,
used to convert a raw json NIST dump to useful python
"""

import json


def generate_nist_material_enum():
    """
    Method used to convert the manually built NIST material
    name to value json file into a python file with an enum class.

    Returns
    -------
    None
    """
    # Open json file
    # Note this expects the file to be of type
    # { "material": int, "material2": int, ... }
    # It is also important that all symbols not accepted as
    # an ENUM key be manually stripped
    with open("data/material_lookup_key.json", encoding="utf-8") as file:
        materials = json.load(file)

    # Create the initial module docstring
    generated_content = (
        '"""\nContainer module for Enum classes used within NISTparser\n"""\n\n'
    )

    # Create the initial imports and class declaration
    generated_content += "from enum import Enum\n\n\n class NISTMaterials(Enum):\n"

    # Doctsring for the class
    generated_content += (
        '    """\n    Simple enum class listing NIST'
        'materials and respective URL index\n    """\n'
    )

    # Copy dict so we can alter
    materials_copy = materials.copy()

    for key, value in materials.items():
        # Replace space with underscore to be able to use as enum key
        # Make keys all uppercase to satisfy class constant name for pylint
        sanitized_key = key.replace(" ", "_")
        sanitized_key = sanitized_key.upper()
        materials_copy[sanitized_key] = materials_copy.pop(key)

        # Append to our string the enum key + value
        generated_content += f"    {sanitized_key} = {value}\n"

    # Print out to file
    with open("../materials_enum.py", "w", encoding="utf-8") as file:
        file.write(generated_content)


if __name__ == "__main__":
    # In case we wish to manually run this file
    generate_nist_material_enum()
