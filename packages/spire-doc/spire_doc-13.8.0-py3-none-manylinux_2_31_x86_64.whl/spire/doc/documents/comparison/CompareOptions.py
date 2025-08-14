from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.doc.common import *
from spire.doc import *
from ctypes import *
import abc

class CompareOptions(SpireObject):
    """
    Document comparison parameter settings.
    """
    @dispatch
    def __init__(self):
        """
        Initializes a new instance of the CompareOptions class.
        """
        GetDllLibDoc().CompareOptions_CreateCompareOptions.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().CompareOptions_CreateCompareOptions,)
        super(CompareOptions, self).__init__(intPtr)

    @property
    def IgnoreFormatting(self)->bool:
        """
        Gets or sets a value indicating whether to ignore format comparisons when comparing documents.
        The default is false.
        """
        GetDllLibDoc().CompareOptions_get_IgnoreFormatting.argtypes=[c_void_p]
        GetDllLibDoc().CompareOptions_get_IgnoreFormatting.restype=c_bool
        ret = CallCFunction(GetDllLibDoc().CompareOptions_get_IgnoreFormatting,self.Ptr)
        return ret

    @IgnoreFormatting.setter
    def IgnoreFormatting(self, value:bool):
        """
        Sets a value indicating whether to ignore format comparisons when comparing documents.
        """
        GetDllLibDoc().CompareOptions_set_IgnoreFormatting.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibDoc().CompareOptions_set_IgnoreFormatting,self.Ptr, value)

    @property

    def TextCompareLevel(self)->'TextDiffMode':
        """

        """
        GetDllLibDoc().CompareOptions_get_TextCompareLevel.argtypes=[c_void_p]
        GetDllLibDoc().CompareOptions_get_TextCompareLevel.restype=c_int
        ret = CallCFunction(GetDllLibDoc().CompareOptions_get_TextCompareLevel,self.Ptr)
        objwraped = TextDiffMode(ret)
        return objwraped

    @TextCompareLevel.setter
    def TextCompareLevel(self, value:'TextDiffMode'):
        GetDllLibDoc().CompareOptions_set_TextCompareLevel.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibDoc().CompareOptions_set_TextCompareLevel,self.Ptr, value.value)
