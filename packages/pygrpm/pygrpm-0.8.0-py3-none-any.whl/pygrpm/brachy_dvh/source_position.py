"""
Module: source_position

This module defines the SourcePosition class, which represents a source position in 3D space,
typically used in radiation therapy planning such as HDR (High Dose Rate) or LDR 
(Low Dose Rate) brachytherapy.

It includes information about the spatial position, orientation, timing weight, catheter index,
and a relative location along a catheter path.
"""
from typing import Tuple


class SourcePosition:
    """
    Represents a source dwell position within a catheter for brachytherapy applications.
    """

    def __init__(
            self,
            position: Tuple[float, float, float],
            direction: Tuple[float, float, float] = None,
            weight: float = -1.0,
            catheter_index: int = -1,
            relative_position: float = -1):
        """Initializes a new SourcePosition instance."""
        self._position = position
        self._direction = direction
        # weight should be in seconds for HDR and in *** for LDR
        self._weight = weight
        self._catheter_index = catheter_index
        self._relative_position = relative_position

    @property
    def position(self) -> Tuple[float, float, float]:
        """
        Returns the 3D coordinates of the source position.
        """
        return self._position

    @property
    def direction(self) -> Tuple[float, float, float]:
        """
        Returns the orientation vector of the source, if defined
        """
        return self._direction

    @property
    def weight(self) -> float:
        """
        Returns the dwell time or intensity weight of the source.
        """
        return self._weight

    @property
    def catheter_index(self) -> int:
        """
        Returns the index of the catheter
        """
        return self._catheter_index

    @property
    def relative_position(self) -> float:
        """
        Returns the relative position along the catheter path.
        """
        return self._relative_position

    @direction.setter
    def direction(self, new_direction: Tuple[float, float, float]):
        """
        Sets a new direction vector for the source.
        """
        self._direction = new_direction
