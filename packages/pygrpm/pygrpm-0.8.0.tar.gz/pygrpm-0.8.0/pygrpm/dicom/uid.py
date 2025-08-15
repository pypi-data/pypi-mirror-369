"""UID Generation module"""
from typing import List, Optional

from pydicom import uid


def generate_uid(entropy_sources: Optional[List[str]] = None) -> uid.UID:
    """Generate a unique DICOM UID with the GRPM prefix.

    Parameters
    ----------
    entropy_sources
        The GRPM prefix will be appended with a SHA512 hash of the given list
        which means the result is deterministic and should make the original
        data unrecoverable.

    Returns
    -------
    str
        A DICOM UID of up to 64 characters.

    """
    return uid.generate_uid(prefix=GRPM_PREFIX, entropy_srcs=entropy_sources)


GRPM_PREFIX: str = "1.2.826.0.1.3680043.10.424."
