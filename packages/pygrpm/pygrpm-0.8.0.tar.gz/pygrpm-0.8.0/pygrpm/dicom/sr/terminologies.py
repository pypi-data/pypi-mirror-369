"""Terminologies sub module"""
import csv
import os
from typing import Dict

DATA_DIRECTORY = f'{os.path.dirname(os.path.realpath(__file__))}/data'
DICOM_TERMINOLOGIES_PATH = f'{DATA_DIRECTORY}/DCM_2023c_20230704.csv'


class DicomTerminologies:
    """This class is a singleton that load the DICOM terminologies a single time

    The terminologies can be found at : https://bioportal.bioontology.org/ontologies/DCM
    """

    def __init__(self, terminologies_path: str):
        self.terminologies_path = terminologies_path
        self._notations = None

    @property
    def notations(self) -> Dict[str, str]:
        """DCM Notations, instantiated only once"""
        if self._notations is None:
            with open(self.terminologies_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader, None)  # Skip the header

                self._notations = {row[37]: row[39] for row in reader}

        return self._notations

    def find_code_meaning(self, notation: str) -> str:
        """Find the code meaning from notation code"""
        try:
            return self.notations[notation]
        except KeyError as exc:
            raise ValueError(f'{notation=} not found in DICOM terminologies') from exc


dicom_terminologies = DicomTerminologies(DICOM_TERMINOLOGIES_PATH)
