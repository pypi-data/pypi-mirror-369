"""
Module: dvh

This module defines the DVH (Dose Volume Histogram) class, which provides methods to
calculate and manage differential and cumulative DVHs from dose distributions and voxel volumes.

It supports conversion to `dicompylercore` DVH objects for interoperability with other tools.

"""

from typing import Sequence, Union

import dicompylercore.dvh
import numpy as np


class DVHError(Exception):
    """Custom exception class for DVH-related errors."""
    pass


class DVH:
    """
    Represents a Dose Volume Histogram (DVH), supporting both differential and cumulative forms.
    """

    MIN_NUMBER_OF_BINS = 100
    MAX_NUMBER_OF_BINS = 2000
    ZERO = 0

    def __init__(self, number_of_bins: int, max_dose: float):
        if number_of_bins < self.MIN_NUMBER_OF_BINS or number_of_bins > self.MAX_NUMBER_OF_BINS:
            raise DVHError(
                f"Number of bins {number_of_bins} is out of range "
                f"[{self.MIN_NUMBER_OF_BINS}, {self.MAX_NUMBER_OF_BINS}]"
            )

        if max_dose < self.ZERO:
            raise DVHError("Max dose is negative")

        self._number_of_bins = number_of_bins
        self._max_dose = max_dose
        self._bin_edges = None
        self._differential_dvh = None
        self._cumulative_dvh = None

    @property
    def differential_dvh(self) -> np.array:
        """
        Returns the differential DVH (volume per dose bin).
        """
        return self._differential_dvh

    @property
    def cumulative_dvh(self) -> np.array:
        """
        Returns the cumulative DVH (volume receiving at least a given dose).
        """
        return self._cumulative_dvh

    @property
    def bin_edges(self) -> np.array:
        """
        Returns the bin edges for the histogram (dose intervals).
        """
        return self._bin_edges

    def get_dicompyler_dvh_instance_differential(self) -> dicompylercore.dvh.DVH:
        """
        Returns a dicompylercore DVH object for the differential DVH.
        """
        return dicompylercore.dvh.DVH(
            self._differential_dvh,
            self._bin_edges,
            dvh_type="differential",
            dose_units='gy',
            volume_units='cm3'
        )

    def get_dicompyler_dvh_instance_cumulative(self) -> dicompylercore.dvh.DVH:
        """
        Returns a dicompylercore DVH object for the cumulative DVH.
        """
        return dicompylercore.dvh.DVH(
            self._cumulative_dvh,
            self._bin_edges,
            dvh_type="cumulative",
            dose_units='gy',
            volume_units='cm3'
        )

    def calculate(
            self,
            dose_points: Sequence,
            voxel_volume: Union[float, Sequence]
    ) -> None:
        """
        Computes the differential and cumulative DVHs based on dose points and voxel volumes.
        """
        dose_points = np.array(dose_points)
        voxel_volume = np.array(voxel_volume)

        if np.any(dose_points < self.ZERO):
            raise DVHError("Dose points contains negative values")

        if np.any(voxel_volume < self.ZERO):
            raise DVHError("Voxel volume contains negative values")

        new_dose_points = np.copy(dose_points)
        new_dose_points[np.where(new_dose_points > self._max_dose)[0]] = self._max_dose

        self._differential_dvh, self._bin_edges = np.histogram(
            new_dose_points,
            bins=self._number_of_bins,
            range=(0.0, self._max_dose)
        )
        self._differential_dvh = self._differential_dvh.astype(np.float64)

        if voxel_volume.shape != ():
            if len(voxel_volume) != len(new_dose_points):
                raise DVHError("Shape of dose points array and voxel volume array should match")

        self._differential_dvh *= voxel_volume
        self._cumulative_dvh = np.flip(np.cumsum(np.flip(self._differential_dvh)))
