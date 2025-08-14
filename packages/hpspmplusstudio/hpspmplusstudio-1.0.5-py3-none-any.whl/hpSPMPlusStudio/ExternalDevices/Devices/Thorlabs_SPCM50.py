from .utils import ExternalScanDevice
import pyvisa
import time
import logging
from enum import Enum

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# -----------------------------------------------------
# Enum Definitions
# -----------------------------------------------------
class SPCM50_OPERATINGMODES(Enum):
    Null = -1
    Idle = 0
    Manual = 1
    FreeRunning = 2
    ExternallyTriggeredTimed = 3
    ExternallyTriggeredCount = 4
    ExternalGating = 5

class SPCM50_GATINGMODE(Enum):
    OFF = 0
    ON = 1

class PhotonCounterDevices(Enum):
    SPCM50A = 0

# -----------------------------------------------------
# SPCM50ControlModel Class
# -----------------------------------------------------
class SPCM50ControlModel(ExternalScanDevice):
    """
    Example Python class for communicating with a photon counter such as the Thorlabs SPCM50 via VISA.
    """

    # ---------------------------
    # Default Values
    # ---------------------------
    DEFAULT_BIN_LENGTH = 20.0          # in ms
    DEFAULT_TIME_BETWEEN_DELAY = 0.0   # in ms
    DEFAULT_PULSE_BLIND_TIME = 8.0     # in ms
    DEFAULT_AVERAGE_COUNT = 10
    RESOURCE_ADDRESS_KEYWORD = "0x1313"

    def __init__(self):
        # Example to store properties similar to C# properties
        self.is_initialized = False
        self.is_measurement_running = False

        self.bin_length = self.DEFAULT_BIN_LENGTH
        self.time_between_delay = self.DEFAULT_TIME_BETWEEN_DELAY
        self.pulse_blind_time = self.DEFAULT_PULSE_BLIND_TIME
        self.average_count = self.DEFAULT_AVERAGE_COUNT

        self.last_average_photon_count = 0

        self.session = None
        self.resource_manager = None
        self.visa_resource_address = None
        self.device_name = "-"
        self.curr_device = PhotonCounterDevices.SPCM50A  # Example

        # Variables to simulate UI indicators (similar to C# style)
        self.is_busy_indicator = False
        self.busy_content = "Connecting..."

        # Example simplified implementation for connection control flag
        self._connection_control_flag = False

    # ---------------------------
    # Public Methods
    # ---------------------------
    def load_settings(self):
        """
        Load settings (e.g., self.bin_length, self.time_between_delay) from an external configuration file.
        This could be a JSON or .ini file. Currently using default values.
        """
        self.is_busy_indicator = False
        self.busy_content = "Connecting..."
        logger.info("Settings loaded (using default values).")

    def set_to_default(self):
        """
        Resets the device settings to default values.
        """
        self.is_busy_indicator = False
        self.busy_content = "Connecting..."

        self.bin_length = self.DEFAULT_BIN_LENGTH
        self.time_between_delay = self.DEFAULT_TIME_BETWEEN_DELAY
        self.pulse_blind_time = self.DEFAULT_PULSE_BLIND_TIME
        self.average_count = self.DEFAULT_AVERAGE_COUNT

        logger.info("Settings reset to default values.")

    def initialize(self):
        """
        Finds the device, establishes a VISA connection, and performs basic initial settings.
        """
        try:
            self.is_busy_indicator = True
            self.busy_content = "Connecting..."

            # 1) Create a Resource Manager
            self.resource_manager = pyvisa.ResourceManager()

            # 2) Find appropriate VISA resource
            self.visa_resource_address = self.find_visa_resource_address()
            time.sleep(1)

            # 3) Exit if not found
            if self.visa_resource_address is None:
                logger.error("Device not found.")
                self.is_busy_indicator = False
                self.busy_content = "Connecting..."
                return False

            # 4) Open session
            self.session = self.resource_manager.open_resource(self.visa_resource_address)

            # 5) Connection established, perform basic settings
            self.is_initialized = True

            # 6) Get device name
            self.set_device_name()

            # 7) Reset the device (if it supports a reset command)
            self.reset_device()

            self.is_busy_indicator = False
            self.busy_content = "Connecting..."

            # 8) (Optional) Start monitoring the connection
            self._connection_control_flag = True

            logger.info(f"Device initialized: {self.device_name}")
            return True

        except pyvisa.VisaIOError as ex:
            logger.error(f"VISA connection error: {ex}")
            self.device_name = "-"
            self.is_busy_indicator = False
            self.busy_content = "Connecting..."
            return False

    def reinitialize(self):
        """
        Closes the session and reinitializes the device.
        """
        self.session_dispose()
        return self.initialize()

    def measurement_init(self):
        """
        Initializes settings for measurement (e.g., sets the device to free-running mode, disables gating).
        """
        if not self.is_initialized:
            logger.error("Device is not initialized.")
            return False
        try:
            self.set_operating_mode(SPCM50_OPERATINGMODES.FreeRunning)
            self.set_bin_length(self.bin_length)
            self.set_time_between(self.time_between_delay)
            self.set_gating_mode(SPCM50_GATINGMODE.OFF)
            logger.info("Measurement initialization completed.")
            return True
        except Exception as ex:
            logger.error(f"Measurement initialization error: {ex}")
            return False

    def get_average_count(self):
        """
        Takes the specified number of measurements (average_count) and returns the average value.
        """
        if not self.is_initialized:
            logger.error("Device is not initialized.")
            return 0.0

        self.start_measurement()
        time.sleep((self.time_between_delay + self.bin_length) / 1000.0 + 0.1)

        total_counts = 0.0
        for _ in range(self.average_count):
            count_value_str = self.get_counter_value()
            parsed_value = self._parse_counter_value(count_value_str)
            total_counts += parsed_value

            time.sleep((self.time_between_delay + self.bin_length) / 1000.0 + 0.01)

        self.stop_measurement()
        average_counts = total_counts / self.average_count

        self.last_average_photon_count = average_counts
        logger.info(f"Average photon count: {average_counts}")
        return average_counts

    def start_measurement(self):
        if not self.is_initialized:
            logger.error("Device is not initialized.")
            return False
        try:
            self.send_command("MEASure:STARt")
            self.is_measurement_running = True
            logger.info("Measurement started.")
            return True
        except Exception as ex:
            logger.error(f"StartMeasurement error: {ex}")
            return False

    def stop_measurement(self):
        if not self.is_initialized:
            logger.error("Device is not initialized.")
            return False
        try:
            self.send_command("MEASure:STOP")
            self.is_measurement_running = False
            logger.info("Measurement stopped.")
            return True
        except Exception as ex:
            logger.error(f"StopMeasurement error: {ex}")
            return False

    def session_dispose(self):
        """
        Closes the session (releases VISA resources).
        """
        if self.session is not None:
            try:
                self.session.close()
            except Exception as ex:
                logger.error(f"Session close error: {ex}")
        self.session = None
        self.visa_resource_address = None
        self.is_initialized = False
        logger.info("Session closed.")

    # ---------------------------
    # Private/Helper Methods
    # ---------------------------
    def find_visa_resource_address(self):
        """
        Finds the device with '0x1313' in its resource string.
        """
        try:
            if self.resource_manager is None:
                self.resource_manager = pyvisa.ResourceManager()

            resources = self.resource_manager.list_resources()
            for rsc in resources:
                if self.RESOURCE_ADDRESS_KEYWORD in rsc:
                    return rsc
            return None
        except Exception as ex:
            logger.error(f"VISA resource search error: {ex}")
            return None

    def send_command(self, command: str):
        """
        Sends a command to the device.
        """
        if not self.is_initialized or self.session is None:
            return
        try:
            self.session.write(command)
        except Exception as ex:
            logger.error(f"Command send error: {command}, {ex}")
            self.session_dispose()

    def read_command(self) -> str:
        """
        Reads a response from the device.
        """
        if not self.is_initialized or self.session is None:
            return ""
        try:
            return self.session.read().strip()
        except Exception as ex:
            logger.error(f"Response read error: {ex}")
            self.session_dispose()
            return ""

    def set_device_name(self):
        """
        Reads the device name using *IDN? query and saves it.
        """
        self.send_command("*IDN?")
        response = self.read_command()
        parts = response.split(',')
        if len(parts) >= 2:
            self.device_name = parts[1]
        logger.info(f"Device name: {self.device_name}")

    def reset_device(self):
        """
        Sends a hardware reset command if supported (e.g., *RST).
        """
        logger.info("Device reset (example).")

    def get_counter_value(self) -> str:
        """
        Requests the measurement value (e.g., using a DATA? command).
        """
        if not self.is_initialized:
            return ""
        try:
            self.send_command("DATA?")
            return self.read_command()
        except Exception as ex:
            logger.error(f"Counter value retrieval error: {ex}")
            return ""

    # ---------------------------
    # Configuration and Status Methods
    # ---------------------------
    def set_operating_mode(self, mode: SPCM50_OPERATINGMODES) -> bool:
        if not self.is_initialized:
            return False
        try:
            self.send_command(f"GATE:MODE {mode.value}")
            return True
        except Exception as ex:
            logger.error(f"SetOperatingMode error: {ex}")
            return False

    def get_operating_mode(self) -> SPCM50_OPERATINGMODES:
        if not self.is_initialized:
            return SPCM50_OPERATINGMODES.Null
        try:
            self.send_command("GATE:MODE?")
            mode_str = self.read_command()
            mode_val = int(mode_str)
            return SPCM50_OPERATINGMODES(mode_val)
        except Exception as ex:
            logger.error(f"GetOperatingMode error: {ex}")
            return SPCM50_OPERATINGMODES.Null

    def set_gating_mode(self, mode: SPCM50_GATINGMODE) -> bool:
        if not self.is_initialized:
            return False
        try:
            self.send_command(f"APD:GATE {mode.value}")
            return True
        except Exception as ex:
            logger.error(f"SetGatingMode error: {ex}")
            return False

    def get_gating_mode(self) -> SPCM50_GATINGMODE:
        if not self.is_initialized:
            return SPCM50_GATINGMODE.OFF
        try:
            self.send_command("APD:GATE?")
            mode_str = self.read_command()
            return SPCM50_GATINGMODE(int(mode_str))
        except Exception as ex:
            logger.error(f"GetGatingMode error: {ex}")
            return SPCM50_GATINGMODE.OFF

    def set_bin_length(self, bin_length_ms: float) -> bool:
        """
        If the device command expects the bin length in seconds,
        convert ms to seconds. For example, SPCM50 may use 'GATE:APERture' in seconds.
        """
        if not self.is_initialized:
            return False
        try:
            self.bin_length = bin_length_ms
            seconds_val = bin_length_ms / 1000.0
            self.send_command(f"GATE:APERture {seconds_val}")
            return True
        except Exception as ex:
            logger.error(f"SetBinLength error: {ex}")
            return False

    def get_bin_length(self) -> float:
        if not self.is_initialized:
            return 0.0
        try:
            self.send_command("GATE:APERture?")
            val_str = self.read_command()
            return float(val_str) * 1000.0  # Convert to ms
        except Exception as ex:
            logger.error(f"GetBinLength error: {ex}")
            return 0.0

    def set_time_between(self, delay_ms: float) -> bool:
        """
        Converts ms to seconds if the device parameter is in seconds.
        """
        if not self.is_initialized:
            return False
        try:
            seconds_val = delay_ms / 1000.0
            self.time_between_delay = delay_ms
            self.send_command(f"GATE:DELay {seconds_val}")
            return True
        except Exception as ex:
            logger.error(f"SetTimeBetween error: {ex}")
            return False

    def get_time_between(self) -> float:
        if not self.is_initialized:
            return 0.0
        try:
            self.send_command("GATE:DELay?")
            val_str = self.read_command()
            return float(val_str) * 1000.0
        except Exception as ex:
            logger.error(f"GetTimeBetween error: {ex}")
            return 0.0

    # ---------------------------
    # Helper Function
    # ---------------------------
    def _parse_counter_value(self, value_str: str) -> float:
        """
        Parses a string like "1234.56;XYZ" and returns the first numeric part as a float.
        Modify according to your protocol.
        """
        if not value_str:
            return 0.0
        try:
            parts = value_str.split(';')
            return float(parts[0])
        except:
            return 0.0
        
    def GetScanData(self) -> list:
        _list = []
        data = 0
        try:    
            avg_count = self.get_average_count()      
            data = avg_count
            print("SPCM50 Data: ", data)
            _list = [data]
            return _list     
        except Exception as e:
            _list = [data]
            print(e)
            return _list