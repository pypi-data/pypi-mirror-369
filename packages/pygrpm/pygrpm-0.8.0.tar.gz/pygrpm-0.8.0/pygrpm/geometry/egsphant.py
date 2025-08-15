"""
Module used to convert volumes into egsphant format
"""
import json
import os
from pathlib import Path
from typing import Dict, Sequence, Union

import numpy as np

# Global list of characters for the material assignment
CHARACTERS = (
    r"123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz"
)

MATERIAL_DICTIONARIES = {
    "CT01": Path(os.path.dirname(__file__)) / "data/CT01_materials.json"
}


class Egsphant:
    """
    Class used to take a volumetric numpy array along with physical center coordinates and
    voxel spacing values to generate an egsphant file of the volume
    """

    # pylint: disable=R0913, R0902
    def __init__(
            self,
            volume: np.ndarray,
            spacings: np.ndarray,
            center: np.ndarray,
            materials: Dict,
    ) -> None:
        """
        Class used to convert a provided 3D numpy array into an egsphant volume
        @param volume: A 3D numpy array who's values dictate material information
        @param spacings: A sequence three values representing spacing in each axis
        @param center: A sequence of three values representing the volume's center, such as
        (0, 0, 0), (-21, -39, 256), etc...
        @param materials: Dictionary with material name, value ranges, and density
        @param slice_axis: Axis where slices are located for a 3-D image (usually 0 or 2).
            Defaults to 0.
        """
        self.volume: np.ndarray = volume
        self.spacings: np.ndarray = spacings
        self.center: np.ndarray = center
        self.materials: Dict = materials

        # Generate base volumes for materials and density
        self.material_volume: np.ndarray = np.chararray(self.volume.shape, unicode=True)
        self.density_volume: np.ndarray = np.zeros_like(self.volume, dtype=np.float16)

        self.header: str = ""
        self.voxel_position_string: str = ""
        self.material_string: str = ""
        self.density_string: str = ""

        self.built: bool = False

    def __str__(self):
        return self.content

    def build(self, precision=3):
        """
        Generic build method to generate and format the egsphant string as desired
        @return: None
        """
        self._trim_materials()
        self.generate_headers()
        self.generate_voxel_positions(precision)
        self.generate_volumes_string()

        self.built = True

    @property
    def content(self) -> str:
        """
        The full egsphant string representation, headers and volumes included
        @return: The egsphant information
        """
        if not self.built:
            self.build()

        return self.header + self.voxel_position_string + "\n" \
               + self.material_string + "\n\n" + self.density_string + "\n"

    def write_to_file(self, filepath: Union[str, os.PathLike]) -> None:
        """
        Utility method to quickly save the egsphant string to a given filepath
        @param filepath: Filepath to save the contents
        @return: None
        """
        with open(filepath, "w", encoding="utf8") as file:
            file.write(self.content)

    def _trim_materials(self) -> None:
        """
        Method to truncate material dictionaries to the bounds of the current volume
        """

        # Dictionary copy to edit while looping
        materials_copy = self.materials.copy()
        for material_name, details in self.materials.items():
            interval = details["value_interval"]

            # This is rather slow but makes for cleaner output
            # Returns true if nothing in the array is within the given interval
            if np.all((self.volume < interval[0]) | (self.volume > interval[1])):
                del materials_copy[material_name]

        self.materials = materials_copy

    def generate_headers(self) -> str:
        """
        Method used to generate egsphant headers as a single string based on the following format:
            Number of materials
            Name_of_material_1 /n
            Name_of_material_2 /n
            ....
            Name_of_material_n /n
            "0" * # materials (example if you have 3 materials this line will be 000)
            Shape of the volume X Y Z
        @return: Returns headers as a string
        """
        header = ""

        # Number of materials
        header += str(len(self.materials)) + "\n"

        # List of materials
        for name in self.materials.keys():
            header += f"{name}\n"

        # 0 series
        header += ("0 " * len(self.materials)) + "\n"

        # Volume shape (put slices in last axis by standard)
        vol_shape = np.swapaxes(self.volume, 0, -1).shape
        header += f"{vol_shape[0]} {vol_shape[1]} {vol_shape[2]}\n"

        self.header = header
        return self.header

    def _generate_dimensions(self) -> tuple:
        """
        Given the internal sequence of spacings, shape, and length,
        generate physical coordinates for every voxel
        @return: A tuple of arrays containing all voxel positions
        """
        shape = self.volume.swapaxes(0, -1).shape
        steps = np.array(self.spacings)

        # Determine half-lengths since we generate with respect to the center point
        vol_lengths = np.array(shape) * steps
        half_lengths = vol_lengths / 2

        start = (self.center - half_lengths) - (steps / 2)
        end = half_lengths + self.center + (steps / 2)

        # Make a quick and dirty check to see if dimensions are even/odd
        odd_shape = ~np.array(shape) % 2

        # If we have even number of slices, our "center pixel" doesn't exist
        # Add a half pixel offset to compensate
        start += odd_shape * (steps / 2)  # Equivalent to if(odd) {apply addition}
        end += odd_shape * (steps / 2)

        x_spacing = np.linspace(start[0], end[0] + steps[0], shape[0] + 1)
        y_spacing = np.linspace(start[1], end[1] + steps[1], shape[1] + 1)
        z_spacing = np.linspace(start[2], end[2], shape[2] + 1)

        return x_spacing, y_spacing, z_spacing

    def generate_voxel_positions(self, precision=3) -> str:
        """
        Generates and stringifies voxel positions for the volumes
        @param precision: Decimal precision for each voxel position
        @return: stringified voxel positions
        """
        pos_arrays = self._generate_dimensions()

        # Convert arrays of values to string, with N decimals and a space as separator
        # Remove garbage values on start and end of arrays
        pos_strings = [
            np.array2string(
                pos, precision=precision, separator=" ", max_line_width=99999,
                floatmode='fixed', suppress_small=True
            )[1:-1]
            for pos in pos_arrays
        ]
        # array2string leaves "nice" spacing which yield extra whitespace. Trim that to always be 1
        pos_strings = [' '.join(mystring.split()) for mystring in pos_strings]

        self.voxel_position_string = "\n".join(pos_strings)
        return self.voxel_position_string

    def _populate_volumes(self) -> None:
        """
        Assigns material and density values to associated volumes
        based on materials dictionary initial volume values
        """
        for idx, details in enumerate(self.materials.values()):
            # For every material, check all volume values that fall within the value_intervals
            # For every matched position, update the material and density volume accordingly
            # Materials get populated from the characters array, and density from the json density
            self.material_volume[
                (self.volume >= details["value_interval"][0])
                & (self.volume <= details["value_interval"][1])
                ] = CHARACTERS[idx]
            self.density_volume[
                (self.volume >= details["value_interval"][0])
                & (self.volume <= details["value_interval"][1])
                ] = details["density"]

    def generate_volumes_string(self) -> str:
        """
        Method used to stringify the density and material volumes belonging to this class
        @return: stringified, and concatenated, strings representing the volumes
        """
        # Make sure we properly populate both volumes
        self._populate_volumes()

        self.material_string = "\n\n".join(
            "\n".join("".join(f"{x}" for x in y) for y in z)
            for z in self.material_volume
        )

        self.density_string = "\n\n".join(
            # pylint: disable=C0209
            # Speed difference of % formatting is very much needed
            "\n".join(" ".join("%0.5f" % x for x in y) for y in z)
            for z in self.density_volume
        )

        return self.material_string + "\n" + self.density_string


