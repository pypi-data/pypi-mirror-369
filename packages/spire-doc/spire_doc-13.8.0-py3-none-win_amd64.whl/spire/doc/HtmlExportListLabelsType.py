from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.doc.common import *
from spire.doc import *
from ctypes import *
import abc

class HtmlExportListLabelsType(Enum):
    """
    Specifies type of the Header/Footer.

    """
    Auto = 0
    InlineText = 1
    HtmlTags = 2

