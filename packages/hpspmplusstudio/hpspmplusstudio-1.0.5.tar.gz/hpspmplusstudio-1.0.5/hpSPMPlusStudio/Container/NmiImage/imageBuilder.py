from hpSPMPlusStudio.Container.NmiImage.image import NMIImage
from hpSPMPlusStudio.Container.NmiContainer.enums import*
from hpSPMPlusStudio.Container.NmiFrame.frameChannels import*
class NMIImageBuilder():
    def __init__(self):
        self.Image = NMIImage()
        pass
    
    def SetWidthPixe(self,width):
        self.Image.WidthPixel = width
        return self

    def SetHeightPixel(self,height):
        self.Image.HeightPixel = height
        return self

    def SetRealHeight(self,height):
        self.Image.RealHeight = height
        return self
    
    def SetRealWidth(self,width):
        self.Image.RealWidth = width
        return self
    
    def SetRealHeightUnit(self,unit:ScaleUnit):
        self.Image.RealHeightUnit = unit
        return self
    
    def SetRealWidthUnit(self,unit:ScaleUnit):
        self.Image.RealWidthUnit = unit
        return self

    def SetRealHeightUnitPrefix(self,prefix:ScalePrefix):
        self.Image.RealHeightUnitPrefix = prefix
        return self
    
    def SetRealWidthUnitPrefix(self,prefix:ScalePrefix):
        self.Image.RealWidthUnitPrefix = prefix
        return self
    
    def SetRealBufferUnit(self,unit:ScaleUnit):
        self.Image.RealBufferUnit = unit
        return self
    def SetRealBufferUnitPrefix(self,prefix:ScalePrefix):
        self.Image.RealBufferUnitPrefix = prefix
        return self
    
    def SetChannel(self,channel:FrameChannels):
        self.Image.channel = channel
        self.Image.imageName = channel.name
        return self
        
    def Build(self)->NMIImage:
        self.Image.CreateNewFrame()
        return self.Image
