"""DICOM related stuff."""
from . import sr
from .reader import DicomReader, DicomSeries, DicomStudy
from .uid import generate_uid
from .utils import VR

__all__ = ["sr", "DicomReader", "DicomStudy", "DicomSeries", "generate_uid", "VR"]
