from hpSPMPlusStudio.NMIImporter.BuiltInImporter import*
from hpSPMPlusStudio.NMIImporter.Decarators import*
from hpSPMPlusStudio.RequestManager.NMIEndpoint import NMIEndpoint
from hpSPMPlusStudio.RequestManager.NMICommand import NMICommand

PREFIX = "Options"

class GET_Commands(Enum):
    Get_Commands = "Get_Commands"
    
    Get_SPMType = "Get_SPMType"
    Get_AFMMode = "Get_AFMMode"
    Get_SPMTypeList = "Get_SPMTypeList"
    Get_AFMModeList = "Get_AFMModeList"
    Get_ScaleList = "Get_ScaleList"
    Get_XYScale = "Get_XYScale"
    Get_ZScale = "Get_ZScale"
    

class SET_Commands(Enum):
    Set_SPMType = "Set_SPMType"
    Set_AFMMode = "Set_AFMMode"
    Set_XYScale = "Set_XYScale"
    Set_ZScale = "Set_ZScale"

  

class OptionsController:
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
    def Get_SPMTypeList(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_SPMTypeList.value)
        response = command.execute_get()
        return response

    @ExceptionLoggerAPIResponse
    def Get_AFMModeList(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_AFMModeList.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse   
    def Get_SPMType(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_SPMType.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_AFMMode(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_AFMMode.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_ScaleList(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_ScaleList.value)
        response = command.execute_get()
        return response

    @ExceptionLoggerAPIResponse
    def Get_XYScale(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_XYScale.value)
        response = command.execute_get()
        return response

    @ExceptionLoggerAPIResponse
    def Get_ZScale(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_ZScale.value)
        response = command.execute_get()
        return response

    @ExceptionLoggerAPIResponse
    def Set_SPMType(self,spmType:str)->dict:
        payload = {
            'reg0': str(spmType),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_SPMType.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_AFMMode(self,afmMode:str)->dict:
        payload = {
            'reg0': str(afmMode),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_AFMMode.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_XYScale(self,scale:str)->dict:
        payload = {
            'reg0': str(scale),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_XYScale.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_ZScale(self,scale:str)->dict:
        payload = {
            'reg0': str(scale),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_ZScale.value,payload)
        response = command.execute_post()
        return response