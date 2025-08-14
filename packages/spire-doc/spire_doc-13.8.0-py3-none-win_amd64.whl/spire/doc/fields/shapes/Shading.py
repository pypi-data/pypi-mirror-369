from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.doc.common import *
from spire.doc import *
from ctypes import *
import abc

class Shading ( AttrCollection):
    """
    Represents a collection of Shading values for a document element.
    """
    @property
    def BackgroundPatternColor(self)->'Color':
        """
        Gets or sets the BackgroundPatternColor.
        """
        GetDllLibDoc().Shading_get_BackgroundPatternColor.argtypes=[c_void_p]
        GetDllLibDoc().Shading_get_BackgroundPatternColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().Shading_get_BackgroundPatternColor,self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret

    @BackgroundPatternColor.setter
    def BackgroundPatternColor(self, value:'Color'):
        """
        Sets the BackgroundPatternColor.
        """
        GetDllLibDoc().Shading_set_BackgroundPatternColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibDoc().Shading_set_BackgroundPatternColor, self.Ptr, value.Ptr)

    @property
    def ForegroundPatternColor(self)->'Color':
        """
        Gets or sets the ForegroundPatternColor.
        """
        GetDllLibDoc().Shading_get_ForegroundPatternColor.argtypes=[c_void_p]
        GetDllLibDoc().Shading_get_ForegroundPatternColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().Shading_get_ForegroundPatternColor,self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret

    @ForegroundPatternColor.setter
    def ForegroundPatternColor(self, value:'Color'):
        """
        Sets the ForegroundPatternColor.
        """
        GetDllLibDoc().Shading_set_ForegroundPatternColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibDoc().Shading_set_ForegroundPatternColor,self.Ptr, value.Ptr)

    @property
    def TextureStyle(self) -> 'TextureStyle':
        """
        Gets or sets TextureStyle.
        """
        GetDllLibDoc().Shading_set_TextureStyle.argtypes=[c_void_p]
        GetDllLibDoc().Shading_set_TextureStyle.restype=c_int
        ret = CallCFunction(GetDllLibDoc().Shading_set_TextureStyle,self.Ptr)
        objwraped = TextureStyle(ret)
        return objwraped

    @TextureStyle.setter
    def TextureStyle(self, value:'TextureStyle'):
        GetDllLibDoc().Shading_get_TextureStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibDoc().Shading_get_TextureStyle,self.Ptr, value.value)

    def ClearFormatting(self):
        """
        Clears the Formatting.
        """
        GetDllLibDoc().Shading_ClearFormatting.argtypes=[c_void_p]
        CallCFunction(GetDllLibDoc().Shading_ClearFormatting,self.Ptr)