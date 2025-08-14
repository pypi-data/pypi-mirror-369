from hpSPMPlusStudio.NMIImporter.BuiltInImporter import*
from hpSPMPlusStudio.NMIImporter.Decarators import*
from hpSPMPlusStudio.RequestManager.NMIEndpoint import NMIEndpoint
from hpSPMPlusStudio.RequestManager.NMICommand import NMICommand

PREFIX = "SystemReadings"

class GET_Commands(Enum):
    Get_Commands = "Get_Commands"
    Get_SystemReadings = "Get_SystemReadings"
    Get_SystemReadingsUnitText = "Get_SystemReadingsUnitText"

class SET_Commands(Enum):
    pass


class SystemReadingsController:
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
    def Get_SystemReadings(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_SystemReadings.value)
        response = command.execute_get()
        return response

    @ExceptionLoggerAPIResponse
    def Get_SystemReadingsUnitText(self)->dict:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_SystemReadingsUnitText.value)
        response = command.execute_get()
        return response