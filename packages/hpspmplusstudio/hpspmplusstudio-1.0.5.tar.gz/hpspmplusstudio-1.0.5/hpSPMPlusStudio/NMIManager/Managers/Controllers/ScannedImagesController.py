from hpSPMPlusStudio.NMIImporter.BuiltInImporter import*
from hpSPMPlusStudio.NMIImporter.Decarators import*
from hpSPMPlusStudio.RequestManager.NMIEndpoint import NMIEndpoint
from hpSPMPlusStudio.RequestManager.NMICommand import NMICommand

PREFIX = "ScannedImages"

class GET_Commands(Enum):
    Get_Commands = "Get_Commands"
    Get_NmiContainerList = "Get_NmiContainerList"
    Get_SelectedContainerImageList = "Get_SelectedContainerImageList"
    Get_SelectedContainerForwardImageList = "Get_SelectedContainerForwardImageList"
    Get_SelectedContainerBackwardImageList = "Get_SelectedContainerBackwardImageList"
    Get_SelectedContainerImage = "Get_SelectedContainerImage"

class SET_Commands(Enum):
    pass

class ScannedImagesController:
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
    def Get_NmiContainers(self)->list:
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_NmiContainerList.value)
        response = command.execute_get()
        if("NmiContainerList" in response):
            return response["NmiContainerList"].split(';')
        else:
            return []
    
    @ExceptionLoggerAPIResponse
    def Get_SelectedContainerImageList(self,containerName:str)->list:
        payload = {
            'reg0': str(containerName),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_SelectedContainerImageList.value,payload)
        response = command.execute_post()
        if("SelectedContainerImageList" in response):
            return response["SelectedContainerImageList"].split(';')
        else:
            return []

    @ExceptionLoggerAPIResponse   
    def Get_SelectedContainerForwardImageList(self,containerName:str)->list:
        payload = {
            'reg0': str(containerName),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_SelectedContainerForwardImageList.value,payload)
        response = command.execute_post()
        if("SelectedContainerForwardImageList" in response):
            return response["SelectedContainerForwardImageList"].split(';')
        else:
            return []
    
    @ExceptionLoggerAPIResponse
    def Get_SelectedContainerBackwardImageList(self,containerName:str)->list:
        payload = {
            'reg0': str(containerName),
            'reg1': "",
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_SelectedContainerBackwardImageList.value,payload)
        response = command.execute_post()
        if("SelectedContainerBackwardImageList" in response):
            return response["SelectedContainerBackwardImageList"].split(';')
        else:
            return []

    @ExceptionLoggerAPIResponse  
    def Get_SelectedContainerImage(self,containerName:str,imageName:str)->dict:
        payload = {
            'reg0': str(containerName),
            'reg1': str(imageName),
            'reg2': "",
            'reg3': "",
        }
        command = NMICommand(self.Endpoint,PREFIX,GET_Commands.Get_SelectedContainerImage.value,payload)
        response = command.execute_post()
        return response