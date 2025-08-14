from hpSPMPlusStudio.Container.NmiFrame.frameChannels import FrameChannels, GetAPIResponseKeyForChannel
import numpy as np

class NMIFrame():
    def __init__(self,width:int,height:int,channel:FrameChannels):
        self.channel:FrameChannels=channel
        self.width:int=width
        self.height:int=height
        self.rawBuffer = []
        self.realBuffer = []
      
    def Get8BitImageData(self)->np.array:
        image_data = np.array(self.rawBuffer).reshape((self.height, self.width))
        image_data = ((image_data - np.min(image_data)) / (np.max(image_data) - np.min(image_data)) * 255).astype(np.uint8)
        return image_data

    def Get16BitImageData(self) -> np.array:
        image_data = np.array(self.rawBuffer).reshape((self.height, self.width))
        # Veriyi normalize et ve 16-bit'e ölçekle
        image_data = ((image_data - np.min(image_data)) / (np.max(image_data) - np.min(image_data)) * 65535).astype(np.uint16)
        return image_data

    def GetRawImageData(self) -> np.array:
        image_data = np.array(self.rawBuffer).reshape((self.height, self.width))
        return image_data

    def UpdateFrameRawBuffer_FromAPIRequest(self,data:dict):
        if "RawBuffer" not in data:
            return None
        data_string = data["RawBuffer"]  
        self.rawBuffer = np.array([int(x) for x in data_string.split(";")], dtype=np.int32)
       
    def UpdateFrameRealBuffer_FromAPIRequest(self,data:dict):
        if "RealBuffer" not in data:
            return None
        data_string = data["RealBuffer"]  
        data = np.array([int(x) for x in data_string.split(";")], dtype=np.int32)
        self.realBuffer = data.reshape(self.height,self.width)
    
    def AddPixelToRawBuffer_FromAPIRequest(self,data:dict):
        key = GetAPIResponseKeyForChannel(self.channel)
        if key is None:
            return None
        if key not in data:
            return None 
        _bufferData = float(data[key])
        self.rawBuffer.append(_bufferData)

    def AddPixelToRawBuffer(self,data:float):
        self.rawBuffer.append(data)

    def AddPixelToRealBuffer(self,data):
        self.realBuffer.append(data)

    def _GetJsonObject(self):
        jsonObject = {
            "Width": self.width,
            "Height": self.height,
            "RawBuffer": self.rawBuffer,
            "RealBuffer": self.realBuffer
        }
        return jsonObject
    
    def _LoadFromJsonObject(self,data:dict):
        self.width = data["Width"]
        self.height = data["Height"]
        self.rawBuffer = data["RawBuffer"]
        self.realBuffer = data["RealBuffer"]


    
    