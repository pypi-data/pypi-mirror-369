from hpSPMPlusStudio.NMIImporter.BuiltInImporter import*
from hpSPMPlusStudio.NMIImporter.Decarators import*
from hpSPMPlusStudio.RequestManager.NMIEndpoint import NMIEndpoint
from hpSPMPlusStudio.RequestManager.NMICommand import NMICommand

PREFIX = "WindowControl"

class GET_Commands(Enum):
    Get_Commands = "Get_Commands"
    
    Get_IsOpened = "Get_IsOpened"
    Get_OpenedWindows = "Get_OpenedWindows"
    
    

class SET_Commands(Enum):
    Set_MinimizeWindow = "Set_MinimizeWindow"
    Set_MaximizeWindow = "Set_MaximizeWindow"
    Set_MinimizeAll = "Set_MinimizeAll"
    Set_NormalizeAll = "Set_NormalizeAll"
    Set_CloseAll = "Set_CloseAll"
    Set_CloseWindow = "Set_CloseWindow"

  
class WindowController:
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
    def Get_OpenedWindows(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_OpenedWindows.value)
        response = command.execute_get()
        return response

    @ExceptionLoggerAPIResponse
    def Get_IsOpened(self,windowTitle:str)->dict:
        payload = {
            'reg0': str(windowTitle),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_IsOpened.value,payload)
        response = command.execute_post()
        return response


    @ExceptionLoggerAPIResponse
    def Set_MinimizeWindow(self,windowTitle:str)->dict:
        payload = {
            'reg0': str(windowTitle),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_MinimizeWindow.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_MaximizeWindow(self,windowTitle:str)->dict:
        payload = {
            'reg0': str(windowTitle),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_MaximizeWindow.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_CloseWindow(self,windowTitle:str)->dict:
        payload = {
            'reg0': str(windowTitle),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_CloseWindow.value,payload)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_MinimizeAll(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_MinimizeAll.value)
        response = command.execute_post()
        return response
    
    @ExceptionLoggerAPIResponse
    def Set_NormalizeAll(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,SET_Commands.Set_NormalizeAll.value)
        response = command.execute_post()
        return response