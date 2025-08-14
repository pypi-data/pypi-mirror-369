from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.doc.common import *
from spire.doc import *
from ctypes import *
import abc

class TextEffectFormat (SpireObject) :
    """
<summary></summary>
    """
    
    def SetTextOpacity(self, value:float):
        GetDllLibDoc().TextEffectFormat_set_TextOpacity.argtypes = [c_void_p, c_double]
        CallCFunction(GetDllLibDoc().TextEffectFormat_set_TextOpacity,self.Ptr, value)

