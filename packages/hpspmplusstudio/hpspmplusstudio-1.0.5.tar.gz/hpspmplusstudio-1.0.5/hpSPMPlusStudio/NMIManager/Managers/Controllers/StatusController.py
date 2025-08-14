from hpSPMPlusStudio.NMIImporter.BuiltInImporter import*
from hpSPMPlusStudio.NMIImporter.Decarators import*
from hpSPMPlusStudio.RequestManager.NMIEndpoint import NMIEndpoint
from hpSPMPlusStudio.RequestManager.NMICommand import NMICommand

PREFIX = "APP"

class GET_Commands(Enum):
    Get_Commands = "Get_Commands"
    Get_Status = "Get_Status"
    DeviceInformations = "DeviceInformations"
    Get_DashboardStatus = "Get_DashboardStatus"

class SET_Commands(Enum):
    pass


class StatusController:
    def __init__(self,endpoint:NMIEndpoint) -> None:
        self.Endpoint = endpoint

    def Get_Commands(self)->list:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_Commands.value)
        response = command.execute_get()
        if("Commands" in response):
            return response["Commands"].split(';')
        else:
            return []

    @ExceptionLoggerAPIResponse  
    def Get_DashboardStatus(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_DashboardStatus.value)
        response = command.execute_get()
        return response
    
    @ExceptionLoggerAPIResponse
    def Get_Status(self)->str:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_Status.value)
        response = command.execute_get()
        if("SystemStatus" in response):
            return response["SystemStatus"]
        else:
            return ""