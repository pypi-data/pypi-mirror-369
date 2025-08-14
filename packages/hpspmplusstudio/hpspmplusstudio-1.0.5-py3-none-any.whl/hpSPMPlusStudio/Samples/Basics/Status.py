from hpSPMPlusStudio import NMICommand,NMIEndpoint,NMIDevice
import time

if __name__ == "__main__":
    # Define the endpoint by specifying the device's IP address and port
    # Ensure the IP and port match the device configuration
    Endpoint = NMIEndpoint("192.168.10.31",9024)

    # Initialize the device with the specified endpoint    
    Device = NMIDevice(Endpoint)

    # Initialize and configure the Status module
    Status = Device.STATUS()

    # Retrieve Status settings 
    print(Status.Get_Commands())  # Available commands for Status
    print(Status.Get_DashboardStatus())  # Retrieve dashboard status (detailed status info)
    print(Status.Get_Status())  # Current device connection status
   
   