from hpSPMPlusStudio import NMICommand,NMIEndpoint,NMIDevice
import time

if __name__ == "__main__":
    # Define the endpoint by specifying the device's IP address and port
    # Ensure the IP and port match the device configuration
    Endpoint = NMIEndpoint("192.168.10.31",9024)

    # Initialize the device with the specified endpoint    
    Device = NMIDevice(Endpoint)

    # Initialize and configure the System Readings module
    sysRead= Device.SYSTEMREADINGS()

    # Retrieve SystemReadings settings
    print(sysRead.Get_Commands())   # List available commands
    print(sysRead.Get_SystemReadings())  # Get current system readings 
    print(sysRead.Get_SystemReadingsUnitText())  # Get the unit text for the system readings