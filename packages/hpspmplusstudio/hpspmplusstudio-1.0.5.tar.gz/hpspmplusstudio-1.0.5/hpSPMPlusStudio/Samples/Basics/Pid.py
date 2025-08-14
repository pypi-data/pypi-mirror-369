from hpSPMPlusStudio import NMICommand,NMIEndpoint,NMIDevice
import time

if __name__ == "__main__":
    # Define the endpoint by specifying the device's IP address and port
    # Ensure the IP and port match the device configuration
    Endpoint = NMIEndpoint("192.168.10.31",9024)
    
    # Initialize the device with the specified endpoint 
    Device = NMIDevice(Endpoint)

    # Perform basic device operations
    Scan = Device.SCAN()
    Options = Device.OPTIONS()
    XYOffsetController = Device.XYOFFSET()
    Status = Device.STATUS()

    # Initialize and configure the Pid module
    Pid  = Device.PID()

    # Retrieve PID types and configurations
    print(Pid.Get_Commands())  # List available commands
    print(Pid.Get_PidTypes()) # List available PID types
    print(Pid.Get_PID(0))  # PID settings for index 0
    print(Pid.Get_PID(1))  # PID settings for index 1
    print(Pid.Get_PID(2))  # PID settings for index 2
    print(Pid.Get_PID(3))  # PID settings for index 3

    # Set PID parameters for index 0
    print(Pid.Set_Pid_PValue(0, 10))  # Update P value to 10 
    print(Pid.Set_Pid_IValue(0, 20))  # Update I value to 20 
    print(Pid.Set_Pid_DValue(0, 30))  # Update D value to 30 
    print(Pid.Set_Pid_SetValue(0, 40))  # Update set value to 40

    # Enable specific PID features for index 0
    print(Pid.Set_Pid_Enable(0))  # Enable PID control 
    print(Pid.Set_Pid_NegativePolarity_Enable(0))  # Enable negative polarity 
    print(Pid.Set_Pid_InvertVz_Enable(0))  # Enable inverted Vz 

    # Pause to observe changes
    time.sleep(4)

    # Disable specific PID features for index 0
    print(Pid.Set_Pid_Disable(0))  # Disable PID control 
    print(Pid.Set_Pid_NegativePolarity_Disable(0))  # Disable negative polarity
    print(Pid.Set_Pid_InvertVz_Disable(0))  # Disable inverted Vz 

    print(Pid.Get_PID(0))  # Verify final PID settings for index 0