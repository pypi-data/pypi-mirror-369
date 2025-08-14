from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.doc.common import *
from spire.doc import *
from ctypes import *
import abc

class ChartSeries (SpireObject) :
    """

    """
    @property
    def Explosion(self)->int:
        """

        """
        GetDllLibDoc().ChartSeries_get_Explosion.argtypes=[c_void_p]
        GetDllLibDoc().ChartSeries_get_Explosion.restype=c_int
        ret = CallCFunction(GetDllLibDoc().ChartSeries_get_Explosion,self.Ptr)
        return ret

    @Explosion.setter
    def Explosion(self, value:int):
        GetDllLibDoc().ChartSeries_set_Explosion.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibDoc().ChartSeries_set_Explosion,self.Ptr, value)

    @property
    def InvertIfNegative(self)->bool:
        """

        """
        GetDllLibDoc().ChartSeries_get_InvertIfNegative.argtypes=[c_void_p]
        GetDllLibDoc().ChartSeries_get_InvertIfNegative.restype=c_bool
        ret = CallCFunction(GetDllLibDoc().ChartSeries_get_InvertIfNegative,self.Ptr)
        return ret

    @InvertIfNegative.setter
    def InvertIfNegative(self, value:bool):
        GetDllLibDoc().ChartSeries_set_InvertIfNegative.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibDoc().ChartSeries_set_InvertIfNegative,self.Ptr, value)

    @property

    def Marker(self)->'ChartMarker':
        """

        """
        GetDllLibDoc().ChartSeries_get_Marker.argtypes=[c_void_p]
        GetDllLibDoc().ChartSeries_get_Marker.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().ChartSeries_get_Marker,self.Ptr)
        ret = None if intPtr==None else ChartMarker(intPtr)
        return ret


    @property
    def Bubble3D(self)->bool:
        """

        """
        GetDllLibDoc().ChartSeries_get_Bubble3D.argtypes=[c_void_p]
        GetDllLibDoc().ChartSeries_get_Bubble3D.restype=c_bool
        ret = CallCFunction(GetDllLibDoc().ChartSeries_get_Bubble3D,self.Ptr)
        return ret

    @Bubble3D.setter
    def Bubble3D(self, value:bool):
        GetDllLibDoc().ChartSeries_set_Bubble3D.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibDoc().ChartSeries_set_Bubble3D,self.Ptr, value)

    @property

    def DataPoints(self)->'ChartDataPointCollection':
        """

        """
        GetDllLibDoc().ChartSeries_get_DataPoints.argtypes=[c_void_p]
        GetDllLibDoc().ChartSeries_get_DataPoints.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().ChartSeries_get_DataPoints,self.Ptr)
        from spire.doc import ChartDataPointCollection
        ret = None if intPtr==None else ChartDataPointCollection(intPtr)
        return ret


    @property

    def Name(self)->str:
        """

        """
        GetDllLibDoc().ChartSeries_get_Name.argtypes=[c_void_p]
        GetDllLibDoc().ChartSeries_get_Name.restype=c_char_p
        ret = CallCFunction(GetDllLibDoc().ChartSeries_get_Name,self.Ptr)
        return ret


    @Name.setter
    def Name(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibDoc().ChartSeries_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibDoc().ChartSeries_set_Name,self.Ptr, valuePtr)

    @property
    def Smooth(self)->bool:
        """

        """
        GetDllLibDoc().ChartSeries_get_Smooth.argtypes=[c_void_p]
        GetDllLibDoc().ChartSeries_get_Smooth.restype=c_bool
        ret = CallCFunction(GetDllLibDoc().ChartSeries_get_Smooth,self.Ptr)
        return ret

    @Smooth.setter
    def Smooth(self, value:bool):
        GetDllLibDoc().ChartSeries_set_Smooth.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibDoc().ChartSeries_set_Smooth,self.Ptr, value)

    @property

    def DataLabels(self)->'ChartDataLabelCollection':
        """

        """
        GetDllLibDoc().ChartSeries_get_DataLabels.argtypes=[c_void_p]
        GetDllLibDoc().ChartSeries_get_DataLabels.restype=c_void_p
        intPtr = CallCFunction(GetDllLibDoc().ChartSeries_get_DataLabels,self.Ptr)
        from spire.doc import ChartDataLabelCollection
        ret = None if intPtr==None else ChartDataLabelCollection(intPtr)
        return ret


