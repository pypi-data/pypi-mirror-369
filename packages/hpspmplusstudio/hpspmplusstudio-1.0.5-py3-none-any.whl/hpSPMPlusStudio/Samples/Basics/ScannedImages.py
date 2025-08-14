from hpSPMPlusStudio import NMICommand,NMIEndpoint,NMIDevice
import time, requests

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

    # Initialize and configure the ScannedImages module
    ScannedImages = Device.SCANNEDIMAGES()

    # Retrieve available commands and settings
    print(ScannedImages.Get_Commands())  # List available commands
    print(ScannedImages.Get_NmiContainers())  # Get the list of available NMI containers
    print(ScannedImages.Get_SelectedContainerImageList("hpSPM_Plus_Image_closed loop_gratıng-acla_scan angle 0_Dynamic_2024.04.15_15.34.46.629"))  # Get the list of images in the currently selected container
    print(ScannedImages.Get_SelectedContainerImage("hpSPM_Plus_Image_closed loop_gratıng-acla_scan angle 0_Dynamic_2024.04.15_15.34.46.629", "Amplitude_Fwd (256x253)"))  # Get the currently selected image from the selected container
    print(ScannedImages.Get_SelectedContainerBackwardImageList("hpSPM_Plus_Image_closed loop_gratıng-acla_scan angle 0_Dynamic_2024.04.15_15.34.46.629"))  # Get the list of backward images in the specified container
    print(ScannedImages.Get_SelectedContainerForwardImageList("hpSPM_Plus_Image_closed loop_gratıng-acla_scan angle 0_Dynamic_2024.04.15_15.34.46.629"))  # Get the list of forward images in the specified container

