from hpSPMPlusStudio import NMIEndpoint,NMIDevice
import requests,time

if __name__ == "__main__":
    # Define the endpoint by specifying the device's IP address and port
    # Ensure the IP and port match the device configuration
    Endpoint = NMIEndpoint("192.168.10.31",9024)

    # Initialize the device with the specified endpoint  
    Device = NMIDevice(Endpoint)

    # Example calls to device functionalities
    WindowControl = Device.WINDOWCONTROLLER()
    
    # Retrieve WindowControl settings and available commands
    print(WindowControl.Get_Commands())  # List available commands
    print(WindowControl.Get_OpenedWindows())  # List currently opened windows
    print(WindowControl.Get_IsOpened("Auto Tune"))  # Check if "Auto Tune" window is opened

    # Minimize specific window
    print("SetMinimizeWindow")    
    print(WindowControl.Set_MinimizeWindow("Auto Tune"))  # Minimize the "Auto Tune" window
    time.sleep(3)

    # Maximize specific window
    print("SetMaximizeWindow")
    print(WindowControl.Set_MaximizeWindow("Auto Tune"))  # Maximize the "Auto Tune" window
    time.sleep(3)

    # Close specific window
    print("SetCloseWindow")
    print(WindowControl.Set_CloseWindow("Auto Tune"))  # Close the "Auto Tune" window
    time.sleep(3)

    # Minimize all open windows
    print("SetMinimizeAll")
    print(WindowControl.Set_MinimizeAll())  # Minimize all currently opened windows
    time.sleep(3)

    # Normalize all minimized windows
    print("SetNormalizeAll")
    print(WindowControl.Set_NormalizeAll())  # Normalize all minimized windows
