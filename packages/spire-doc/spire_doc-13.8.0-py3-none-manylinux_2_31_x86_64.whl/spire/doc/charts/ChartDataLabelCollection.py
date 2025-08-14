from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.doc.common import *
from spire.doc import *
from ctypes import *
import abc

class ChartDataLabelCollection (  IEnumerable) :
    """

    """

    def get_Item(self ,index:int)->'ChartDataLabel':
        """

        """
        
        GetDllLibDoc().ChartDataLabelCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibDoc().ChartDataLabelCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().ChartDataLabelCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else ChartDataLabel(intPtr)
        return ret



    def GetEnumerator(self)->'IEnumerator':
        """

        """
        GetDllLibDoc().ChartDataLabelCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibDoc().ChartDataLabelCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().ChartDataLabelCollection_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret



    ##def Add(self ,index:int)->'ChartDataLabel':       
        ##GetDllLibDoc().ChartDataLabelCollection_Add.argtypes=[c_void_p ,c_int]
        ##GetDllLibDoc().ChartDataLabelCollection_Add.restype=c_void_p
        ##intPtr = CallCFunction(GetDllLibDoc().ChartDataLabelCollection_Add,self.Ptr, index)
        ##ret = None if intPtr==None else ChartDataLabel(intPtr)
        ##return ret



    ##def RemoveAt(self ,index:int):
        ##GetDllLibDoc().ChartDataLabelCollection_RemoveAt.argtypes=[c_void_p ,c_int]
        ##CallCFunction(GetDllLibDoc().ChartDataLabelCollection_RemoveAt,self.Ptr, index)

    ##def Clear(self):
        ##GetDllLibDoc().ChartDataLabelCollection_Clear.argtypes=[c_void_p]
        ##CallCFunction(GetDllLibDoc().ChartDataLabelCollection_Clear,self.Ptr)

    @property
    def Count(self)->int:
        """

        """
        GetDllLibDoc().ChartDataLabelCollection_get_Count.argtypes=[c_void_p]
        GetDllLibDoc().ChartDataLabelCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibDoc().ChartDataLabelCollection_get_Count,self.Ptr)
        return ret

