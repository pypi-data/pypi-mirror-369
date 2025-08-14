from hpSPMPlusStudio.Container.NmiFrame import*
from hpSPMPlusStudio.Container.NmiImage import NMIImage
from hpSPMPlusStudio.Container.NmiImage import NMIImageBuilder
from hpSPMPlusStudio.Container.NmiContainer.enums import*
import json
from datetime import datetime 

class NMIContainer():
    def  __init__(self,containerName:str = None):
        if(containerName is None):
            containerName = "Default_" + datetime.now().strftime("%Y%m%d%H%M%S")
        self.containerName = containerName
        self.ImageList = [] 
        self.WidthPixel:int = None
        self.HeightPixel:int = None
        self.RealHeight:float = None
        self.RealWidth:float = None
        self.RealHeightUnit:ScaleUnit = None
        self.RealWidthUnit:ScaleUnit = None
        self.RealHeightUnitPrefix:ScalePrefix = None
        self.RealWidthUnitPrefix:ScalePrefix = None

    def AddNewImage(self,frameType:FrameChannels,realBufferUnit:ScaleUnit = ScaleUnit.Meter,realBufferUnitPrefix:ScalePrefix = ScalePrefix.micro):
        self.NMIImageBuilder = NMIImageBuilder()
        newImage = (self.NMIImageBuilder
                    .SetChannel(frameType)
                    .SetWidthPixe(self.WidthPixel)
                    .SetHeightPixel(self.HeightPixel)
                    .SetRealHeight(self.RealHeight)
                    .SetRealWidth(self.RealWidth)
                    .SetRealHeightUnitPrefix(self.RealHeightUnitPrefix)
                    .SetRealWidthUnitPrefix(self.RealWidthUnitPrefix)
                    .SetRealHeightUnit(self.RealHeightUnit)
                    .SetRealWidthUnit(self.RealWidthUnit)
                    .SetRealBufferUnit(realBufferUnit)
                    .SetRealBufferUnitPrefix(realBufferUnitPrefix)
                    .Build())
        self.ImageList.append(newImage)

    def GetImageFromChannel(self,channel:FrameChannels)->NMIImage:
        for image in self.ImageList:
            image: NMIImage = image
            if image.channel == channel:
                return image
        return None
    
    def GetFrameFromChannel(self,channel:FrameChannels)->NMIFrame:
        for image in self.ImageList:
            image: NMIImage = image
            if image.channel == channel:
                return image.GetFirstFrame()
        return None

    def AddPixelToRawBuffer_FromAPIRequest(self,data):
        for image in self.ImageList:
            image: NMIImage = image
            image.AddPixelToRawBuffer_FromAPIRequest(data)
       
    def GetImageList(self):
        return self.ImageList
    
    def _GetJsonObject(self):
        jsonObject = {
            "ContainerName": self.containerName,
            "WidthPixel": self.WidthPixel,
            "HeightPixel": self.HeightPixel,
            "RealHeight": self.RealHeight,
            "RealWidth": self.RealWidth,
            "RealHeightUnit": self.RealHeightUnit.name,
            "RealWidthUnit": self.RealWidthUnit.name,
            "RealHeightUnitPrefix": self.RealHeightUnitPrefix.name,
            "RealWidthUnitPrefix": self.RealWidthUnitPrefix.name,
            "ImageList": self._GetImageListJsonObject()
        }
        return jsonObject

    def _GetImageListJsonObject(self):
        _list = []
        for image in self.ImageList:
            image:NMIImage = image
            _list.append(image._GetJsonObject())
        return _list

    def Save(self,filename:str):
        data = self._GetJsonObject()
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)

    def _LoadFromJsonObject(self,data:dict):
        self.containerName = data["ContainerName"]
        self.WidthPixel = data["WidthPixel"]
        self.HeightPixel = data["HeightPixel"]
        self.RealHeight = data["RealHeight"]
        self.RealWidth = data["RealWidth"]
        self.RealHeightUnit = ScaleUnit[data["RealHeightUnit"]]
        self.RealWidthUnit = ScaleUnit[data["RealWidthUnit"]]
        self.RealHeightUnitPrefix = ScalePrefix[data["RealHeightUnitPrefix"]]
        self.RealWidthUnitPrefix = ScalePrefix[data["RealWidthUnitPrefix"]]
        self.ImageList = []
        for image in data["ImageList"]:
            newImage = NMIImage()
            newImage._LoadFromJsonObject(image)
            self.ImageList.append(newImage)
    
    def Load(self,filename:str):
        with open(filename, 'r') as file:
            data = json.load(file)
            self._LoadFromJsonObject(data)