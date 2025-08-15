"""
A module intended to facilitate the loading and parsing of dicom files within a given,
and recursive, folder.
"""

import os
import warnings
from pathlib import Path
from typing import Generator, List, Union

import pydicom
from pydicom.errors import InvalidDicomError

from pygrpm.dicom.structures import DicomSeries, DicomStudy


# disabling name linting due to UID present in names
# pylint: disable=invalid-name
class DicomReader:
    """
    Master reader class to crawl through the directory and generate relevant
    DicomStudy and DicomSeries dataclasses
    """

    def __init__(self, folderpath: Union[str, bytes, os.PathLike], verbose: int = 0):
        self.data_path = Path(folderpath)
        self.verbose = verbose
        # ensure we have an actual directory
        if not self.data_path.is_dir():
            raise NotADirectoryError(self.data_path)

        self._studies: List[DicomStudy] = []
        self._study_uids: List[str] = []
        self.dicoms: List[pydicom.FileDataset] = []

    @property
    def studies_UID(self) -> List[Union[str, pydicom.uid.UID]]:
        """
        property method to return a list of all instances uid within the series dataclass
        @return: An similarly ordered list of instances UID
        """
        return [study.study_UID for study in self.studies]

    @property
    def studies(self) -> List[DicomStudy]:
        """
        Property method to get an explicit list of the obtained studies
        @return: A list of DicomStudy dataclasses for the found studies
        """
        if len(self._studies) == 0:
            self.build_dicom_list()
            self.build_studies()

        return self._studies

    def yield_dicoms(self) -> Generator[pydicom.FileDataset, None, None]:
        """
        Generator utilized to obtain the pydicom FileDatasets within the data folder
        """
        for root, folders, files in os.walk(self.data_path):  # pylint: disable=unused-variable
            for file in files:
                # If file is not a proper dicom it will be set to None
                my_file = Path(root) / file
                my_dicom = self.load_dcm(my_file)

                # Append dataset to master list if appropriate
                if my_dicom:
                    yield my_dicom

    def build_dicom_list(self) -> List[pydicom.FileDataset]:
        """
        Method used to navigate through the class folder, ensure the files are dicom,
        then append the dicoms to a master list for further processing
        @return: The list of dicom datasets
        """
        for my_dicom in self.yield_dicoms():
            self.dicoms.append(my_dicom)

        return self.dicoms

    def load_dcm(
        self, filepath: Union[str, os.PathLike]
    ) -> Union[pydicom.FileDataset, None]:
        """
        Simple wrapper method to cleanly handle non-dicom files within the provided folder
        @param filepath: path to the potential dicom file
        @return: The pydicom FileDataset is appropriate, otherwise None
        """
        try:
            return pydicom.read_file(filepath)
        except (InvalidDicomError, TypeError):
            if self.verbose > 0:
                print(f"File {filepath} was not a dicom file, skipping.")
            return None

    def build_studies(self) -> List[DicomStudy]:
        """
        Main method used to buildup all the studies and series from the given folder
        @return: A -> List of studies as obtained from the folder
        """
        # Initial sanity check and warning
        if len(self.dicoms) < 1:
            warnings.warn("Attempted to build study with no dicoms loaded.")

        for dcm in self.dicoms:
            # Generate or load current dicom's Study
            if len(self._studies) == 0 or dcm.StudyInstanceUID not in self._study_uids:
                study = self.make_study(dcm)

                # Add the study to the class
                self._studies.append(study)
                self._study_uids.append(dcm.StudyInstanceUID)
            else:
                # get proper study
                study = self.get_study(dcm.StudyInstanceUID)

            # Generate or load current dicom's Serie
            if len(study.series) == 0 or dcm.SeriesInstanceUID not in study.series_UID:
                series = self.make_series(dcm)
            else:
                series = study.get_series(dcm.SeriesInstanceUID)

            # Add instance in series if not exist
            series = self.add_instance_in_series(series, dcm)
            # Add or update series in study
            self.add_or_update_series_in_study(study, series)

        return self._studies

    @staticmethod
    def add_or_update_series_in_study(
        study: DicomStudy, series: DicomSeries
    ) -> DicomStudy:
        """
        Method will either append series to the study if it is not already present.
        Should the series already exist in the study it will be updated
        @param study: The DicomStudy to be updated
        @param series: The DicomSeries to place/update within the study
        @return: The updated DicomStudy
        """
        # check if this serie is already in the study
        existing_series = [s for s in study.series if s.series_UID == series.series_UID]

        if len(existing_series) > 0:
            # Determine position in list, and update
            idx = study.series_UID.index(series.series_UID)
            study.series[idx] = series
        else:
            # Append to lists if the series does not already exist
            study.series.append(series)
            study.series_UID.append(series.series_UID)

        return study

    @staticmethod
    def add_instance_in_series(
        series: DicomSeries, dicom: pydicom.FileDataset
    ) -> DicomSeries:
        """
        Method used to add the dicom instance into the series should it not already be present
        @param series: The DicomSeries to be updated
        @param dicom: The pydicom filedataset containing the dicom instance
        @return: The updated DataSeries
        """

        # Sanity checks, perhaps should not raise errors
        if dicom.Modality != series.modality:
            raise ValueError(
                f"Dicom modality does not correspond with series modality, "
                f"{dicom.filename}"
            )
        if dicom.SeriesInstanceUID != series.series_UID:
            raise ValueError(
                f"Dicom SeriesInstanceUID does not correspond with series UID, "
                f"{dicom.filename}"
            )
        if dicom.StudyInstanceUID != series.study_UID:
            raise ValueError(
                f"Dicom StudyInstanceUID does not correspond with study UID, "
                f"{dicom.filename}"
            )

        # Check if this instance is already in this series
        for instance in series.instances:
            if instance.SOPInstanceUID == dicom.SOPInstanceUID:
                # If the instance was already in the series, leave it alone
                return series

        # Update and return if it wasn't in there
        series.instances.append(dicom)
        return series

    def get_study(self, study_UID: Union[str, pydicom.uid.UID]) -> Union[DicomStudy, None]:
        """
        Helper method to obtain a DicomStudy class from its StudyInstanceUID
        @param study_UID: StudyInstanceUID
        @return: The DicomStudy dataclass matching the provided UID
        """
        for study in self.studies:
            if study.study_UID == study_UID:
                return study

        return None

    def get_series(self, study: Union[DicomStudy, str, pydicom.uid.UID],
                   series_UID: Union[str, pydicom.uid.UID]) -> Union[DicomSeries, None]:
        """
        Helper method to obtain a DicomSeries class from its DicomStudy
        @param study: The reference DicomStudy dataclass or associated UID
        @param series_UID: SeriesInstanceUID
        @return: The DicomSeries dataclass matching the provided UID
        """
        if type(study) in [str, pydicom.uid.UID]:
            study = self.get_study(study)

        for series in study.series:
            if series.series_UID == series_UID:
                return series

        return None

    @staticmethod
    def make_study(dicom: pydicom.FileDataset) -> DicomStudy:
        """
        Method to create a DicomStudy dataclass based on the provided dicom dataset
        @param dicom: The reference dicom dataset
        @return: The DicomStudy dataclass
        """
        study = DicomStudy(
            study_UID=dicom.StudyInstanceUID,
            patientID=dicom.PatientID,
            series=[],
            reference_folder_paths=[Path(dicom.filename).parents[0]],
        )

        return study

    @staticmethod
    def make_series(dicom: pydicom.FileDataset) -> DicomSeries:
        """
        Method to create a DicomSeries dataclass based on the provided dicom dataset
        @param dicom: The reference dicom dataset
        @return: The DicomSeries dataclass
        """
        series = DicomSeries(
            series_UID=dicom.SeriesInstanceUID,
            study_UID=dicom.StudyInstanceUID,
            patientID=dicom.PatientID,
            modality=dicom.Modality,
            instances=[dicom],
            reference_folder_path=Path(dicom.filename).parents[0],
        )

        return series

    def save_by_study(self, save_path: os.PathLike, save_by_series: bool = True,
                      modality_prefix: bool = True) -> None:
        """
        Utility method to save DICOM data by studies (and series)
        :param save_path: Root save folder
        :param save_by_series: True to save each series in its own subfolder
        :param modality_prefix: Include or not the series modality in the folder
        name (only active with `save_by_series`)
        """
        # Create root save path if needed
        save_path = Path(save_path)
        save_path.mkdir(parents=True, exist_ok=True)

        if len(self.studies) == 0:
            print("No studies found, aborting save.")
            return

        for study in self.studies:
            # Store each study in their own folder
            study_path = save_path / study.study_UID
            study_path.mkdir(exist_ok=True)

            for series in study.series:
                # If save_by_series, then create a sub-folder for every series
                # If not, then everything gets dumped into the study folder
                if save_by_series:
                    if modality_prefix:
                        series_path = study_path / f"{series.modality}_{series.series_UID}"
                    else:
                        series_path = study_path / series.series_UID
                else:
                    series_path = study_path
                series_path.mkdir(exist_ok=True)

                for instance in series.instances:
                    old_filepath = Path(instance.filename)

                    # If there's no suffix (.dcm, .ima, etc), then just add .dcm
                    # Although not necessary, ods are it would be preferred
                    if old_filepath.suffix == '':
                        old_filepath = old_filepath.parent / (old_filepath.name + ".dcm")

                    instance.save_as(series_path / old_filepath.name)
