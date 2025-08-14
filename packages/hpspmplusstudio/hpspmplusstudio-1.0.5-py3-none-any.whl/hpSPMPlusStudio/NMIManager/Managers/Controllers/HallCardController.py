from hpSPMPlusStudio.NMIImporter.BuiltInImporter import*
from hpSPMPlusStudio.NMIImporter.Decarators import*
from hpSPMPlusStudio.RequestManager.NMIEndpoint import NMIEndpoint
from hpSPMPlusStudio.RequestManager.NMICommand import NMICommand

PREFIX = "HallCard"

class GET_Commands(Enum):
    Get_Commands = "Get_Commands"   
    Get_IsHallProbeEnabled = "Get_IsHallProbeEnabled"
    Get_IsInfraRedLedOn = "Get_IsInfraRedLedOn"
    Get_IHallRange = "Get_IHallRange"
    Get_IHall = "Get_IHall"
    Get_IHallOffset = "Get_IHallOffset"
    Get_RHall = "Get_RHall"
    Get_VHall = "Get_VHall"
    Get_BHall = "Get_BHall"
    Get_HallAmplitudeGain = "Get_HallAmplitudeGain"
    Get_HallAmplitudeBandwith = "Get_HallAmplitudeBandwith"
    Get_CoilVoltage = "Get_CoilVoltage"
    Get_CoilVoltageRate = "Get_CoilVoltageRate"
    

class SET_Commands(Enum):
    Set_IHall = "Set_IHall"
    Set_IHallOffset = "Set_IHallOffset"
    Set_RHall = "Set_RHall"
    Set_EnableHallProbe = "Set_EnableHallProbe"
    Set_DisableHallProbe = "Set_DisableHallProbe"
    Set_EnableIRLed = "Set_EnableIRLed"
    Set_DisableIRLed = "Set_DisableIRLed"
    Set_HallAmplitudeGain = "Set_HallAmplitudeGain"
    Set_HallAmplitudeBandwidth = "Set_HallAmplitudeBandwidth"
    Set_CoilVoltage = "Set_CoilVoltage"
    Set_CoilVoltageRate = "Set_CoilVoltageRate"

    NullHallOffset = "NullHallOffset"
    

class HallCardController:
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
    def Get_IsHallProbeEnabled(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_IsHallProbeEnabled.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_IsInfraRedLedOn(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_IsInfraRedLedOn.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_IHallRange(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_IHallRange.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_IHall(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_IHall.value)
        response = command.execute_get()
        return response

    @ExceptionLoggerAPIResponse
    def Get_IHallOffset(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_IHallOffset.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_RHall(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_RHall.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_VHall(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_VHall.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_BHall(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_BHall.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_HallAmplitudeGain(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_HallAmplitudeGain.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_HallAmplitudeBandwith(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_HallAmplitudeBandwith.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_CoilVoltage(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_CoilVoltage.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_CoilVoltageRate(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_CoilVoltageRate.value)
        response = command.execute_get()
        return response
    
  
    @ExceptionLoggerAPIResponse
    def Set_IHall(self,current:float)->dict:
        payload = {
            'reg0': str(current),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_IHall.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_IHallOffset(self,offset:float)->dict:
        payload = {
            'reg0': str(offset),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_IHallOffset.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_RHall(self,rhall:float)->dict:
        payload = {
            'reg0': float(rhall),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_RHall.value,payload)
        response = command.execute_post()
        return response

    @ExceptionLoggerAPIResponse
    def Set_EnableHallProbe(self)->dict:
        payload = {
            'reg0': "",
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_EnableHallProbe.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_DisableHallProbe(self)->dict:
        payload = {
            'reg0': "",
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_DisableHallProbe.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_EnableIRLed(self)->dict:
        payload = {
            'reg0': "",
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_EnableIRLed.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_DisableIRLed(self)->dict:
        payload = {
            'reg0': "",
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_DisableIRLed.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_HallAmplitudeGain(self,gain:int)->dict:
        payload = {
            'reg0': int(gain),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_HallAmplitudeGain.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_HallAmplitudeBandwidth(self,bandwidth:int)->dict:
        payload = {
            'reg0': int(bandwidth),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_HallAmplitudeBandwidth.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_CoilVoltage(self,voltage:float)->dict:
        payload = {
            'reg0': float(voltage),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_CoilVoltage.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_CoilVoltageRate(self,rate:float)->dict:
        payload = {
            'reg0': float(rate),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_CoilVoltageRate.value,payload)
        response = command.execute_post()
        return response
    

    @ExceptionLoggerAPIResponse
    def NullHallOffset(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.NullHallOffset.value)
        response = command.execute_post()
        return response
    
   