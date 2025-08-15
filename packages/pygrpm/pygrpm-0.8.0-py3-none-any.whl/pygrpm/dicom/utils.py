"""
Utility functions and enumeration classes for manipulation of DICOM tags.

Pydicom VR typings reference
class VR(Enum):
    List of appropriate python types for DICOM VR, as used in pydicom 2.4.4 to SET values
    See https://pydicom.github.io/pydicom/stable/guides/element_value_types.html
    It should be noted thatevery field also accepts empty values
    AE = str
    AS = str
    AT = Tag
    CS = str
    DA = str
    DS = Union[str, float, int]
    DT = str
    FL = float
    FD = float
    IS = Union[str, int]
    LO = str
    LT = str
    OB = bytes
    OD = bytes
    OF = bytes
    OL = bytes
    OV = bytes
    OW = bytes
    PN = str
    SH = str
    SL = int
    SQ = list
    SS = int
    ST = str
    SV = int
    TM = str
    UC = str
    UI = str
    UL = int
    UN = bytes
    UR = str
    US = int
    UT = str
    UV = int
"""

from enum import Enum


class VR(Enum):
    """
    List of value representations, as used in pydicom 2.4.4.
    See https://pydicom.github.io/pydicom/stable/guides/element_value_types.html
    """
    APPLICATION_ENTITY = "AE"
    AE = "AE"
    AGE_STRING = "AS"
    AS = "AS"
    ATTRIBUTE_TAG = "AT"
    AT = "AT"
    CODE_STRING = "CS"
    CS = "CS"
    DATE = "DA"
    DA = "DA"
    DECIMAL_STRING = "DS"
    DS =  "DS"
    DATE_TIME = "DT"
    DT = "DT"
    FLOATING_POINT_SINGLE = "FL"
    FL = "FL"
    FLOATING_POINT_DOUBLE = "FD"
    FD = "FD"
    INTEGER_STRING = "IS"
    IS = "IS"
    LONG_STRING = "LO"
    LO = "LO"
    LONG_TEXT = "LT"
    LT = "LT"
    OTHER_BYTE = "OB"
    OB = "OB"
    OTHER_DOUBLE = "OD"
    OD = "OD"
    OTHER_FLOAT = "OF"
    OF = "OF"
    OTHER_LONG = "OL"
    OL = "OL"
    OTHER_64_BIT_VERY_LONG = "OV"
    OV = "OV"
    OTHER_WORD = "OW"
    OW = "OW"
    PERSON_NAME = "PN"
    PN = "PN"
    SHORT_STRING = "SH"
    SH = "SH"
    SIGNED_LONG = "SL"
    SL = "SL"
    SEQUENCE_OF_ITEMS = "SQ"
    SQ = "SQ"
    SIGNED_SHORT = "SS"
    SS = "SS"
    SHORT_TEXT = "ST"
    ST = "ST"
    SIGNED_64_BIT_VERY_LONG = "SV"
    SV = "SV"
    TIME = "TM"
    TM = "TM"
    UNLIMITED_CHARACTERS = "UC"
    UC = "UC"
    UNIQUE_IDENTIFIER = "UI"
    UI = "UI"
    UNSIGNED_LONG = "UL"
    UL = "UL"
    UNKNOWN = "UN"
    UN = "UN"
    URI_URL = "UR"
    UR = "UR"
    UNSIGNED_SHORT = "US"
    US = "US"
    UNLIMITED_TEXT = "UT"
    UT = "UT"
    UNSIGNED_64_BIT_VERY_LONG = "UV"
    UV = "UV"
