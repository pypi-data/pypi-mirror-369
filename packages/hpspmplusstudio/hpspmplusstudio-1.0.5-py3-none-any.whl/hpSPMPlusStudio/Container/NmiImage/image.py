from hpSPMPlusStudio.Container.NmiFrame import*
from hpSPMPlusStudio.Container.NmiContainer.enums import*

class NMIImage():
    def __init__(self):
        self.imageName = None
        self.WidthPixel:int = None
        self.HeightPixel:int = None
        self.RealHeight:float = None
        self.RealWidth:float = None
        self.RealHeightUnit:ScaleUnit = None
        self.RealWidthUnit:ScaleUnit = None
        self.RealHeightUnitPrefix:ScalePrefix = None
        self.RealWidthUnitPrefix:ScalePrefix = None
        self.RealBufferUnit:ScaleUnit = None
        self.RealBufferUnitPrefix:ScalePrefix = None
        self.channel:FrameChannels = None
        self.frameList = []

    def AddPixelToRawBuffer_FromAPIRequest(self,data:dict,index = 0):
        frame:NMIFrame = self.frameList[index]
        frame.AddPixelToRawBuffer_FromAPIRequest(data)

    def UpdateFrameRawBuffer_FromAPIRequest(self,data:dict,index = 0):
        frame:NMIFrame = self.frameList[index]
        frame.UpdateFrameRawBuffer_FromAPIRequest(data)

    def AddPixelToRealBuffer(self,data:dict,index = 0):
        frame:NMIFrame = self.frameList[index]
        frame.AddPixelToRealBuffer(data)

    def AddPixelToRawBuffer(self,data,index = 0):
        frame:NMIFrame = self.frameList[index]
        frame.AddPixelToRawBuffer(data)

    def CreateNewFrame(self):
        newFrame = NMIFrame(self.WidthPixel,self.HeightPixel,self.channel)
        self.frameList.append(newFrame)
   
    def GetFrameList(self):
        return self.frameList
    
    def GetFirstFrame(self)->NMIFrame:
        return self.frameList[0]

    def _GetJsonObject(self):
        jsonObject = {
            "ImageName": self.imageName,
            "WidthPixel": self.WidthPixel,
            "HeightPixel": self.HeightPixel,
            "RealHeight": self.RealHeight,
            "RealWidth": self.RealWidth,
            "RealHeightUnit": self.RealHeightUnit.name,
            "RealWidthUnit": self.RealWidthUnit.name,
            "RealHeightUnitPrefix": self.RealHeightUnitPrefix.name,
            "RealWidthUnitPrefix": self.RealWidthUnitPrefix.name,
            "RealBufferUnit": self.RealBufferUnit.name,
            "RealBufferUnitPrefix": self.RealBufferUnitPrefix.name,
            "Channel": self.channel.name,
            "Frames": self._GetJsonObjectFrameList()
        }
        return jsonObject

    def _GetJsonObjectFrameList(self):
        _list = []
        for frame in self.frameList:
            frame:NMIFrame = frame
            _list.append(frame._GetJsonObject())
        return _list
    
    def _LoadFromJsonObject(self,data:dict):
        self.imageName = data["ImageName"]
        self.WidthPixel = data["WidthPixel"]
        self.HeightPixel = data["HeightPixel"]
        self.RealHeight = data["RealHeight"]
        self.RealWidth = data["RealWidth"]
        self.RealHeightUnit = ScaleUnit[data["RealHeightUnit"]]
        self.RealWidthUnit = ScaleUnit[data["RealWidthUnit"]]
        self.RealHeightUnitPrefix = ScalePrefix[data["RealHeightUnitPrefix"]]
        self.RealWidthUnitPrefix = ScalePrefix[data["RealWidthUnitPrefix"]]
        self.RealBufferUnit = ScaleUnit[data["RealBufferUnit"]]
        self.RealBufferUnitPrefix = ScalePrefix[data["RealBufferUnitPrefix"]]
        self.channel = FrameChannels[data["Channel"]]
        for frameData in data["Frames"]:
            frame = NMIFrame(self.WidthPixel,self.HeightPixel,self.channel)
            frame._LoadFromJsonObject(frameData)
            self.frameList.append(frame)
    
 
