from hpSPMPlusStudio.NMIImporter.BuiltInImporter import*
from hpSPMPlusStudio.NMIImporter.Decarators import*
from hpSPMPlusStudio.RequestManager.NMIEndpoint import NMIEndpoint
from hpSPMPlusStudio.RequestManager.NMICommand import NMICommand

PREFIX = "Approach"

class GET_Commands(Enum):
    Get_Commands = "Get_Commands"   
    Get_IsInit = "Get_IsInit"
    Get_AdjustableDistanceType = "Get_AdjustableDistanceType"
    Get_SpeedType = "Get_SpeedType"

    Get_StepCountX = "Get_StepCountX"
    Get_StepCountY = "Get_StepCountY"
    Get_StepCountZ = "Get_StepCountZ"
    
class SET_Commands(Enum):
    Set_Initialize = "Set_Initialize"
    Set_AxisType = "Set_AxisType"
    Set_AdjustableDistanceType = "Set_AdjustableDistanceType"
    Set_SpeedType = "Set_SpeedType"
    Set_MoveUp = "Set_MoveUp"
    Set_MoveDown = "Set_MoveDown"
    Set_MoveLeft = "Set_MoveLeft"
    Set_MoveRight = "Set_MoveRight"
    Set_MoveForward = "Set_MoveForward"
    Set_MoveBackward = "Set_MoveBackward"
    Set_Stop = "Set_Stop"
   
    
class ApproachController:
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
    def Get_AdjustableDistanceType(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_AdjustableDistanceType.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_SpeedType(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_SpeedType.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_StepCountX(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_StepCountX.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_StepCountY(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_StepCountY.value)
        response = command.execute_get()
        return response

    @ExceptionLoggerAPIResponse
    def Get_StepCountZ(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_StepCountZ.value)
        response = command.execute_get()
        return response

    @ExceptionLoggerAPIResponse
    def Set_Initialize(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_Initialize.value)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_AxisType_Sample(self)->dict:
        payload = {
            'reg0': str("Approach-Sample"),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_AxisType.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_AxisType_Objective(self)->dict:
        payload = {
            'reg0': str("Approach-Objective"),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_AxisType.value,payload)
        response = command.execute_post()
        return response
    

    @ExceptionLoggerAPIResponse
    def Set_AdjustableDistanceType(self, distance_type:str)->dict:
        payload = {
            'reg0': str(distance_type),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_AdjustableDistanceType.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_SpeedType(self, speed_type:str)->dict:
        payload = {
            'reg0': str(speed_type),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_SpeedType.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_MoveUp(self)->dict:
        payload = {
            'reg0': str("Approach-MoveUp"),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_MoveUp.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_MoveDown(self)->dict:
        payload = {
            'reg0': str("Approach-MoveDown"),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_MoveDown.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_MoveLeft(self)->dict:
        payload = {
            'reg0': str("Approach-MoveLeft"),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_MoveLeft.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_MoveRight(self)->dict:
        payload = {
            'reg0': str("Approach-MoveRight"),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_MoveRight.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_MoveForward(self)->dict:
        payload = {
            'reg0': str("Approach-MoveForward"),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_MoveForward.value,payload)
        response = command.execute_post()
        return response 
    
    @ExceptionLoggerAPIResponse
    def Set_MoveBackward(self)->dict:
        payload = {
            'reg0': str("Approach-MoveBackward"),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_MoveBackward.value,payload)
        response = command.execute_post()
        return response

    @ExceptionLoggerAPIResponse
    def Set_Stop(self)->dict:
        payload = {
            'reg0': str("Approach-Stop"),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_Stop.value,payload)
        response = command.execute_post()
        return response
        