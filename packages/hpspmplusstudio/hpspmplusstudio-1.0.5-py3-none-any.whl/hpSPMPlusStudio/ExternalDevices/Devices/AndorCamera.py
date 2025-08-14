from .utils import ExternalScanDevice
from pylablib.devices import Andor
import numpy as np
from enum import Enum


class ReadMode(Enum):
    FVB = "fvb"
    IMAGE = "image"

class TriggerMode(Enum):
    INTERNAL = "int"
    EXTERNAL = "ext"

class AcquisitionMode(Enum):
    SINGLE = "single"
    ACCUM = "accum"

class AndorCamera(ExternalScanDevice):
    def __init__(self):
        self.camera = None

    def connect(self):
        """Connect to the Andor camera."""
        camera_count = Andor.get_cameras_number_SDK2()
        if camera_count == 0:
            raise Exception("No cameras found.")
        self.camera = Andor.AndorSDK2Camera()
        print("Camera connected.")

    def disconnect(self):
        """Disconnect the camera."""
        if self.camera and self.camera.is_opened():
            self.camera.close()
            print("Camera disconnected.")

    def set_temperature(self, temperature):
        """Set the camera temperature."""
        if self.camera:
            self.camera.set_temperature(temperature)
            self.camera.set_cooler()
            print(f"Temperature set to {temperature}C.")

    def get_status(self):
        """Get the current status of the camera."""
        if self.camera:
            return self.camera.get_full_status()
        return None

    def get_info(self):
        """Get full camera information."""
        if self.camera:
            return self.camera.get_full_info()
        return None

    def set_exposure(self, exposure_time):
        """Set the exposure time."""
        if self.camera:
            self.camera.set_exposure(exposure_time)
            print(f"Exposure time set to {exposure_time} seconds.")

    def configure_acquisition(self, mode=AcquisitionMode.SINGLE, read_mode=ReadMode.FVB, trigger_mode=TriggerMode.INTERNAL, amp_settings=None):
        """Configure acquisition settings."""
        if self.camera:
            self.camera.set_read_mode(read_mode.value)
            self.camera.set_trigger_mode(trigger_mode.value)
            self.camera.setup_shutter("auto")

            if amp_settings:
                self.camera.set_amp_mode(
                    channel=amp_settings.get("channel", 0),
                    oamp=amp_settings.get("oamp", 1),
                    hsspeed=amp_settings.get("hsspeed", 2),
                    preamp=amp_settings.get("preamp", 2),
                )
            
            self.camera.setup_acquisition(mode.value)
            print(f"Acquisition configured. Mode: {mode.name}, Read Mode: {read_mode.name}, Trigger Mode: {trigger_mode.name}.")

    def acquire_spectrum(self):
        """Acquire a Raman spectrum."""
        if self.camera:
            spectrum = self.camera.snap()        
            return spectrum[0]  # Return the spectral data
        return None

    def start_acquisition(self):
        """Start acquisition."""
        if self.camera:
            self.camera.start_acquisition()
            print("Acquisition started.")

    def stop_acquisition(self):
        """Stop acquisition."""
        if self.camera:
            self.camera.stop_acquisition()
            print("Acquisition stopped.")

    def clear_acquisition(self):
        """Clear acquisition settings."""
        if self.camera:
            self.camera.clear_acquisition()
            print("Acquisition cleared.")

    
    def GetScanData(self) -> float:
        return None

   