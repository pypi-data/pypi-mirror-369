from hpSPMPlusStudio.Container.NmiContainer.containerBuilder import NMIContainerBuilder
from hpSPMPlusStudio.Container.NmiContainer.container import NMIContainer
from hpSPMPlusStudio.Container.NmiImage import NMIImage
from hpSPMPlusStudio.Container.NmiContainer.enums import*
from hpSPMPlusStudio.Container.NmiFrame.frameChannels import FrameChannels
from hpSPMPlusStudio.Container.NmiFrame.frame import NMIFrame
from hpSPMPlusStudio.ExternalDevices.Devices.utils import ExternalScanDevice
from hpSPMPlusStudio.Plots.ContainerPlot.ContainerPlotManager import ContainerPlotManager
from hpSPMPlusStudio import NMICommand,NMIEndpoint,NMIDevice
import time
from tqdm import tqdm

class CustomScanner:
    def __init__(self,device:NMIDevice):
        self.Device = device
        self._Scan = self.Device.SCAN()
        self._XYOffsetController = self.Device.XYOFFSET()
        self.ExternalScanDevices = []
            
    def InitScan(self,width:int,height:int,realwidth:float,realheight:float,channelList:list,xOffset:int=0,yOffset:int=0):
        self.ExternalScanDevices = []
        self.width = width
        self.height = height
        self._XYOffsetController.Start_GuiOffsetUpdater()
        self._XYOffsetController.Set_XOffset(0)
        self._XYOffsetController.Set_YOffset(0)
        self._XYOffsetController.Stop_GuiOffsetUpdater()
        self.xOffsetList = self.calculate_x_positions(realwidth, width,xOffset)
        self.yOffsetList = self.calculate_y_positions(realheight, height,yOffset)
        ContainerBuilder = NMIContainerBuilder() 
        self.container = (ContainerBuilder.SetWidthPixel(self.width)
                    .SetHeightPixel(self.height)
                    .SetRealHeight(realheight)
                    .SetRealWidth(realwidth)
                    .SetRealHeightUnit(ScaleUnit.Meter)
                    .SetRealWidthUnit(ScaleUnit.Meter)
                    .SetRealHeightUnitPrefix(ScalePrefix.micro)
                    .SetRealWidthUnitPrefix(ScalePrefix.micro))     
        for channel in channelList:
            if(type(channel) == FrameChannels):
                self.container.AddImageChannel(channel)   
                print("Channel Added: ",channel)     
        self.container = self.container.Build()     
       
    def StartScan(self):
        self._startScan()

    def _startScan(self):
        for line in tqdm(range(self.height),desc="Scanning Lines"):
            self.SetYOffset(self.yOffsetList[line])
            self.SetXOffset(self.xOffsetList[0])
            self._LineScan()
            time.sleep(0.1)
        self._XYOffsetController.Start_GuiOffsetUpdater()
        
    def AddExternalScanDevice(self,channel:FrameChannels,device:ExternalScanDevice,frameCount:int=1):
        self.container.AddNewImage(channel)
        if(frameCount>1):
            image:NMIImage =self.container.GetImageFromChannel(channel)
            for i in range(frameCount-1):
                image.CreateNewFrame()
        self.ExternalScanDevices.append((channel,device))
        print("Channel Added: ",channel)
        print("Device Added: ", device)


    def _LineScan(self):
        for pixel in tqdm(range(self.width),desc="Scanning Pixels",disable=False):
            self.SetXOffset(self.xOffsetList[pixel])
            data = self._GetCapturePixelData()
            self.container.AddPixelToRawBuffer_FromAPIRequest(data)
            self.UpdateExternalDevicesScanData()

    def UpdateExternalDevicesScanData(self):
        for device in self.ExternalScanDevices:
            try:
                channel = device[0]
                device:ExternalScanDevice = device[1]
                data = device.GetScanData()
                if(type(data)==list):
                    if(len(data)==1):
                        self.container.GetImageFromChannel(channel).AddPixelToRawBuffer(data[0])
                    
                    if(len(data)>1):
                        for i in range(len(data)):
                            self.container.GetImageFromChannel(channel).AddPixelToRawBuffer(data[i],i)
                        
                    if(len(data)==0):
                        print("Error: External Device Data is Empty")    

                if(type(data)==float):
                    self.container.GetImageFromChannel(channel).AddPixelToRawBuffer(data)
            except Exception as e:
                print("Error: ",e)
                
            

    def SetXOffset(self,offset:int):
        self._XYOffsetController.Set_DirectXOffset(offset)

    def SetYOffset(self,offset:int):
        self._XYOffsetController.Set_DirectYOffset(offset)

    def _GetCapturePixelData(self)->dict:
        return self._Scan.Get_DirectCapturePixel()

    def GetScanContainer(self)->NMIContainer:
        return self.container
      
    def calculate_pixel_positions(self,axis_length_um, num_pixels,offset):
        step_size = axis_length_um / (num_pixels - 1)
        return [(i * step_size+offset) for i in range(num_pixels)]

    def calculate_x_positions(self,realwidth, num_pixels,xOffset):
        return self.calculate_pixel_positions(realwidth, num_pixels,xOffset)

    def calculate_y_positions(self,realheight, num_pixels,yOffset):
        return self.calculate_pixel_positions(realheight, num_pixels,yOffset)


       
  





