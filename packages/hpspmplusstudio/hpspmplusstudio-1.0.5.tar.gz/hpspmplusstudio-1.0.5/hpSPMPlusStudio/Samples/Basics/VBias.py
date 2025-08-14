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

    # Initialize and configure the VBias module
    VBias = Device.VBIAS()

    # Retrieve VBias settings (e.g., DC offset in V, AC amplitude in Vpp, AC frequency in Hz, etc.)
    print(VBias.Get_Commands())  # List available commands
    print(VBias.Get_DCOffset())  # Current DC offset 
    print(VBias.Get_ACAmplitude())  # Current AC amplitude 
    print(VBias.Get_ACFrequency())  # Current AC frequency 
    print(VBias.Get_MinDCOffset())  # Minimum allowed DC offset 
    print(VBias.Get_MaxDCOffset())  # Maximum allowed DC offset 

    # Update VBias parameters
    print(VBias.Set_DCOffset(5))  # Set DC offset to 5 V
    print(VBias.Set_ACAmplitude(5))  # Set AC amplitude to 5 Vpp
    print(VBias.Set_ACFrequency(30000))  # Set AC frequency to 30 kHz

    # Verify updated VBias parameters
    print(VBias.Get_DCOffset())  # Updated DC offset
    print(VBias.Get_ACAmplitude())  # Updated AC amplitude 
    print(VBias.Get_ACFrequency())  # Updated AC frequency
    
    
    


 
    

