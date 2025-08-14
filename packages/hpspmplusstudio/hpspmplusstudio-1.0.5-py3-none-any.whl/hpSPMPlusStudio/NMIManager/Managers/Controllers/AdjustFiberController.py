from hpSPMPlusStudio.NMIImporter.BuiltInImporter import*
from hpSPMPlusStudio.NMIImporter.Decarators import*
from hpSPMPlusStudio.RequestManager.NMIEndpoint import NMIEndpoint
from hpSPMPlusStudio.RequestManager.NMICommand import NMICommand

PREFIX = "AdjustFiber"

class GET_Commands(Enum):
    Get_Commands = "Get_Commands"   
    Get_IsRunning = "Get_IsRunning"
    Get_IsInit = "Get_IsInit"
    Get_NumSamples = "Get_NumSamples"
    Get_NumAvg = "Get_NumAvg"
    Get_Delay = "Get_Delay"
    Get_MiddleDelay = "Get_MiddleDelay"
    Get_KFiber = "Get_KFiber"
    Get_SlopeStepSize = "Get_SlopeStepSize"
    Get_SinPeriod = "Get_SinPeriod"
    Get_SlopeModeList = "Get_SlopeModeList"
    Get_SlopeMode = "Get_SlopeMode"
    Get_Gamma = "Get_Gamma"
    Get_MaxPztVoltage = "Get_MaxPztVoltage"
    Get_IsAutoKFiberEnable = "Get_IsAutoKFiberEnable"
    Get_Results = "Get_Results"
    Get_ResultMaxSlope = "Get_ResultMaxSlope"
    Get_ResultMinSlope = "Get_ResultMinSlope"
    Get_ResultQuadraturePointPower = "Get_ResultQuadraturePointPower"
    Get_ResultFiberVoltage = "Get_ResultFiberVoltage"
    Get_ResultFiberPosition = "Get_ResultFiberPosition"
    Get_ResultLaserPower = "Get_ResultLaserPower"
    Get_ResultFinesse = "Get_ResultFinesse"
    Get_ResultVisibility = "Get_ResultVisibility"
    Get_ForwardDataList = "Get_ForwardDataList"
    Get_ForwardSlopeDataList = "Get_ForwardSlopeDataList"
    Get_BackwardDataList = "Get_BackwardDataList"
    Get_BackwardSlopeDataList = "Get_BackwardSlopeDataList"



class SET_Commands(Enum):
    Set_NumSamples = "Set_NumSamples"
    Set_NumAvg = "Set_NumAvg"
    Set_Delay = "Set_Delay"
    Set_MiddleDelay = "Set_MiddleDelay"
    Set_KFiber = "Set_KFiber"
    Set_SlopeStepSize = "Set_SlopeStepSize"
    Set_SlopeMode = "Set_SlopeMode"
    Set_Gamma = "Set_Gamma"
    Set_AutoKFiberEnable = "Set_AutoKFiberEnable"
    Set_AutoKFiberDisable = "Set_AutoKFiberDisable"
    Set_Initialize = "Set_Initialize"

    FindQuadrature = "FindQuadrature"
    Stop = "Stop"
    

class AdjustFiberController:
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
    def Get_IsInit(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_IsInit.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_IsRunning(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_IsRunning.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_NumSamples(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_NumSamples.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_NumAvg(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_NumAvg.value)
        response = command.execute_get()
        return response

    @ExceptionLoggerAPIResponse
    def Get_Delay(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_Delay.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_MiddleDelay(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_MiddleDelay.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_KFiber(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_KFiber.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_SlopeStepSize(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_SlopeStepSize.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_SinPeriod(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_SinPeriod.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_SlopeModeList(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_SlopeModeList.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_SlopeMode(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_SlopeMode.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_Gamma(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_Gamma.value)
        response = command.execute_get()
        return response
    
    
    @ExceptionLoggerAPIResponse
    def Get_MaxPztVoltage(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_MaxPztVoltage.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_IsAutoKFiberEnable(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_IsAutoKFiberEnable.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_Results(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_Results.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_ResultMaxSlope(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_ResultMaxSlope.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_ResultMinSlope(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_ResultMinSlope.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_ResultQuadraturePointPower(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_ResultQuadraturePointPower.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_ResultFiberVoltage(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_ResultFiberVoltage.value)
        response = command.execute_get()
        return response

    @ExceptionLoggerAPIResponse
    def Get_ResultFiberPosition(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_ResultFiberPosition.value)
        response = command.execute_get()
        return response

    @ExceptionLoggerAPIResponse
    def Get_ResultLaserPower(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_ResultLaserPower.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_ResultFinesse(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_ResultFinesse.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_ResultVisibility(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_ResultVisibility.value)
        response = command.execute_get()
        return response


    @ExceptionLoggerAPIResponse
    def Get_ForwardDataList(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_ForwardDataList.value)
        response = command.execute_get()
        return response

    @ExceptionLoggerAPIResponse
    def Get_ForwardSlopeDataList(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_ForwardSlopeDataList.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_BackwardDataList(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_BackwardDataList.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_BackwardSlopeDataList(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_BackwardSlopeDataList.value)
        response = command.execute_get()
        return response


    @ExceptionLoggerAPIResponse
    def Set_Initialize(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_Initialize.value)
        response = command.execute_post()
        return response

   
    @ExceptionLoggerAPIResponse
    def Set_NumSamples(self,numSample:int)->dict:
        payload = {
            'reg0': int(numSample),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_NumSamples.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_NumAvg(self,numAvg:int)->dict:
        payload = {
            'reg0': int(numAvg),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_NumAvg.value,payload)
        response = command.execute_post()
        return response

    @ExceptionLoggerAPIResponse
    def Set_Delay(self,delay:int)->dict:
        payload = {
            'reg0': int(delay),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_Delay.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_MiddleDelay(self,middleDelay:int)->dict:
        payload = {
            'reg0': int(middleDelay),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_MiddleDelay.value,payload)
        response = command.execute_post()
        return response

    @ExceptionLoggerAPIResponse
    def Set_KFiber(self,kFiber:float)->dict:
        payload = {
            'reg0': float(kFiber),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_KFiber.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_SlopeStepSize(self,slopeStepSize:int)->dict:
        payload = {
            'reg0': int(slopeStepSize),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_SlopeStepSize.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_SlopeMode(self,slopeMode:str)->dict:
        payload = {
            'reg0': str(slopeMode),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_SlopeMode.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_Gamma(self,gamma:float)->dict:
        payload = {
            'reg0': float(gamma),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_Gamma.value,payload)
        response = command.execute_post()
        return response


    @ExceptionLoggerAPIResponse
    def Set_AutoKFiberEnable(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_AutoKFiberEnable.value)
        response = command.execute_post()
        return response

    @ExceptionLoggerAPIResponse
    def Set_AutoKFiberDisable(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_AutoKFiberDisable.value)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_Initialize(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_Initialize.value)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def FindQuadrature(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.FindQuadrature.value)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Stop(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Stop.value)
        response = command.execute_post()
        return response





