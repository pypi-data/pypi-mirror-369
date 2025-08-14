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
    Status = Device.STATUS()

    # Initialize and configure the PhotoDiode module
    PhotoDiode = Device.PHOTODIODE()

    # Retrieve current PhotoDiode settings (laser power in %, RF frequency in MHz, etc.)
    print(PhotoDiode.Get_Commands())  # List available commands
    print(PhotoDiode.Get_FL())  # Laser feedback value
    print(PhotoDiode.Get_FN())  # Normalized feedback value
    print(PhotoDiode.Get_FN10())  # 10x normalized feedback value
    print(PhotoDiode.Get_FT())  # Total feedback
    print(PhotoDiode.Get_LaserPower())  # Current laser power
    print(PhotoDiode.Get_LaserRF_Frequency())  # Current laser RF frequency
    print(PhotoDiode.Get_IsLaserEnabled())  # Check if the laser is enabled

    # Update PhotoDiode parameters
    print(PhotoDiode.Set_LaserPower(20.5))  # Update laser power to 20.5%
    print(PhotoDiode.Set_LaserRF_Frequency(21.5))  # Update RF frequency to 21.5 MHz
    print(PhotoDiode.Set_LaserEnable())  # Enable the laser
    print(PhotoDiode.Set_LaserDisable())  # Disable the laser

    # Recheck PhotoDiode settings after updates (laser power in %, RF frequency in MHz, etc.)
    print(PhotoDiode.Get_LaserPower())  # Verify updated laser power
    print(PhotoDiode.Get_LaserRF_Frequency())  # Verify updated RF frequency
    print(PhotoDiode.Get_IsLaserEnabled())  # Check if the laser is enabled (recheck)

    # Nullify or reset specific PhotoDiode parameters
    time.sleep(5)
    print(PhotoDiode.Null10FN())  # Nullify 10x normalized feedback value
    time.sleep(5)
    print(PhotoDiode.NullFL())  # Nullify laser feedback value
    time.sleep(5)
    print(PhotoDiode.PhotoDiodeReset())  # Reset all PhotoDiode parameters to default state
    

   
    


