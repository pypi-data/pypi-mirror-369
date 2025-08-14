from hpSPMPlusStudio.NMIImporter.BuiltInImporter import*
from hpSPMPlusStudio.NMIImporter.Decarators import*
from hpSPMPlusStudio.RequestManager.NMIEndpoint import NMIEndpoint
from hpSPMPlusStudio.RequestManager.NMICommand import NMICommand

PREFIX = "FiberCard"

class GET_Commands(Enum):
    Get_Commands = "Get_Commands"   
    Get_IsLaserOn = "Get_IsLaserOn"
    Get_IsLaserFanOn = "Get_IsLaserFanOn"
    Get_LaserPowerSetPoint = "Get_LaserPowerSetPoint"
    Get_LaserPower = "Get_LaserPower"
    Get_IsRFModulatorOn = "Get_IsRFModulatorOn"
    Get_RFModulatorFrequencyDigiPOT = "Get_RFModulatorFrequencyDigiPOT"
    Get_RFModulatorAmplitudeDigiPOT = "Get_RFModulatorAmplitudeDigiPOT"
    Get_SignalPhotoDiodeGain = "Get_SignalPhotoDiodeGain"
    Get_ReferancePhotoDiodeGain = "Get_ReferancePhotoDiodeGain"
    Get_FiberPZTVoltage = "Get_FiberPZTVoltage"
    Get_QuadlockStatus = "Get_QuadlockStatus"
    Get_IsEnableQuadlock = "Get_IsEnableQuadlock"
    Get_IsRescanQuadlockEnable = "Get_IsRescanQuadlockEnable"
    
class SET_Commands(Enum):
    Set_LaserEnable = "Set_LaserEnable"
    Set_LaserDisable = "Set_LaserDisable"
    Set_LaserFanEnable = "Set_LaserFanEnable"
    Set_LaserFanDisable = "Set_LaserFanDisable"
    Set_LaserPowerSetPoint = "Set_LaserPowerSetPoint"
    Set_RFModulatorEnable = "Set_RFModulatorEnable"
    Set_RFModulatorDisable = "Set_RFModulatorDisable"
    Set_RFModulatorFrequencyDigiPOT = "Set_RFModulatorFrequencyDigiPOT"
    Set_RFModulatorAmplitudeDigiPOT = "Set_RFModulatorAmplitudeDigiPOT"
    Set_SignalPhotoDiodeGain = "Set_SignalPhotoDiodeGain"
    Set_ReferancePhotoDiodeGain = "Set_ReferancePhotoDiodeGain"
    Set_FiberPZTVoltage = "Set_FiberPZTVoltage"
    Set_QuadlockEnable = "Set_QuadlockEnable"
    Set_QuadlockDisable = "Set_QuadlockDisable"
    Set_RescanQuadlockEnable = "Set_RescanQuadlockEnable"
    Set_RescanQuadlockDisable = "Set_RescanQuadlockDisable"
    NullFiber = "NullFiber"
    

class FiberCardController:
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
    def Get_IsLaserOn(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_IsLaserOn.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_IsLaserFanOn(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_IsLaserFanOn.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_LaserPowerSetPoint(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_LaserPowerSetPoint.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_LaserPower(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_LaserPower.value)
        response = command.execute_get()
        return response

    @ExceptionLoggerAPIResponse
    def Get_IsRFModulatorOn(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_IsRFModulatorOn.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_RFModulatorFrequencyDigiPOT(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_RFModulatorFrequencyDigiPOT.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_RFModulatorAmplitudeDigiPOT(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_RFModulatorAmplitudeDigiPOT.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_SignalPhotoDiodeGain(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_SignalPhotoDiodeGain.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_FiberPZTVoltage(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_FiberPZTVoltage.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_ReferancePhotoDiodeGain(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_ReferancePhotoDiodeGain.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_QuadlockStatus(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_QuadlockStatus.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_IsEnableQuadlock(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_IsEnableQuadlock.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_IsRescanQuadlockEnable(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_IsRescanQuadlockEnable.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_LaserEnable(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_LaserEnable.value)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_LaserDisable(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_LaserDisable.value)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_LaserFanEnable(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_LaserFanEnable.value)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_LaserFanDisable(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_LaserFanDisable.value)
        response = command.execute_post()
        return response

  
    @ExceptionLoggerAPIResponse
    def Set_LaserPowerSetPoint(self,setPoint:float)->dict:
        payload = {
            'reg0': float(setPoint),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_LaserPowerSetPoint.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_RFModulatorEnable(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_RFModulatorEnable.value)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_RFModulatorDisable(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_RFModulatorDisable.value)
        response = command.execute_post()
        return response
    


    @ExceptionLoggerAPIResponse
    def Set_RFModulatorFrequencyDigiPOT(self,digipot:int)->dict:
        payload = {
            'reg0': int(digipot),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_RFModulatorFrequencyDigiPOT.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_RFModulatorAmplitudeDigiPOT(self,digipot:int)->dict:
        payload = {
            'reg0': int(digipot),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_RFModulatorAmplitudeDigiPOT.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_SignalPhotoDiodeGain(self,digipot:int)->dict:
        payload = {
            'reg0': int(digipot),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_SignalPhotoDiodeGain.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_ReferancePhotoDiodeGain(self,digipot:int)->dict:
        payload = {
            'reg0': int(digipot),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_ReferancePhotoDiodeGain.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_FiberPZTVoltage(self,pzt:float)->dict:
        payload = {
            'reg0': float(pzt),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_FiberPZTVoltage.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_QuadlockEnable(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_QuadlockEnable.value)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_QuadlockDisable(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_QuadlockDisable.value)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_RescanQuadlockEnable(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_RescanQuadlockEnable.value)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_RescanQuadlockDisable(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_RescanQuadlockDisable.value)
        response = command.execute_post()
        return response

    @ExceptionLoggerAPIResponse
    def NullFiber(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.NullFiber.value)
        response = command.execute_post()
        return response
    
   