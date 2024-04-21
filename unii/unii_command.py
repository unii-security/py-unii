"""
Commands used by the Alphatronics UNii.
"""

from enum import IntEnum
from typing import Final


class UNiiCommand(IntEnum):
    """
    UNii Commands
    """

    # Connection setup
    CONNECTION_REQUEST: Final = 0x0001
    CONNECTION_REQUEST_RESPONSE: Final = 0x0002
    CONNECTION_REQUEST_DENIED: Final = 0x0003
    NORMAL_DISCONNECT: Final = 0x0014

    # Operational commands
    POLL_ALIVE_REQUEST: Final = 0x0012
    POLL_ALIVE_RESPONSE: Final = 0x0013
    GENERAL_RESPONSE: Final = 0x0101
    EVENT_OCCURRED: Final = 0x0102
    RESPONSE_EVENT_OCCURRED: Final = 0x0103
    FLUSH_EVENT_BUFFER: Final = 0x0104
    INPUT_STATUS_CHANGED: Final = 0x0105
    REQUEST_INPUT_STATUS: Final = 0x0106
    DEVICE_STATUS_CHANGED: Final = 0x0107
    REQUEST_DEVICE_STATUS: Final = 0x0108
    CLEAR_ALARM_MEMORY: Final = 0x0109
    REQUEST_READY_TO_ARM_SECTIONS: Final = 0x0110
    RESPONSE_READY_TO_ARM_SECTIONS: Final = 0x0111
    REQUEST_ARM_SECTION: Final = 0x0112
    RESPONSE_ARM_SECTION: Final = 0x0113
    REQUEST_DISARM_SECTION: Final = 0x0114
    RESPONSE_DISARM_SECTION: Final = 0x0115
    REQUEST_SECTION_STATUS: Final = 0x0116
    RESPONSE_REQUEST_SECTION_STATUS: Final = 0x0117
    REQUEST_TO_BYPASS_AN_INPUT: Final = 0x0118
    RESPONSE_REQUEST_TO_BYPASS_AN_INPUT: Final = 0x0119
    REQUEST_TO_UNBYPASS_AN_INPUT: Final = 0x011A
    RESPONSE_REQUEST_TO_UNBYPASS_AN_INIPUT: Final = 0x011B
    REQUEST_TO_SET_OUTPUT: Final = 0x011C
    RESPONSE_REQUEST_TO_SET_OUTPUT: Final = 0x011D
    REQUEST_OUTPUT_STATUS: Final = 0x011E
    RESPONSE_REQUEST_OUTPUT_STATUS: Final = 0x011F
    # REQUEST TO SET OUTPUT(S) WITH USER CODE: Final = 0X0120
    # RESPONSE REQUEST TO SET OUTPUT(S) WITH USER CODE: Final = 0X0121
    REQUEST_TO_RESET_ALARM: Final = 0x0122
    RESPONSE_REQUEST_TO_RESET_ALARM: Final = 0x0123
    EXIT_ENTRY_TIMER: Final = 0x0124

    # Configuration commands
    REQUEST_SECTION_ARRANGEMENT: Final = 0x0130
    RESPONSE_REQUEST_SECTION_ARRANGEMENT: Final = 0x0131
    REQUEST_GROUP_ARRANGEMENT: Final = 0x0132
    RESPONSE_REQUEST_GROUP_ARRANGEMENT: Final = 0x0133
    REQUEST_INPUT_ARRANGEMENT: Final = 0x0140
    RESPONSE_REQUEST_INPUT_ARRANGEMENT: Final = 0x0141
    REQUEST_EQUIPMENT_INFORMATION: Final = 0x0142
    RESPONSE_REQUEST_EQUIPMENT_INFORMATION: Final = 0x0143
    REQUEST_DATE_AND_TIME: Final = 0x0144
    RESPONSE_REQUEST_DATE_AND_TIME: Final = 0x0145
    WRITE_DATE_AND_TIME: Final = 0x0146
    RESPONSE_WRITE_DATE_AND_TIME: Final = 0x0147

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name
