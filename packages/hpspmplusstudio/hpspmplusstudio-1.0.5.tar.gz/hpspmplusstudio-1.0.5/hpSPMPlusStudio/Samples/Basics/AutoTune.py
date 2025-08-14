from hpSPMPlusStudio import NMICommand,NMIEndpoint,NMIDevice
import time

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

    # Initialize and configure the AutoTune module
    AutoTune = Device.AUTOTUNE()

    # Check and initialize AutoTune
    print(AutoTune.Get_IsInit())  # Check if initialized
    try:
        AutoTune.Set_Initialize()  # Initialize AutoTune
    except Exception as e:
        print("Initialization failed:", e)
        exit(1)
    print(AutoTune.Get_IsInit())  # Verify initialization

    # Retrieve available commands and settings
    print(AutoTune.Get_Commands())  # List available commands
    print(AutoTune.Get_Excitation())  # Get current excitation value
    print(AutoTune.Get_ExcitationPercent())  # Get excitation percentage
    print(AutoTune.Get_FrequencyStartInHertz())  # Get start frequency in Hz
    print(AutoTune.Get_FrequencyEndInHertz())  # Get end frequency in Hz
    print(AutoTune.Get_FrequencyIncrementInHertz())  # Get frequency increment
    print(AutoTune.Get_FrequencySlopeTypes())  # Get available slope types
    print(AutoTune.Get_FrequencySlopeType())  # Get current slope type
    print(AutoTune.Get_IsCenterSpan())  # Check if center span is enabled
    print(AutoTune.Get_StartDelay())  # Get start delay value
    print(AutoTune.Get_Delay())  # Get delay between operations
    print(AutoTune.Get_FineRmsSeries())  # Get fine-resolution RMS data
    print(AutoTune.Get_FinePhaseSeries())  # Get fine-resolution phase data

    # Set AutoTune parameters
    print(AutoTune.Set_ExcitationPercent(30))  # Update excitation percentage to 30%
    print(AutoTune.Set_FrequencyStartInHertz(100000))  # Update start frequency to 100 kHz
    print(AutoTune.Set_FrequencyEndInHertz(300000))  # Update end frequency to 300 kHz
    print(AutoTune.Set_FrequencyIncrementInHertz(1000))  # Update frequency increment to 1 kHz
    print(AutoTune.Set_Delay(1))  # Update delay to 1 second
    print(AutoTune.Set_StartDelay(300))  # Update start delay to 300 ms
    print(AutoTune.Set_FrequencySlope("MinSlope"))  # Update frequency slope to "MinSlope"
    print(AutoTune.Set_CenterSpanType())  # Update tuning using a center frequency and span
    print(AutoTune.Set_StartEndType())  # Update tuning using start and end frequencies
    print(AutoTune.Set_Excitation(1))  # Update current excitation value
    
    # Start the tuning process
    print(AutoTune.StartTune())
    time.sleep(5)  # Wait for the operation to start

    while True:
        isTunning = AutoTune.Get_IsTunning()["IsTunning"]  # Check tuning status
        if not isTunning:
            print("Tuning completed.")
            break
        time.sleep(0.5)
        print(isTunning)
    
    # Retrieve tuning results
    print(AutoTune.Get_MaxRms())  # Get maximum RMS value
    print(AutoTune.Get_MaxRmsFrequency())  # Get frequency of max RMS
    print(AutoTune.Get_MinSlopeFrequency())  # Get frequency of minimum slope
    print(AutoTune.Get_MinSlopeRms())  # Get RMS value at minimum slope
    print(AutoTune.Get_MaxSlopeFrequency())  # Get frequency of maximum slope
    print(AutoTune.Get_MaxSlopeRms())  # Get RMS value at maximum slope
    print(AutoTune.Get_Excitation())  # Get current excitation value

    # Retrieve detailed series data
    print(AutoTune.Get_CoarseRmsSeries())  # Get coarse RMS series data
    print(AutoTune.Get_CoarsePhaseSeries())  # Get coarse phase series data
    
    # Stops the tuning process
    print(AutoTune.StopTune())

 
