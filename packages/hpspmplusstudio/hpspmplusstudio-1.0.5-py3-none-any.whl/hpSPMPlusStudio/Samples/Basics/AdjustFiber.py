import hpSPMPlusStudio as hps
from hpSPMPlusStudio import NMICommand,NMIEndpoint,NMIDevice
import time

# Display general documentation, including available commands and their descriptions
hps.help()


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

    # Initialize and configure the AdjustFiber module
    AdjustFiber = Device.ADJUSTFIBER()

    # Check the initialization status of AdjustFiber
    print(AdjustFiber.Get_IsInit())  # Check if initialized
    try:
        AdjustFiber.Set_Initialize()
    except Exception as e:
        print("Initialization failed:", e)
        exit(1)
    print(AdjustFiber.Get_IsInit())  # Recheck initialization status

    # Retrieve available commands and settings
    print(AdjustFiber.Get_Commands())  # List available commands
    print(AdjustFiber.Get_NumSamples())  # Number of samples used
    print(AdjustFiber.Get_NumAvg())  # Number of averages applied
    print(AdjustFiber.Get_Delay())  # Delay setting
    print(AdjustFiber.Get_MiddleDelay())  # Middle delay
    print(AdjustFiber.Get_KFiber())  # K Fiber value
    print(AdjustFiber.Get_SlopeStepSize())  # Slope step size
    print(AdjustFiber.Get_SinPeriod())  # Sine period
    print(AdjustFiber.Get_SlopeModeList())  # List of slope modes
    print(AdjustFiber.Get_SlopeMode())  # Active slope mode
    print(AdjustFiber.Get_Gamma())  # Gamma value
    print(AdjustFiber.Get_MaxPztVoltage())  # Maximum PZT voltage
    print(AdjustFiber.Get_IsAutoKFiberEnable())  # Auto K Fiber status

    # Retrieve current results
    print(AdjustFiber.Get_Results())  # All results
    print(AdjustFiber.Get_ResultMaxSlope())  # Maximum slope
    print(AdjustFiber.Get_ResultMinSlope())  # Minimum slope
    print(AdjustFiber.Get_ResultQuadraturePointPower())  # Power at quadrature point
    print(AdjustFiber.Get_ResultFiberVoltage())  # Fiber voltage
    print(AdjustFiber.Get_ResultFiberPosition())  # Fiber position
    print(AdjustFiber.Get_ResultLaserPower())  # Laser power
    print(AdjustFiber.Get_ResultFinesse())  # Finesse value
    print(AdjustFiber.Get_ResultVisibility())  # Signal visibility

    # Set AdjustFiber parameters
    print(AdjustFiber.Set_NumSamples(256))  # Update sample count
    print(AdjustFiber.Set_NumAvg(6))  # Update average count
    print(AdjustFiber.Set_SlopeStepSize(6))  # Update slope step
    print(AdjustFiber.Set_SlopeMode("MaxSlope"))  # Change slope mode
    print(AdjustFiber.Set_Gamma(0.85))  # Update gamma
    print(AdjustFiber.Set_AutoKFiberEnable())  # Enable auto K Fiber

    # Find the quadrature point
    print(AdjustFiber.FindQuadrature())
    time.sleep(5)  # Wait for the operation to start
    
    while True:
        isTunning = AdjustFiber.Get_IsRunning()["IsRunning"]
        if not isTunning:
            print("Tuning completed.")
            break
        time.sleep(0.5)
        print(isTunning)
    
    # Disable Auto K Fiber after tuning
    print(AdjustFiber.Set_AutoKFiberDisable())  

    # Retrieve current results and parameters
    print(AdjustFiber.Get_Results()) 
    print(AdjustFiber.Get_ResultMaxSlope())  
    print(AdjustFiber.Get_ResultMinSlope())  
    print(AdjustFiber.Get_ResultQuadraturePointPower()) 
    print(AdjustFiber.Get_ResultFiberVoltage())  
    print(AdjustFiber.Get_ResultFiberPosition())  
    print(AdjustFiber.Get_ResultLaserPower())  
    print(AdjustFiber.Get_ResultFinesse())  
    print(AdjustFiber.Get_ResultVisibility())  

    print(AdjustFiber.Get_ForwardDataList())  # Retrieve forward data list for analysis
    print(AdjustFiber.Get_ForwardSlopeDataList())  # Retrieve forward slope data list for analysis
    
    print(AdjustFiber.Get_BackwardDataList())  # Retrieve backward data list for analysis
    print(AdjustFiber.Get_BackwardSlopeDataList())  # Retrieve backward slope data list for analysis

    # Stop the AdjustFiber process
    print(AdjustFiber.Stop())

  

    