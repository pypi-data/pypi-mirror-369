from hpSPMPlusStudio.NMIImporter.BuiltInImporter import*
from hpSPMPlusStudio.NMIImporter.Decarators import*
from hpSPMPlusStudio.RequestManager.NMIEndpoint import NMIEndpoint
from hpSPMPlusStudio.RequestManager.NMICommand import NMICommand

PREFIX = "PID"

class GET_Commands(Enum):
    Get_Commands = "Get_Commands"
    
    Get_PidTypes = "Get_PidTypes"
    Get_Pid = "Get_Pid"
 
class SET_Commands(Enum):
    Set_Pid_PValue = "Set_Pid_PValue"
    Set_Pid_IValue = "Set_Pid_IValue"
    Set_Pid_DValue = "Set_Pid_DValue"
    Set_Pid_SetValue = "Set_Pid_SetValue"
    Set_Pid_Enable = "Set_Pid_Enable"
    Set_Pid_Disable = "Set_Pid_Disable"
    Set_Pid_NegativePolarity_Enable = "Set_Pid_NegativePolarity_Enable"
    Set_Pid_NegativePolarity_Disable = "Set_Pid_NegativePolarity_Disable"
    Set_Pid_InvertVz_Enable = "Set_Pid_InvertVz_Enable"
    Set_Pid_InvertVz_Disable = "Set_Pid_InvertVz_Disable"

  

class PIDController:
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
    def Get_PidTypes(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_PidTypes.value)
        response = command.execute_get()
        return response

    @ExceptionLoggerAPIResponse
    def Get_PID(self,pidIndex:int)->dict:
        payload = {
            'reg0': str(pidIndex),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_Pid.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_Pid_PValue(self,pidIndex:int,pValue:int)->dict:
        payload = {
            'reg0': str(pidIndex),
            'reg1': str(pValue),
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_Pid_PValue.value,payload)
        response = command.execute_post()
        return response

    @ExceptionLoggerAPIResponse
    def Set_Pid_IValue(self,pidIndex:int,iValue:int)->dict:
        payload = {
            'reg0': str(pidIndex),
            'reg1': str(iValue),
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_Pid_IValue.value,payload)
        response = command.execute_post()
        return response

    @ExceptionLoggerAPIResponse
    def Set_Pid_DValue(self,pidIndex:int,dValue:int)->dict:
        payload = {
            'reg0': str(pidIndex),
            'reg1': str(dValue),
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_Pid_DValue.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_Pid_SetValue(self,pidIndex:int,setValue:float)->dict:
        payload = {
            'reg0': str(pidIndex),
            'reg1': str(setValue),
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_Pid_SetValue.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_Pid_Enable(self,pidIndex:int)->dict:
        payload = {
            'reg0': str(pidIndex),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_Pid_Enable.value,payload)
        response = command.execute_post()
        return response

    @ExceptionLoggerAPIResponse
    def Set_Pid_Disable(self,pidIndex:int)->dict:
        payload = {
            'reg0': str(pidIndex),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_Pid_Disable.value,payload)
        response = command.execute_post()
        return response

    @ExceptionLoggerAPIResponse
    def Set_Pid_NegativePolarity_Enable(self,pidIndex:int)->dict:
        payload = {
            'reg0': str(pidIndex),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_Pid_NegativePolarity_Enable.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_Pid_NegativePolarity_Disable(self,pidIndex:int)->dict:
        payload = {
            'reg0': str(pidIndex),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_Pid_NegativePolarity_Disable.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_Pid_InvertVz_Enable(self,pidIndex:int)->dict:
        payload = {
            'reg0': str(pidIndex),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_Pid_InvertVz_Enable.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_Pid_InvertVz_Disable(self,pidIndex:int)->dict:
        payload = {
            'reg0': str(pidIndex),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_Pid_InvertVz_Disable.value,payload)
        response = command.execute_post()
        return response

    