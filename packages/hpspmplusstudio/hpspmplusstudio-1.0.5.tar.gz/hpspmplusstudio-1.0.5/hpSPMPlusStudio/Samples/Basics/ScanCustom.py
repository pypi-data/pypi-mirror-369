from hpSPMPlusStudio import NMICommand,NMIEndpoint,NMIDevice,SystemReadingsChannels

class NMIManualScan:
    def __init__(self,device:NMIDevice):
        self.Device = device
       




if __name__ == "__main__":
    Endpoint = NMIEndpoint("192.168.10.53",9024)
    Device = NMIDevice(Endpoint)