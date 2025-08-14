from hpSPMPlusStudio.NMIImporter.Decarators import*
from hpSPMPlusStudio.RequestManager.NMIEndpoint import NMIEndpoint
from hpSPMPlusStudio.RequestManager.NMICommand import NMICommand
from hpSPMPlusStudio.NMIManager.Managers.Controllers.StatusController import StatusController
from hpSPMPlusStudio.NMIManager.Managers.Controllers.ScannedImagesController import ScannedImagesController
from hpSPMPlusStudio.NMIManager.Managers.Controllers.SystemReadingsController import SystemReadingsController
from hpSPMPlusStudio.NMIManager.Managers.Controllers.ScanController import ScanController
from hpSPMPlusStudio.NMIManager.Managers.Controllers.OptionsController import OptionsController
from hpSPMPlusStudio.NMIManager.Managers.Controllers.XYOffsetController import XYOffsetController
from hpSPMPlusStudio.NMIManager.Managers.Controllers.PIDController import PIDController
from hpSPMPlusStudio.NMIManager.Managers.Controllers.AutoTuneController import AutoTuneController
from hpSPMPlusStudio.NMIManager.Managers.Controllers.PhotoDiodeController import PhotoDiodeController
from hpSPMPlusStudio.NMIManager.Managers.Controllers.HallCardController import HallCardController
from hpSPMPlusStudio.NMIManager.Managers.Controllers.BiasController import VBiasController
from hpSPMPlusStudio.NMIManager.Managers.Controllers.FiberController import FiberCardController
from hpSPMPlusStudio.NMIManager.Managers.Controllers.AdjustFiberController import AdjustFiberController
from hpSPMPlusStudio.NMIManager.Managers.Controllers.WindowController import WindowController
from hpSPMPlusStudio.NMIManager.Managers.Controllers.ApproachController import ApproachController


PREFIX = "APP"
BASE_COMMAND = "DeviceInformations"

@Singleton
class NMIDevice:
    def __init__(self,endpoint:NMIEndpoint) -> None:
        self.DeviceEndpoint = endpoint
        self._CreateControllers()

    def Get_DeviceInfo(self)->dict:
        command = NMICommand(self.DeviceEndpoint,PREFIX,BASE_COMMAND)
        return command.execute_get()
    
    def _CreateControllers(self):
        self._Status = StatusController(self.DeviceEndpoint)
        self._ScannedImages = ScannedImagesController(self.DeviceEndpoint)
        self._SystemReadings = SystemReadingsController(self.DeviceEndpoint)
        self._Scan = ScanController(self.DeviceEndpoint)
        self._Options = OptionsController(self.DeviceEndpoint)
        self._XYOffset = XYOffsetController(self.DeviceEndpoint)
        self._PID = PIDController(self.DeviceEndpoint)
        self._AutoTune = AutoTuneController(self.DeviceEndpoint)
        self._PhotoDiode = PhotoDiodeController(self.DeviceEndpoint)
        self._HallCard = HallCardController(self.DeviceEndpoint)
        self._VBias = VBiasController(self.DeviceEndpoint)
        self._FiberCardController = FiberCardController(self.DeviceEndpoint)
        self._AdjustFiberController = AdjustFiberController(self.DeviceEndpoint)
        self._WindowController = WindowController(self.DeviceEndpoint)
        self._ApproachController = ApproachController(self.DeviceEndpoint)
        

    def STATUS(self)->StatusController:
        return self._Status
    
    def SCAN(self)->ScanController:
        return self._Scan
    
    def SCANNEDIMAGES(self)->ScannedImagesController:
        return self._ScannedImages

    def SYSTEMREADINGS(self)->SystemReadingsController:
        return self._SystemReadings
    
    def OPTIONS(self)->OptionsController:
        return self._Options

    def XYOFFSET(self)->XYOffsetController:
        return self._XYOffset
    
    def PID(self)->PIDController:
        return self._PID
    
    def AUTOTUNE(self)->AutoTuneController:
        return self._AutoTune

    def APPROACH(self)->ApproachController:
        return self._ApproachController

    def PHOTODIODE(self)->PhotoDiodeController:
        return self._PhotoDiode
    
    def HALLCARD(self)->HallCardController:
        return self._HallCard
    
    def VBIAS(self)->VBiasController:
        return self._VBias
    
    def FIBERCARD(self)->FiberCardController:
        return self._FiberCardController
    
    def ADJUSTFIBER(self)->AdjustFiberController:
        return self._AdjustFiberController
    
    def WINDOWCONTROLLER(self)->WindowController:
        return self._WindowController