def _validate_inputs(volume, spacings, center) -> None:
    """
    Helper method to validate user inputs
    @param volume: A 3D numpy array who's values dictate material information
    @param spacings: A sequence three values representing spacing in each axis
    @param center: A sequence of three values representing the volume's center
    """
    if volume.ndim != 3:
        raise ValueError(
            f"Provided volume was not 3 dimensional, found {volume.ndim}."
        )

    if len(spacings) != 3:
        raise ValueError(
            f"Must have spacing values for 3 dimensions, found for {len(spacings)}"
        )

    if len(center) != 3:
        raise ValueError(
            f"Must have center values for 3 dimensions, found for {len(center)}"
        )


def _ensure_materials_dict(materials: Union[str, Dict]) -> Dict:
    """
    Helper method to ensure proper materials assignment to the Egsphant class
    @param materials: The desired materials dictionary, or filename
    @return: The associated materials dictionary
    """
    # Assign the proper values to internal self.materials dictionary
    if isinstance(materials, str):
        if materials in MATERIAL_DICTIONARIES:
            # Open the jsons with the materials and open it in dictionary
            with open(MATERIAL_DICTIONARIES[materials], "r", encoding="utf8") as json_file:
                return json.load(json_file)
        else:
            raise ValueError(
                f"Provided dictionary name was not an accepted value."
                f"Current values are {MATERIAL_DICTIONARIES.keys()}"
            )
    elif isinstance(materials, dict):
        return materials
    else:
        raise ValueError("Provided materials was neither a string nor dictionary.")


# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
def make_egsphant_from_numpy(volume: np.ndarray,
                             spacings: Sequence,
                             center: Sequence,
                             materials: Union[str, Dict],
                             precision: int = 3,
                             slice_axis: int = 0) -> Egsphant:
    """
    Utility method to build an Egsphant class given numpy content
    @param volume: A 3D numpy array who's values dictate material information
    @param spacings: A sequence three values representing spacing in each axis
    @param center: A sequence of three values representing the volume's center, such as
    (0, 0, 0), (-21, -39, 256), etc...
    @param materials: Either a string representing predefined material assignments
            or a custom dictionary with material name, value ranges, and density
    @param precision: The decimal precision for voxel positions
    @param slice_axis: Axis where slices are located for a 3-D image (usually 0 or 2).
        Defaults to 0.
    @return: The Egsphant class structured on the provided input
    """
    # ValueError will be raised here if inputs are unacceptable
    _validate_inputs(volume, spacings, center)

    # Make sure we have slices in position 0
    volume = volume.swapaxes(0, slice_axis)
    center = np.array(center)
    spacings = np.array(spacings)

    materials = _ensure_materials_dict(materials)

    egsphant = Egsphant(volume, spacings, center, materials)
    egsphant.build(precision=precision)

    return egsphant
