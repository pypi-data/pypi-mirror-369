from abc import ABC, abstractmethod
# Soyut sınıf tanımı
class ExternalScanDevice(ABC):
    @abstractmethod
    def GetScanData(self)->float:
        pass