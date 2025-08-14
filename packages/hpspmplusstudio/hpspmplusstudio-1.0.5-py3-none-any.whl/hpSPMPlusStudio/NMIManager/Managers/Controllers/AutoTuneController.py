from hpSPMPlusStudio.NMIImporter.BuiltInImporter import*
from hpSPMPlusStudio.NMIImporter.Decarators import*
from hpSPMPlusStudio.RequestManager.NMIEndpoint import NMIEndpoint
from hpSPMPlusStudio.RequestManager.NMICommand import NMICommand

PREFIX = "AutoTune"

class GET_Commands(Enum):
    Get_Commands = "Get_Commands"   
    Get_IsInit = "Get_IsInit"
    Get_IsTunning = "Get_IsTunning"
    Get_FrequencySlopeTypes = "Get_FrequencySlopeTypes"
    Get_IsCenterSpan = "Get_IsCenterSpan"
    Get_ExcitationPercent = "Get_ExcitationPercent"
    Get_Excitation = "Get_Excitation"
    Get_FrequencyStartInHertz = "Get_FrequencyStartInHertz"
    Get_FrequencyEndInHertz = "Get_FrequencyEndInHertz"
    Get_FrequencyIncrementInHertz = "Get_FrequencyIncrementInHertz"
    Get_Delay = "Get_Delay"
    Get_StartDelay = "Get_StartDelay"
    Get_FrequencySlopeType = "Get_FrequencySlopeType"
    Get_MaxSlopeFrequency = "Get_MaxSlopeFrequency"
    Get_MaxSlopeRms = "Get_MaxSlopeRms"
    Get_MinSlopeFrequency = "Get_MinSlopeFrequency"
    Get_MinSlopeRms = "Get_MinSlopeRms"
    Get_MaxRmsFrequency = "Get_MaxRmsFrequency"
    Get_MaxRms = "Get_MaxRms"
    Get_CoarseRmsSeries = "Get_CoarseRmsSeries"
    Get_CoarsePhaseSeries = "Get_CoarsePhaseSeries"
    Get_FineRmsSeries = "Get_FineRmsSeries"
    Get_FinePhaseSeries = "Get_FinePhaseSeries"



class SET_Commands(Enum):
    Set_Initialize = "Set_Initialize"
    Set_ExcitationPercent = "Set_ExcitationPercent"
    Set_Excitation = "Set_Excitation"
    Set_FrequencyStartInHertz = "Set_FrequencyStartInHertz"
    Set_FrequencyEndInHertz = "Set_FrequencyEndInHertz"
    Set_FrequencyIncrementInHertz = "Set_FrequencyIncrementInHertz"
    Set_Delay = "Set_Delay"
    Set_StartDelay = "Set_StartDelay"
    Set_CenterSpanType = "Set_CenterSpanType"
    Set_StartEndType = "Set_StartEndType"
    Set_FrequencySlope = "Set_FrequencySlope"
    StartTune = "StartTune"
    StopTune = "StopTune"
    

class AutoTuneController:
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
    def Get_IsTunning(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_IsTunning.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_FrequencySlopeTypes(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_FrequencySlopeTypes.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_FrequencySlopeType(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_FrequencySlopeType.value)
        response = command.execute_get()
        return response

    @ExceptionLoggerAPIResponse
    def Get_IsCenterSpan(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_IsCenterSpan.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_ExcitationPercent(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_ExcitationPercent.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_Excitation(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_Excitation.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_FrequencyStartInHertz(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_FrequencyStartInHertz.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_FrequencyEndInHertz(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_FrequencyEndInHertz.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_FrequencyIncrementInHertz(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_FrequencyIncrementInHertz.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_Delay(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_Delay.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_StartDelay(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_StartDelay.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_MaxSlopeFrequency(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_MaxSlopeFrequency.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_MaxSlopeRms(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_MaxSlopeRms.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_MinSlopeFrequency(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_MinSlopeFrequency.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_MinSlopeRms(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_MinSlopeRms.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_MaxRmsFrequency(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_MaxRmsFrequency.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_MaxRms(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_MaxRms.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_CoarseRmsSeries(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_CoarseRmsSeries.value)
        response = command.execute_get()
        return response

    @ExceptionLoggerAPIResponse
    def Get_CoarsePhaseSeries(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_CoarsePhaseSeries.value)
        response = command.execute_get()
        return response

    @ExceptionLoggerAPIResponse
    def Get_FineRmsSeries(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_FineRmsSeries.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_FinePhaseSeries(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_FinePhaseSeries.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_Initialize(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_Initialize.value)
        response = command.execute_post()
        return response

   
    @ExceptionLoggerAPIResponse
    def Set_ExcitationPercent(self,excitationPercent:float)->dict:
        payload = {
            'reg0': str(excitationPercent),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_ExcitationPercent.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_Excitation(self,excitation:float)->dict:
        payload = {
            'reg0': str(excitation),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_Excitation.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_FrequencyStartInHertz(self,hertz:float)->dict:
        payload = {
            'reg0': float(hertz),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_FrequencyStartInHertz.value,payload)
        response = command.execute_post()
        return response

    @ExceptionLoggerAPIResponse
    def Set_FrequencyEndInHertz(self,hertz:float)->dict:
        payload = {
            'reg0': float(hertz),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_FrequencyEndInHertz.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_FrequencyIncrementInHertz(self,hertz:float)->dict:
        payload = {
            'reg0': float(hertz),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_FrequencyIncrementInHertz.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_Delay(self,delay:float)->dict:
        payload = {
            'reg0': float(delay),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_Delay.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_StartDelay(self,delay:float)->dict:
        payload = {
            'reg0': float(delay),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_StartDelay.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_CenterSpanType(self)->dict:
        payload = {
            'reg0': "",
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_CenterSpanType.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_StartEndType(self)->dict:
        payload = {
            'reg0': "",
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_StartEndType.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_FrequencySlope(self,slopeType:str)->dict:
        payload = {
            'reg0': str(slopeType),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_FrequencySlope.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def StartTune(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.StartTune.value)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def StopTune(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.StopTune.value)
        response = command.execute_post()
        return response