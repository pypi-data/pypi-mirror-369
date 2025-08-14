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

    # Initialize and configure the HallCard module
    HallCard = Device.HALLCARD()

    # Retrieve HallCard settings (current in μA, resistance in Ω/G, voltage in V, bandwidth in Hz, etc.)
    print(HallCard.Get_Commands())  # List available commands
    print(HallCard.Get_IsHallProbeEnabled())  # Hall probe status
    print(HallCard.Get_IsInfraRedLedOn())  # InfraRed LED status
    print(HallCard.Get_IHallRange())  # Hall current range
    print(HallCard.Get_IHall())  # Hall current
    print(HallCard.Get_IHallOffset())  # Hall current offset
    print(HallCard.Get_RHall())  # Hall resistance
    print(HallCard.Get_VHall())  # Hall voltage
    print(HallCard.Get_BHall())  # Magnetic field
    print(HallCard.Get_HallAmplitudeGain())  # Hall amplitude gain
    print(HallCard.Get_HallAmplitudeBandwith())  # Hall amplitude bandwidth
    print(HallCard.Get_CoilVoltage())  # Coil voltage
    print(HallCard.Get_CoilVoltageRate())  # Coil voltage rate

    # Set HallCard parameters
    print(HallCard.Set_IHall(2))  # Update Hall current to 2 μA
    print(HallCard.Set_IHallOffset(3))  # Update current offset to 3 μA
    print(HallCard.Set_RHall(3))  # Update resistance to 3 Ω/G
    print(HallCard.Set_EnableHallProbe())  # Enable Hall probe
    print(HallCard.Set_EnableIRLed())  # Enable InfraRed LED
    print(HallCard.Set_HallAmplitudeGain(100))  # Update amplitude gain to 100
    print(HallCard.Set_HallAmplitudeBandwidth(1))  # Update bandwidth to 1 Hz
    print(HallCard.Set_CoilVoltage(3))  # Update coil voltage to 3 V
    print(HallCard.Set_CoilVoltageRate(0.6))  # Update coil voltage rate to 0.6 V/s
    print(HallCard.Set_DisableHallProbe())  # Disable Hall probe
    print(HallCard.Set_DisableIRLed())  # Disable InfraRed LED

    # Null the HallCard settings to reset to default state
    print(HallCard.NullHallOffset())  

    # Recheck HallCard settings after updates (current in μA, resistance in Ω/G, voltage in V, bandwidth in Hz, etc.)
    print(HallCard.Get_IsHallProbeEnabled())  # Hall probe status
    print(HallCard.Get_IsInfraRedLedOn())  # InfraRed LED status
    print(HallCard.Get_IHallRange())  # Hall current range
    print(HallCard.Get_IHall())  # Hall current
    print(HallCard.Get_IHallOffset())  # Hall current offset
    print(HallCard.Get_RHall())  # Hall resistance
    print(HallCard.Get_VHall())  # Hall voltage
    print(HallCard.Get_BHall())  # Magnetic field
    print(HallCard.Get_HallAmplitudeGain())  # Hall amplitude gain
    print(HallCard.Get_HallAmplitudeBandwith())  # Hall amplitude bandwidth
    print(HallCard.Get_CoilVoltage())  # Coil voltage
    print(HallCard.Get_CoilVoltageRate())  # Coil voltage rate
    


 
    

