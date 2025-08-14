from hpSPMPlusStudio import NMICommand,NMIEndpoint,NMIDevice
import time

if __name__ == "__main__":
    # Define the endpoint by specifying the device's IP address and port
    # Ensure the IP and port match the device configuration
    Endpoint = NMIEndpoint("192.168.10.31",9024)

    # Initialize the device with the specified endpoint 
    Device = NMIDevice(Endpoint)

    # Perform basic device operations
    Options = Device.OPTIONS()
    XYOffsetController = Device.XYOFFSET()
    Status = Device.STATUS()

    # Initialize and configure the HallCard module
    Scan = Device.SCAN()

    # Retrieve current scale settings
    print(Options.Get_XYScale())  # Get XY scale in μm
    print(Options.Get_ZScale())  # Get Z scale in nm

    # Set initial XY offset position for scan
    XYOffsetController.Set_XYOffset(0,0)  # Update XY offset to (0, 0)

    # Set scan parameters
    print(Scan.Set_XOffset(0))  # Update X offset to 0
    print(Scan.Set_YOffset(0))  # Update Y offset to 0
    print(Scan.Set_ScanHeightPixel(64))  # Update scan height to 64 pixels
    print(Scan.Set_ScanWidthPixel(64))  # Update scan width to 64 pixels
    print(Scan.Set_ImageWidth(3))  # Update image width to 3 μm
    print(Scan.Set_ImageHeight(3))  # Update image height to 3 μm
    print(Scan.Set_ScanAngle(0))  # Update scan angle to 0 degrees
    print(Scan.Set_ScanNumberOfAverages(4))  # Update averages to 4
    print(Scan.Set_NumberOfScans(1))  # Update total scans to 1
    print(Scan.Set_ScanSpeed(5))  # Update scan speed to 5
    print(Scan.Set_IsSaveScannedImages(True))  # Enable image saving
    print(Scan.Set_OffsetPosition("BottomLeft"))  # Update position to bottom-left
    print(Scan.Set_ScanDirection("BottomToTop"))  # Update scan direction to bottom-to-top
    print(Scan.Set_IsImageSquare(True))  # Update as enables or disables the square shape
    print(Scan.Set_IsRoundtripScan(True))  # Update as enable or disable the roundtrip scan

    # Retrieve and print scan-related information (current offset in μm, dimensions in pixels, etc.)
    print(Scan.Get_Commands())  # List available scan commands
    print(Scan.Get_IsScanning())  # Is scan currently in progress?
    print(Scan.Get_ScanError())  # Current scan error status
    print(Scan.Get_ScanLineIndex())  # Current scan line index
    print(Scan.Get_ScanIndex())  # Current scan index
    print(Scan.Get_XOffset())  # X offset
    print(Scan.Get_YOffset())  # Y offset
    print(Scan.Get_ScanWidthPixel())  # Scan width in pixels
    print(Scan.Get_ScanHeightPixel())  # Scan height in pixels
    print(Scan.Get_ImageWidth())  # Real image width
    print(Scan.Get_ImageHeight())  # Real image height
    print(Scan.Get_ScanAngle())  # Scan angle
    print(Scan.Get_ScanSpeed())  # Scan speed
    print(Scan.Get_ScanNumberOfAverages())  # Number of averages
    print(Scan.Get_NumberOfScans())  # Total number of scans
    print(Scan.Get_OffsetPosition())  # Offset position
    print(Scan.Get_ScanDirection())  # Scan direction
    print(Scan.Get_IsRoundtripScan())  # Is roundtrip scan enabled?
    print(Scan.Get_IsSaveScannedImages())  # Is saving scanned images enabled?
    print(Scan.Get_IsImageSquare())  # Is the scanned image square?
    
    print(Scan.Get_CapturePixel())  # Get the capture pixel value for the scan
    print(Scan.Get_CapturePixelUnitText())  # Get the unit text for the capture pixel (e.g., "pixels")
    
    # Check scanning status and errors
    isScanning = (bool)(Scan.Get_IsScanning()["IsScanning"])  # Is scanning in progress?
    hasError = Scan.Get_ScanError()["ScanError"]  # Retrieve scan error status
    status = Status.Get_Status()  # Retrieve current device status
    time.sleep(2)

    # Start scanning process if ready
    if(isScanning==False and status == "Ready"):
        Scan.StartScan(True)  # Start scan process
        time.sleep(2)
        while(True):
            isScanning = (bool)(Scan.Get_IsScanning()["IsScanning"])
            if(isScanning==False):
                break   # Exit loop if scanning is complete
            print(Scan.Get_ScanLineIndex())  # Current scan line index
            print(Scan.Get_ScanIndex())  # Current scan index
            time.sleep(0.5)
    
    # Stop scanning
    Scan.StopScan(True)
    
    # Check for any errors after scanning
    hasError = Scan.Get_ScanError()["ScanError"]
    print(hasError)


 