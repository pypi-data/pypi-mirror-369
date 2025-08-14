from hpSPMPlusStudio.NMIImporter.BuiltInImporter import*
from hpSPMPlusStudio.NMIImporter.Decarators import*
from hpSPMPlusStudio.RequestManager.NMIEndpoint import NMIEndpoint
from hpSPMPlusStudio.RequestManager.NMICommand import NMICommand

PREFIX = "XYOffset"
class GET_Commands(Enum):
    Get_Commands                = "Get_Commands"
    Get_IsOffsetUpdateAvailable = "Get_IsOffsetUpdateAvailable"
    Get_XOffset                 = "Get_XOffset"
    Get_YOffset                 = "Get_YOffset"
    Get_XYOffset                = "Get_XYOffset"
    Get_XOffsetLimit            = "Get_XOffsetLimit"
    Get_YOffsetLimit            = "Get_YOffsetLimit"
    Get_XYOffsetLimit           = "Get_XYOffsetLimit"

class SET_Commands(Enum):
    Set_XOffset         = "Set_XOffset"
    Set_YOffset         = "Set_YOffset"
    Set_XYOffset        = "Set_XYOffset"
    Set_DirectXOffset   = "Set_DirectXOffset"
    Set_DirectYOffset   = "Set_DirectYOffset"

    Start_GuiOffsetUpdater = "Start_GuiOffsetUpdater"
    Stop_GuiOffsetUpdater  = "Stop_GuiOffsetUpdater"

    

class XYOffsetController:
    def __init__(self,endpoint:NMIEndpoint) -> None:
        self.Endpoint = endpoint

    @ExceptionLoggerAPIResponse
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
    def Get_IsOffsetUpdateAvailable(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_IsOffsetUpdateAvailable.value)
        response = command.execute_get()
        return response

    
    @ExceptionLoggerAPIResponse
    def Get_XOffset(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_XOffset.value)
        response = command.execute_get()
        return response

    @ExceptionLoggerAPIResponse
    def Get_YOffset(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_YOffset.value)
        response = command.execute_get()
        return response

    @ExceptionLoggerAPIResponse
    def Get_XYOffset(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_XYOffset.value)
        response = command.execute_get()
        return response

    @ExceptionLoggerAPIResponse
    def Get_XOffsetLimit(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_XOffsetLimit.value)
        response = command.execute_get()
        return response

    @ExceptionLoggerAPIResponse
    def Get_YOffsetLimit(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_YOffsetLimit.value)
        response = command.execute_get()
        return response

    @ExceptionLoggerAPIResponse
    def Get_XYOffsetLimit(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_XYOffsetLimit.value)
        response = command.execute_get()
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
    def Set_DirectXOffset(self,yOffset:float)->dict:
        payload = {
            'reg0': float(yOffset),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_DirectXOffset.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_DirectYOffset(self,yOffset:float)->dict:
        payload = {
            'reg0': float(yOffset),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_DirectYOffset.value,payload)
        response = command.execute_post()
        return response

    @ExceptionLoggerAPIResponse
    def Set_XYOffset(self,xOffset:float,yOffset:float)->dict:
        payload = {
            'reg0': float(xOffset),
            'reg1': float(yOffset),
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_XYOffset.value,payload)
        response = command.execute_post()
        return response

    @ExceptionLoggerAPIResponse
    def Start_GuiOffsetUpdater(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Start_GuiOffsetUpdater.value)
        response = command.execute_post()
        return response

    @ExceptionLoggerAPIResponse
    def Stop_GuiOffsetUpdater(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Stop_GuiOffsetUpdater.value)
        response = command.execute_post()
        return response