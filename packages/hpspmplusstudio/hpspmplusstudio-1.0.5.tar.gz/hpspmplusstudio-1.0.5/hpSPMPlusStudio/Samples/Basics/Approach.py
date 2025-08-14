from hpSPMPlusStudio import NMICommand,NMIEndpoint,NMIDevice
import time

if __name__ == "__main__":
    # Define the endpoint by specifying the device's IP address and port
    # Ensure the IP and port match the device configuration
    Endpoint = NMIEndpoint("192.168.10.110",9024)
    # Initialize the device with the specified endpoint    
    Device = NMIDevice(Endpoint)
    # Initialize and configure the AutoTune module
    Approach = Device.APPROACH()

    # Check and initialize AutoTune
    print(Approach.Get_IsInit())  # Check if initialized
    try:
        Approach.Set_Initialize()  # Initialize AutoTune
    except Exception as e:
        print("Initialization failed:", e)
        exit(1)
    time.sleep(1)  # Wait for initialization to complete
    print(Approach.Get_IsInit())  # Verify initialization

    # Retrieve available commands and settings
    print(Approach.Get_Commands())  # List available commands
    
    print(Approach.Get_AdjustableDistanceType())  # Get current adjustable distance type
    print(Approach.Get_SpeedType())

    print(Approach.Set_AxisType_Sample())
    
    time.sleep(1)  # Wait for settings to be applied    
    print(Approach.Set_AdjustableDistanceType("Fine"))  # Set adjustable distance type to "Short"
    time.sleep(0.2)  # Wait for setting to be applied
    print(Approach.Get_AdjustableDistanceType())  # Get current adjustable distance type
    print(Approach.Set_SpeedType("Fast"))  # Set speed type to "Fast"
    time.sleep(0.2) 
    print(Approach.Get_SpeedType())  # Get current speed type

    print(Approach.Set_AdjustableDistanceType("Coarse"))  # Set adjustable distance type to "Short"
    time.sleep(0.2)  # Wait for setting to be applied
    print(Approach.Get_AdjustableDistanceType())  # Get current adjustable distance type

    time.sleep(1)  # Wait for settings to be applied
    print(Approach.Set_AxisType_Objective())  # Set axis type to "Objective"
    time.sleep(0.2)

    print(Approach.Set_AxisType_Sample())
    time.sleep(0.2)  # Wait for setting to be applied
    print(Approach.Set_MoveUp())  # Move up
    time.sleep(1)  # Wait for movement to complete
    print(Approach.Set_MoveDown())  # Move down
    time.sleep(1)
    print(Approach.Set_MoveLeft())  # Move left
    time.sleep(1)  # Wait for movement to complete
    print(Approach.Set_MoveRight())  # Move right
    time.sleep(1)
    print(Approach.Set_MoveForward())
    time.sleep(1)  # Wait for movement to complete
    print(Approach.Set_MoveBackward())
    time.sleep(1)  # Wait for movement to complete
    print(Approach.Set_Stop())
    time.sleep(1)  # Wait for stop command to complete

    print(Approach.Get_StepCountX())  # Get step count in X direction
    print(Approach.Get_StepCountY())  # Get step count in Y direction
    print(Approach.Get_StepCountZ())