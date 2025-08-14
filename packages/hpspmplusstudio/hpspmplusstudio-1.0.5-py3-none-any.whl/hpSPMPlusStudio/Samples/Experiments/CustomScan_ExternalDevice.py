from hpSPMPlusStudio import NMICommand,NMIEndpoint,NMIDevice
from hpSPMPlusStudio.Plots.ContainerPlot.ContainerPlotManager import ContainerPlotManager
from hpSPMPlusStudio.Container.NmiContainer.container import NMIContainer
from hpSPMPlusStudio.Container.NmiContainer.enums import*
from hpSPMPlusStudio.Container.NmiFrame.frameChannels import FrameChannels
from hpSPMPlusStudio.Container.NmiFrame.frame import NMIFrame
from hpSPMPlusStudio.ExternalDevices.Devices.utils import ExternalScanDevice
from hpSPMPlusStudio.ExternalDevices.Devices.Thorlabs_SPCM50 import*
from hpSPMPlusStudio.NMIManager.Managers.CustomScanner import CustomScanner

from hpSPMPlusStudio.ExternalDevices.Devices.externalTest import ExternalTest
from hpSPMPlusStudio import help

help()

Endpoint = NMIEndpoint("192.168.10.53",9024)
Device = NMIDevice(Endpoint)
Device.XYOFFSET().Start_GuiOffsetUpdater()

device2 = ExternalTest()

spcm_model = SPCM50ControlModel()
# Ayarları yükle (Örnek: varsayılanı kullan)
spcm_model.load_settings()
# Cihazı başlat
if spcm_model.initialize():
        # Ölçüm ile ilgili ön hazırlıkları yap
    if spcm_model.measurement_init():
        spcm_model.set_operating_mode(SPCM50_OPERATINGMODES.FreeRunning)
        
        spcm_model.average_count = 10
        spcm_model.set_bin_length(20)
        spcm_model.set_time_between(10)

        _ScanManager = CustomScanner(Device)

        ChannelList = [
            FrameChannels.Channel_Vz,
            FrameChannels.Channel_ITunnel,
            FrameChannels.Channel_Rms2,
        ]

        _ScanManager.InitScan(5,5,3,3,channelList=ChannelList,xOffset=0,yOffset=0)
        _ScanManager.AddExternalScanDevice(FrameChannels.Channel_Custom1,spcm_model)
        _ScanManager.AddExternalScanDevice(FrameChannels.Channel_Custom2,device2,128)
        _ScanManager.StartScan()

        Container = _ScanManager.GetScanContainer()

        Container.Save("sampleContainer2.json")

        ContainerPlotManager().plot8BitColorMapFromImage(Container.GetImageFromChannel(FrameChannels.Channel_Vz))
        ContainerPlotManager().plot8BitColorMapFromImage(Container.GetImageFromChannel(FrameChannels.Channel_ITunnel))
        ContainerPlotManager().plot8BitColorMapFromImage(Container.GetImageFromChannel(FrameChannels.Channel_Rms2))

        ContainerPlotManager().plot8BitColorMapFromImage(Container.GetImageFromChannel(FrameChannels.Channel_Custom1))
        ContainerPlotManager().plot16BitColorMapFromImage(Container.GetImageFromChannel(FrameChannels.Channel_Custom1))
        ContainerPlotManager().plot16BitRawMapFromImage(Container.GetImageFromChannel(FrameChannels.Channel_Custom1))