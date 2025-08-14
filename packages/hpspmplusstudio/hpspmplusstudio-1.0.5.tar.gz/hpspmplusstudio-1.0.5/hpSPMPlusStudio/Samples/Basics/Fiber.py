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

    # Initialize and configure the Fiber module
    Fiber = Device.FIBERCARD()

    # Retrieve current Fiber settings and status
    print(Fiber.Get_Commands())  # List available commands
    print(Fiber.Get_IsLaserOn())  # Check if laser is enabled
    print(Fiber.Get_IsLaserFanOn())  # Check if laser fan is enabled
    print(Fiber.Get_LaserPowerSetPoint())  # Get laser power set point
    print(Fiber.Get_LaserPower())  # Get current laser power
    print(Fiber.Get_IsRFModulatorOn())  # Check if RF modulator is enabled
    print(Fiber.Get_RFModulatorAmplitudeDigiPOT())  # Get RF modulator amplitude
    print(Fiber.Get_RFModulatorFrequencyDigiPOT())  # Get RF modulator frequency
    print(Fiber.Get_SignalPhotoDiodeGain())  # Get signal photodiode gain
    print(Fiber.Get_ReferancePhotoDiodeGain())  # Get reference photodiode gain
    print(Fiber.Get_FiberPZTVoltage())  # Get fiber PZT voltage
    print(Fiber.Get_QuadlockStatus())  # Get quadlock status
    print(Fiber.Get_IsEnableQuadlock())  # Check if quadlock is enabled
    print(Fiber.Get_IsRescanQuadlockEnable())  # Check if rescan quadlock is enabled

    # Set Fiber parameters
    print(Fiber.Set_LaserEnable())  # Update laser status to enabled
    time.sleep(2)
    print(Fiber.Set_LaserDisable())  # Update laser status to disabled
    time.sleep(2)
    print(Fiber.Set_LaserEnable())  # Update laser status to re-enabled
    time.sleep(2)
    print(Fiber.Set_LaserFanEnable())  # Update laser fan status to enabled
    time.sleep(2)
    print(Fiber.Set_LaserFanDisable())  # Update laser fan status to disabled
    time.sleep(2)
    print(Fiber.Set_LaserFanEnable())  # Update laser fan status to re-enabled
    print(Fiber.Set_LaserPowerSetPoint(41.0))  # Update laser power set point to 41.0
    print(Fiber.Set_SignalPhotoDiodeGain(1))  # Update signal photodiode gain to 1
    print(Fiber.Set_ReferancePhotoDiodeGain(10))  # Update reference photodiode gain to 10
    print(Fiber.Set_FiberPZTVoltage(30))  # Update fiber PZT voltage to 30
    print(Fiber.Set_QuadlockEnable())  # Update quadlock status to enabled
    print(Fiber.Set_RescanQuadlockEnable())  # Update rescan quadlock status to enabled

    print(Fiber.Get_IsEnableQuadlock())  # Checks if quadlock is enabled
    print(Fiber.Get_IsRescanQuadlockEnable())  # Checks if rescan quadlock is enabled
     
    print(Fiber.Set_QuadlockDisable())  # Disables quadlock
    time.sleep(2)
    print(Fiber.Get_IsEnableQuadlock())  # Checks if quadlock is enabled

    print(Fiber.Set_RescanQuadlockDisable())  # Disables rescan quadlock
    time.sleep(2)
    print(Fiber.Get_IsRescanQuadlockEnable())  # Checks if rescan quadlock is enabled

    # Null the Fiber settings to reset to default state
    print(Fiber.NullFiber())



  


 
    

