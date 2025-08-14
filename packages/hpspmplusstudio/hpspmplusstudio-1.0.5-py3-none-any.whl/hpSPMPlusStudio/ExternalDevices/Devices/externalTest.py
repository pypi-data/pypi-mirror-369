from .utils import ExternalScanDevice
from enum import Enum

class ExternalTest(ExternalScanDevice):
    def __init__(self):
        self.index = 0
        pass

    def GetScanData(self) -> list:
        _dataList = []
        for i in range(128):
            _dataList.append(i+self.index)
        self.index += 1
        return _dataList