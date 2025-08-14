from hpSPMPlusStudio.NMIImporter.BuiltInImporter import*
from hpSPMPlusStudio.NMIImporter.Decarators import*
from hpSPMPlusStudio.RequestManager.NMIEndpoint import NMIEndpoint
from hpSPMPlusStudio.RequestManager.NMICommand import NMICommand

PREFIX = "Scan"

class GET_Commands(Enum):
    Get_Commands = "Get_Commands"
    Get_IsScanning = "Get_IsScanning"
    Get_ScanError = "Get_ScanError"
    Get_ScanLineIndex = "Get_ScanLineIndex"
    Get_ScanIndex = "Get_ScanIndex"

    Get_XOffset = "Get_XOffset"
    Get_YOffset = "Get_YOffset"
    Get_ScanWidthPixel = "Get_ScanWidthPixel"
    Get_ScanHeightPixel = "Get_ScanHeightPixel"
    Get_ImageWidth = "Get_ImageWidth"
    Get_ImageHeight = "Get_ImageHeight"
    Get_IsImageSquare = "Get_IsImageSquare"
    Get_ScanAngle = "Get_ScanAngle"
    Get_ScanSpeed = "Get_ScanSpeed" 
    Get_ScanNumberOfAverages = "Get_ScanNumberOfAverages"
    Get_NumberOfScans = "Get_NumberOfScans"
    Get_OffsetPosition = "Get_OffsetPosition"
    Get_ScanDirection = "Get_ScanDirection"
    Get_IsRoundtripScan = "Get_IsRoundtripScan"
    Get_IsSaveScannedImages = "Get_IsSaveScannedImages"
    Get_CapturePixel = "Get_CapturePixel"
    Get_DirectCapturePixel = "Get_DirectCapturePixel"
    Get_CapturePixelUnitText = "Get_CapturePixelUnitText"

   
class SET_Commands(Enum):
    Set_UseDefaultScanOptions = "Set_UseDefaultScanOptions"
    Set_XOffset = "Set_XOffset"
    Set_YOffset = "Set_YOffset"
    Set_ScanWidthPixel = "Set_ScanWidthPixel" 
    Set_ScanHeightPixel = "Set_ScanHeightPixel"
    Set_ImageWidth = "Set_ImageWidth"
    Set_ImageHeight = "Set_ImageHeight"
    Set_IsImageSquare = "Set_IsImageSquare"
    Set_ScanAngle = "Set_ScanAngle"
    Set_ScanSpeed = "Set_ScanSpeed"
    Set_ScanNumberOfAverages = "Set_ScanNumberOfAverages"
    Set_NumberOfScans = "Set_NumberOfScans"
    Set_OffsetPosition = "Set_OffsetPosition"
    Set_ScanDirection = "Set_ScanDirection"
    Set_IsRoundtripScan = "Set_IsRoundtripScan"
    Set_IsSaveScannedImages = "Set_IsSaveScannedImages"

    StartScan = "StartScan"
    StopScan = "StopScan"


