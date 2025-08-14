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

    # Initialize and configure the XYOffset module
    offset = Device.XYOFFSET()

    # Retrieve XYOffset settings (offset in nm, limits in nm, etc.)
    print(offset.Get_Commands())  # List all available commands in the module
    print(offset.Get_IsOffsetUpdateAvailable())  # Check if offset updates are available
    print(offset.Get_XOffset())  # Get current X offset
    print(offset.Get_YOffset())  # Get current Y offset 
    print(offset.Get_XYOffset())  # Get both X and Y offsets 

    # Retrieve offset limits
    print(offset.Get_XOffsetLimit())  # Get X offset positive and negative limits
    print(offset.Get_YOffsetLimit())  # Get Y offset positive and negative limits 
    print(offset.Get_XYOffsetLimit())  # Get both X and Y offset limits 

    # Update offset settings
    print(offset.Set_XOffset(120.5))  # Update X offset to 120.5 nm
    print(offset.Get_XOffset())  # Verify updated X offset

    print(offset.Set_YOffset(150.5))  # Update Y offset to 150.5 nm
    print(offset.Get_YOffset())  # Verify updated Y offset
    
    print(offset.Set_XYOffset(120.5, 150.5))  # Update both X and Y offsets
    print(offset.Get_XYOffset())  # Verify updated X and Y offsets