from hpSPMPlusStudio.NMIImporter.BuiltInImporter import*
from hpSPMPlusStudio.NMIImporter.Decarators import*
from hpSPMPlusStudio.RequestManager.NMIEndpoint import NMIEndpoint
from hpSPMPlusStudio.RequestManager.NMICommand import NMICommand

PREFIX = "VBias"

class GET_Commands(Enum):
    Get_Commands = "Get_Commands"   
    Get_DCOffset = "Get_DCOffset"
    Get_MinDCOffset = "Get_MinDCOffset"
    Get_MaxDCOffset = "Get_MaxDCOffset"
    Get_ACAmplitude = "Get_ACAmplitude"
    Get_ACFrequency = "Get_ACFrequency"
      
class SET_Commands(Enum):
    Set_DCOffset = "Set_DCOffset"
    Set_ACAmplitude = "Set_ACAmplitude"
    Set_ACFrequency = "Set_ACFrequency"
 

class VBiasController:
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
    def Get_DCOffset(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_DCOffset.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_MinDCOffset(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_MinDCOffset.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_MaxDCOffset(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_MaxDCOffset.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_ACAmplitude(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_ACAmplitude.value)
        response = command.execute_get()
        return response

    @ExceptionLoggerAPIResponse
    def Get_ACFrequency(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_ACFrequency.value)
        response = command.execute_get()
        return response
    
  
    @ExceptionLoggerAPIResponse
    def Set_DCOffset(self,dcOffset:float)->dict:
        payload = {
            'reg0': float(dcOffset),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_DCOffset.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_ACAmplitude(self,amplitude:float)->dict:
        payload = {
            'reg0': float(amplitude),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_ACAmplitude.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_ACFrequency(self,frequency:float)->dict:
        payload = {
            'reg0': float(frequency),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_ACFrequency.value,payload)
        response = command.execute_post()
        return response

    
   