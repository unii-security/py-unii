"""
Data classes used by the UNii library.
"""

import logging
import string
from abc import abstractmethod
from datetime import datetime
from enum import IntEnum, IntFlag, auto
from typing import Final

logger = logging.getLogger(__name__)


class UNiiData:
    # pylint: disable=too-few-public-methods
    """
    UNii Base data class
    """


class UNiiSendData:
    # pylint: disable=too-few-public-methods
    """
    Method which should be implemented by data classes which are used to send data.
    """

    @abstractmethod
    def to_bytes(self):
        """
        Converts a message to bytes which can be send to the UNii.
        """
        raise NotImplementedError


class UNiiRawData(UNiiData, UNiiSendData):
    # pylint: disable=too-few-public-methods
    """
    UNii Raw data class
    """

    def __init__(self, raw_data):
        self.raw_data = raw_data

    def to_bytes(self):
        return self.raw_data

    def __str__(self) -> str:
        return "0x" + self.raw_data.hex()


class UNiiResultCode(UNiiData):
    """
    UNii Result Code data class
    """

    # pylint: disable=too-few-public-methods

    OK: Final = 0x0000
    ERROR: Final = 0x0001


class UNiiEventRecord(UNiiData):
    """
    UNii Event Record data class
    """

    # pylint: disable=too-few-public-methods
    # pylint: disable=too-many-instance-attributes

    event_description: str = None
    user_id: int = None
    user_name: str = None
    input_id: int = None
    input_name: str = None
    device_id: int = None
    device_name: str = None
    bus_id: int = None
    section: int = None
    sia_code: int = None

    def __init__(self, data: bytes):
        # pylint: disable=consider-using-min-builtin
        # pylint: disable=too-many-locals
        """ """
        offset = 0

        # Version
        version = data[1]
        if version != 3:
            raise TypeError()

        # Event Number
        self.event_number = int.from_bytes(data[2:4])

        # Timestamp
        year = 1900 + data[4]
        month = data[5] + 1
        day = data[6]
        hour = data[7]
        minute = data[8]
        second = data[9]
        self.timestamp = datetime(year, month, day, hour, minute, second)

        data = data[10:]

        # Description
        event_description_length = data[0]
        if event_description_length > 0:
            event_description = data[1 : 1 + event_description_length]
            self.event_description = event_description.decode("ascii")

        data = data[1 + event_description_length :]

        # User
        user_id = int.from_bytes(data[0:2])
        if user_id > 0:
            self.user_id = user_id

        user_name_length = data[2]
        if user_name_length > 0:
            user_name = data[3 : 3 + user_name_length]
            self.user_name = user_name.decode("ascii")

        data = data[3 + user_name_length :]

        # Input
        input_id = int.from_bytes(data[0:2])
        if input_id > 0:
            self.input_id = input_id

        input_name_length = data[2]
        if input_name_length > 0:
            input_name = data[3 : 3 + input_name_length]
            self.input_name = input_name.decode("ascii")
            offset += input_name_length

        data = data[3 + input_name_length :]

        # Device
        device_id = int.from_bytes(data[0:2])
        if device_id > 0:
            self.device_id = device_id

        device_name_length = data[2]
        if device_name_length > 0:
            device_name = data[3 : 3 + device_name_length]
            self.device_name = device_name.decode("ascii")
            offset += device_name_length

        data = data[3 + device_name_length :]

        # Bus
        self.bus_id = data[0]

        # Section
        self.section = int.from_bytes(data[1:5])

        # SIA Code
        self.sia_code = data[5:7].decode("ascii")

    def __str__(self) -> str:
        return str(
            {
                "event_number": self.event_number,
                "timestamp": self.timestamp,
                "event_description": self.event_description,
                "user_id": self.user_id,
                "user_name": self.user_name,
                "input_id": self.input_id,
                "input_name": self.input_name,
                "device_id": self.device_id,
                "device_name": self.device_name,
                "bus_id": self.bus_id,
                "section": self.section,
                "sia_code": self.sia_code,
            }
        )


class UNiiInputState(IntEnum):
    """
    The available input states.
    """

    INPUT_OK: Final = 0x0
    ALARM: Final = 0x1
    TAMPER: Final = 0x2
    MASKING: Final = 0x4
    DISABLED: Final = 0xF


