from hpSPMPlusStudio.Container.NmiFrame import*
from hpSPMPlusStudio.Container.NmiContainer import NMIContainer
from hpSPMPlusStudio.Container.NmiContainer.enums import*

class NMIContainerBuilder():
    def __init__(self):
        self.container = NMIContainer()
    
    def SetWidthPixel(self,width):
        self.container.WidthPixel = width
        return self
    def SetHeightPixel(self,height):
        self.container.HeightPixel = height
        return self
    def SetRealHeight(self,height):
        self.container.RealHeight = height
        return self
    def SetRealWidth(self,width):
        self.container.RealWidth = width
        return self
    def SetRealHeightUnit(self,unit:ScaleUnit):
        self.container.RealHeightUnit = unit
        return self
    def SetRealWidthUnit(self,unit:ScaleUnit):
        self.container.RealWidthUnit = unit
        return self
    
    def SetRealHeightUnitPrefix(self,prefix:ScalePrefix):
        self.container.RealHeightUnitPrefix = prefix
        return self
    def SetRealWidthUnitPrefix(self,prefix:ScalePrefix):
        self.container.RealWidthUnitPrefix = prefix
        return self
    
    def AddImageChannel(self,channel:FrameChannels):
        self.container.AddNewImage(channel)
        return self

    def Build(self):
        return self.container