class ScanController:
    def __init__(self,endpoint:NMIEndpoint) -> None:
        self.Endpoint = endpoint

    def Get_Commands(self)->list:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_Commands.value)
        try:
            response = command.execute_get()
            if("Commands" in response):
                return response["Commands"].split(';')
            else:
                return []
        except Exception as e:
            return []
        
    @ExceptionLoggerAPIResponse    
    def Get_XOffset(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_XOffset.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse    
    def Get_IsScanning(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_IsScanning.value)
        response = command.execute_get()
        return response

    @ExceptionLoggerAPIResponse    
    def Get_ScanError(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_ScanError.value)
        response = command.execute_get()
        return response

    @ExceptionLoggerAPIResponse    
    def Get_ScanLineIndex(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_ScanLineIndex.value)
        response = command.execute_get()
        return response

    @ExceptionLoggerAPIResponse    
    def Get_ScanIndex(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_ScanIndex.value)
        response = command.execute_get()
        return response

    @ExceptionLoggerAPIResponse
    def Get_YOffset(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_YOffset.value)
        response = command.execute_get()
        return response
    @ExceptionLoggerAPIResponse
    def Get_ScanWidthPixel(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_ScanWidthPixel.value)
        response = command.execute_get()
        return response
    @ExceptionLoggerAPIResponse
    def Get_ScanHeightPixel(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_ScanHeightPixel.value)
        response = command.execute_get()
        return response
    @ExceptionLoggerAPIResponse
    def Get_ImageWidth(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_ImageWidth.value)
        response = command.execute_get()
        return response
    @ExceptionLoggerAPIResponse
    def Get_ImageHeight(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_ImageHeight.value)
        response = command.execute_get()
        return response
    @ExceptionLoggerAPIResponse
    def Get_IsImageSquare(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_IsImageSquare.value)
        response = command.execute_get()
        return response
    @ExceptionLoggerAPIResponse
    def Get_ScanAngle(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_ScanAngle.value)
        response = command.execute_get()
        return response
    @ExceptionLoggerAPIResponse
    def Get_ScanSpeed(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_ScanSpeed.value)
        response = command.execute_get()
        return response
    @ExceptionLoggerAPIResponse
    def Get_ScanNumberOfAverages(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_ScanNumberOfAverages.value)
        response = command.execute_get()
        return response
    @ExceptionLoggerAPIResponse
    def Get_NumberOfScans(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_NumberOfScans.value)
        response = command.execute_get()
        return response
    @ExceptionLoggerAPIResponse
    def Get_OffsetPosition(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_OffsetPosition.value)
        response = command.execute_get()
        return response
    @ExceptionLoggerAPIResponse
    def Get_ScanDirection(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_ScanDirection.value)
        response = command.execute_get()
        return response
    @ExceptionLoggerAPIResponse
    def Get_IsRoundtripScan(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_IsRoundtripScan.value)
        response = command.execute_get()
        return response
    @ExceptionLoggerAPIResponse     
    def Get_IsSaveScannedImages(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_IsSaveScannedImages.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_CapturePixel(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_CapturePixel.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_DirectCapturePixel(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_DirectCapturePixel.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_CapturePixelUnitText(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_CapturePixelUnitText.value)
        response = command.execute_get()
        return response

    @ExceptionLoggerAPIResponse
    def Set_UseDefaultScanOptions(self,useDefaultScanOptions:bool)->dict:
        payload = {
            'reg0': bool(useDefaultScanOptions),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_UseDefaultScanOptions.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_XOffset(self,xOffset:float)->dict:
        payload = {
            'reg0': float(xOffset),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_XOffset.value,payload)
        response = command.execute_post()
        return response
    @ExceptionLoggerAPIResponse
    def Set_YOffset(self,yOffset:float)->dict:
        payload = {
            'reg0': float(yOffset),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_YOffset.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_ScanWidthPixel(self,pixel:int)->dict:
        payload = {
            'reg0': int(pixel),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_ScanWidthPixel.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_ScanHeightPixel(self,pixel:int)->dict:
        payload = {
            'reg0': int(pixel),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_ScanHeightPixel.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_ImageWidth(self,width:float)->dict:
        payload = {
            'reg0': float(width),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_ImageWidth.value,payload)
        response = command.execute_post()
        return response

    @ExceptionLoggerAPIResponse
    def Set_ImageHeight(self,height:float)->dict:
        payload = {
            'reg0': float(height),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_ImageHeight.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_IsImageSquare(self,isImageSquare:bool)->dict:
        payload = {
            'reg0': bool(isImageSquare),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_IsImageSquare.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_ScanAngle(self,scanAngle:float)->dict:
        payload = {
            'reg0': float(scanAngle),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_ScanAngle.value,payload)
        response = command.execute_post()
        return response

    @ExceptionLoggerAPIResponse
    def Set_ScanSpeed(self,scanSpeed:float)->dict:
        payload = {
            'reg0': float(scanSpeed),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_ScanSpeed.value,payload)
        response = command.execute_post()
        return response

    @ExceptionLoggerAPIResponse
    def Set_ScanNumberOfAverages(self,numberOfAverage:int)->dict:
        payload = {
            'reg0': int(numberOfAverage),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_ScanNumberOfAverages.value,payload)
        response = command.execute_post()
        return response

    @ExceptionLoggerAPIResponse
    def Set_NumberOfScans(self,numberOfScan:int)->dict:
        payload = {
            'reg0': int(numberOfScan),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_NumberOfScans.value,payload)
        response = command.execute_post()
        return response

    @ExceptionLoggerAPIResponse
    def Set_OffsetPosition(self,offsetPosition:str)->dict:
        payload = {
            'reg0': str(offsetPosition),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_OffsetPosition.value,payload)
        response = command.execute_post()
        return response

    @ExceptionLoggerAPIResponse
    def Set_ScanDirection(self,scanDirection:str)->dict:
        payload = {
            'reg0': str(scanDirection),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_ScanDirection.value,payload)
        response = command.execute_post()
        return response

    @ExceptionLoggerAPIResponse
    def Set_IsRoundtripScan(self,isRoundtripScan:bool)->dict:
        payload = {
            'reg0': bool(isRoundtripScan),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_IsRoundtripScan.value,payload)
        response = command.execute_post()
        return response

    @ExceptionLoggerAPIResponse
    def Set_IsSaveScannedImages(self,isSaveImages:bool)->dict:
        payload = {
            'reg0': bool(isSaveImages),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_IsSaveScannedImages.value,payload)
        response = command.execute_post()
        return response


    @ExceptionLoggerAPIResponse
    def StartScan(self,status:bool)->dict:
        payload = {
            'reg0': bool(status),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.StartScan.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def StopScan(self,status:bool)->dict:
        payload = {
            'reg0': bool(status),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.StopScan.value,payload)
        response = command.execute_post()
        return response