class UNiiInputType(IntEnum):
    """
    The available input types.
    """

    WIRED: Final = auto()
    KEYPAD: Final = auto()
    SPARE: Final = auto()
    WIRELESS: Final = auto()
    KNX: Final = auto()
    DOOR: Final = auto()


class UNiiInputStatusRecord(dict):
    """
    UNii Input Status record
    """

    # Get dictionarry keys as attributes.
    __getattr__ = dict.get

    def __init__(self, input_number: int, data: int):
        if input_number <= 511:
            self["type"] = UNiiInputType.WIRED
        elif 512 >= input_number <= 543:
            self["type"] = UNiiInputType.KEYPAD
        elif 544 >= input_number <= 575:
            self["type"] = UNiiInputType.SPARE
        elif 576 >= input_number <= 639:
            self["type"] = UNiiInputType.WIRELESS
        elif 640 >= input_number <= 688:
            self["type"] = UNiiInputType.KNX
        elif 689 >= input_number <= 705:
            self["type"] = UNiiInputType.SPARE
        elif 706 >= input_number <= 962:
            self["type"] = UNiiInputType.DOOR

        self["status"] = UNiiInputState(data & 0x0F)
        self["bypassed"] = data & 0b00010000 == 0b00010000
        self["alarm_memorized"] = data & 0b00100000 == 0b00100000
        # if self["type"] == UNiiInputType.WIRELESS:
        self["low_battery"] = data & 0b01000000 == 0b01000000
        self["supervision"] = data & 0b10000000 == 0b10000000


class UNiiInputStatus(dict, UNiiData):
    # pylint: disable=too-few-public-methods
    """
    UNii Input Status data class
    """

    def __init__(self, data: bytes):
        # Version
        version = data[1]
        if version != 2:
            raise TypeError()

        for input_number, input_status in enumerate(data[2:]):
            input_status = UNiiInputStatusRecord(input_number, input_status)
            self[input_number + 1] = input_status

    # def __str__(self) -> str:
    #     return str(self)


class UNiiDeviceStatusRecord(IntFlag):
    """
    UNii Device Status Record
    """

    LAN_CONNECTION_FAILURE: Final = 32762
    POWER_UNIT_FAILURE_RESTORED: Final = 16384
    POWER_UNIT_FAILURE: Final = 8192
    BATTERY_FAULT_RESTORED: Final = 4096
    BATTERY_FAULT: Final = 2048
    BATTERY_MISSING_RESTORED: Final = 1024
    BATTERY_MISSING: Final = 512
    DEVICE_PRESENT: Final = 256
    RS485_BUS_COMMUNICATION_FAILURE_RESTORED: Final = 128
    RS485_BUS_COMMUNICATION_FAILURE: Final = 64
    TAMPER_SWITCH_OPEN_RESTORED: Final = 32
    TAMPER_SWITCH_OPEN: Final = 16
    LOW_BATTERY_RESTORED: Final = 8
    LOW_BATTERY: Final = 4
    MAINS_FAILURE_RESTORED: Final = 2
    MAINS_FAILURE: Final = 1

    def __str__(self) -> str:
        return self.name


class UNiiDeviceStatus(UNiiData):
    # pylint: disable=too-few-public-methods
    """
    UNii Device Status data class
    """

    io_devices = []
    keyboard_devices = []
    wiegand_devices = []
    uwi_devices = []

    def __init__(self, data: bytes):
        # Version
        # version = data[1]
        # if version != 2:
        #     raise TypeError()

        # Split data in chunks of 2 bytes
        chunks = [data[pos : pos + 2] for pos in range(0, len(data), 2)]
        # Convert chunks to list of Device Status Records
        device_status_records = [
            UNiiDeviceStatusRecord.from_bytes(chunk) for chunk in chunks
        ]

        # Control Panel
        self.control_panel = device_status_records[0]

        # IO Devices
        self.io_devices = device_status_records[1:16]
        # logger.debug("%i IO Devices", len(self.io_devices))

        # Keyboard Devices
        self.keyboard_devices = device_status_records[16:32]
        # logger.debug("%i Keyboard Devices", len(self.keyboard_devices))

        # Wiegand Devices
        self.wiegand_devices = device_status_records[32:48]
        # logger.debug("%i Wiegand Devices", len(self.wiegand_devices))

        # KNX Device
        self.knx_device = device_status_records[48]

        # UWI Devices
        self.uwi_devices = device_status_records[49:51]
        # logger.debug("%i UWI Devices", len(self.uwi_devices))

        # Redundant Device
        self.redundant_device = device_status_records[51]

    def __str__(self) -> str:
        return str(
            {
                "control_panel": self.control_panel,
                "io_devices": self.io_devices,
                "keyboard_devices": self.keyboard_devices,
                "wiegand_devices": self.wiegand_devices,
                "knx_device": self.knx_device,
                "uwi_devices": self.uwi_devices,
                "redundant_device": self.redundant_device,
            }
        )


