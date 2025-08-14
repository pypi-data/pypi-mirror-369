from hpSPMPlusStudio.NMIImporter.BuiltInImporter import*
from hpSPMPlusStudio.NMIImporter.Decarators import*
from hpSPMPlusStudio.RequestManager.NMIEndpoint import NMIEndpoint
from hpSPMPlusStudio.RequestManager.NMICommand import NMICommand

PREFIX = "PhotoDiode"

class GET_Commands(Enum):
    Get_Commands                = "Get_Commands"
    Get_IsLaserEnabled = "Get_IsLaserEnabled"
    Get_LaserPower                 = "Get_LaserPower"
    Get_LaserRF_Frequency                 = "Get_LaserRF_Frequency"
    Get_FN10                = "Get_FN10"
    Get_FN            = "Get_FN"
    Get_FL            = "Get_FL"
    Get_FT           = "Get_FT"

class SET_Commands(Enum):
    Set_LaserEnable = "Set_LaserEnable"
    Set_LaserDisable = "Set_LaserDisable"
    Set_LaserPower         = "Set_LaserPower"
    Set_LaserRF_Frequency         = "Set_LaserRF_Frequency"
    NullFL   = "NullFL"
    Null10FN = "Null10FN"
    PhotoDiodeReset = "PhotoDiodeReset"

    

class PhotoDiodeController:
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
    def Get_IsLaserEnabled(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_IsLaserEnabled.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_LaserPower(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_LaserPower.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_LaserRF_Frequency(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_LaserRF_Frequency.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_FN10(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_FN10.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_FN(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_FN.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_FL(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_FL.value)
        response = command.execute_get()
        return response
    @ExceptionLoggerAPIResponse
    def Get_FT(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_FT.value)
        response = command.execute_get()
        return response


    @ExceptionLoggerAPIResponse
    def Set_LaserPower(self,power:float)->dict:
        payload = {
            'reg0': float(power),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_LaserPower.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_LaserRF_Frequency(self,rf:float)->dict:
        payload = {
            'reg0': float(rf),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_LaserRF_Frequency.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def NullFL(self)->dict:
        payload = {
            'reg0': "",
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.NullFL.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Null10FN(self)->dict:
        payload = {
            'reg0': "",
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Null10FN.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def PhotoDiodeReset(self)->dict:
        payload = {
            'reg0': "",
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.PhotoDiodeReset.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_LaserEnable(self)->dict:
        payload = {
            'reg0': "",
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_LaserEnable.value,payload)
        response = command.execute_post()
        return response
    @ExceptionLoggerAPIResponse
    def Set_LaserDisable(self)->dict:
        payload = {
            'reg0': "",
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_LaserDisable.value,payload)
        response = command.execute_post()
        return response

    

    