from hpSPMPlusStudio import NMIEndpoint,NMIDevice
import requests

if __name__ == "__main__":
    # Define the endpoint by specifying the device's IP address and port
    # Ensure the IP and port match the device configuration
    Endpoint = NMIEndpoint("192.168.10.31",9024)

    # Initialize the device with the specified endpoint  
    Device = NMIDevice(Endpoint)

    # Example calls to device functionalities
    Scan = Device.SCAN()
    Options = Device.OPTIONS()
    XYOffsetController = Device.XYOFFSET()
    Status = Device.STATUS()

    # Initialize and configure the Options module
    Options = Device.OPTIONS()
    
    # Retrieve Options settings (e.g., SPM type, AFM mode, scale settings, etc.)
    print(Options.Get_Commands())  # List available commands
    print(Options.Get_SPMTypeList())  # The list of available SPM types
    print(Options.Get_AFMModeList())  # The list of available AFM modes
    print(Options.Get_SPMType())  # The current SPM type
    print(Options.Get_AFMMode())  # The current AFM mode
    print(Options.Get_ScaleList())  # The list of available scales
    print(Options.Get_XYScale())  # The current XY scale
    print(Options.Get_ZScale())  # The current Z scale

    # Set Options parameters
    print(Options.Set_SPMType("LT_SHPM"))  # Update SPM type to "LT_SHPM"
    print(Options.Set_AFMMode("LFM"))  # Update AFM mode to "LFM"
    print(Options.Set_XYScale("nm"))  # Update XY scale to nanometers (nm)
    print(Options.Set_ZScale("nm"))  # Update Z scale to nanometers (nm)

    # Recheck Options settings after updates (e.g., SPM type, AFM mode, scale settings, etc.)
    print(Options.Get_SPMType())  # SPM type
    print(Options.Get_AFMMode())  # AFM mode
    print(Options.Get_XYScale())  # XY scale
    print(Options.Get_ZScale())  # Z scale

 