class UNiiReadyToArmSectionState(UNiiData):
    # pylint: disable=too-few-public-methods
    """
    UNii Ready To Arm Section State data class
    """

    NOT_PROGRAMMED: Final = 0
    SECTION_ARMED: Final = 1
    # SECTION_DISARMED: Final = 2
    SECTION_READY_FOR_ARMING: Final = 3
    SECTION_NOT_READY_FOR_ARMING: Final = 4
    NOT_AUTHORIZED_TO_ARM: Final = 5
    SYSTEM_ERROR: Final = 6

    def __init__(self, data: bytes):
        self.section_number = data[0]
        self.section_state = data[1]


class UNiiArmSectionState(UNiiData):
    # pylint: disable=too-few-public-methods
    """
    UNii Arm Section State data class
    """

    NO_CHANGE: Final = 0
    SECTION_ARMED: Final = 1
    ARMING_FAILED_SECTION_NOT_READY: Final = 2
    ARMING_FAILED_NOT_AUTHORIZED: Final = 3


class UNiiDisarmSectionState(UNiiData):
    # pylint: disable=too-few-public-methods
    """
    UNii Disarm Section State data class
    """

    NO_CHANGE: Final = 0
    SECTION_DISARMED: Final = 1
    DISARMING_FAILED: Final = 2
    DISARMING_FAILED_NOT_AUTHORIZED: Final = 3


class UNiiInput(dict):
    """
    UNii Input
    """

    # Get dictionarry keys as attributes.
    __getattr__ = dict.get

    def __init__(self, data: bytes):
        self["number"] = int.from_bytes(data[0:2])
        self["type"] = data[2]
        self["reaction"] = data[3]
        name_length = data[4]
        name = None
        if name_length > 0:
            name = data[5 : 5 + name_length]
            name = name.decode("ascii")
        self["name"] = name
        self["section"] = data[5 + name_length :]
        self["status"] = None


class UNiiInputArrangement(dict, UNiiData):
    # pylint: disable=too-few-public-methods
    """
    UNii Input Arrangement data class
    """

    def __init__(self, data: bytes):
        """ """
        # Version
        # version = data[1]

        # Block Number
        block_number = int.from_bytes(data[2:4])

        if block_number == 0xFFFF:
            raise TypeError()

        self.block_number = block_number

        offset = 4
        while offset < len(data):
            name_length = data[4 + offset]
            input_information = data[offset : 9 + offset + name_length]
            input_information = UNiiInput(input_information)
            # logger.debug(input_information)
            self[input_information.number] = input_information

            offset += 9 + name_length

    def __str__(self) -> str:
        return str({"block_number": self.block_number, "inputs": super().__str__()})


class UNiiEquipmentInformation(UNiiData):
    # pylint: disable=too-few-public-methods
    """
    UNii Equipment Information data class
    """

    def __init__(self, data: bytes):
        # pylint: disable=consider-using-min-builtin
        # pylint: disable=too-many-locals
        """ """
        # Version
        version = data[1]
        if version != 2:
            raise TypeError()

        self.software_version = data[2:7].decode("ascii")
        software_date = data[7:19].decode("ascii").strip(string.whitespace + "\x00")
        self.software_date = datetime.strptime(software_date, "%d-%m-%Y").date()
        device_name_length = data[19]
        self.device_name = (
            data[20 : 20 + device_name_length]
            .decode("ascii")
            .strip(string.whitespace + "\x00")
        )
        self.max_inputs = data[-5]
        self.max_groups = data[-4]
        self.max_sections = data[-3]
        self.max_users = int.from_bytes(data[-2:])

    def __str__(self) -> str:
        return str(
            {
                "software_version": self.software_version,
                "software_date": self.software_date,
                "device_name": self.device_name,
            }
        )
