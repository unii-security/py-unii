"""
Classes for interfacing with Alphatronics UNii security systems.
"""

import asyncio
import logging
import time
from abc import ABC
from datetime import datetime, timedelta
from enum import IntFlag, auto
from threading import Lock
from typing import Any, Final

from .unii_command import UNiiCommand
from .unii_command_data import (
    UNiiArmDisarmSection,
    UNiiArmSectionStatus,
    UNiiArmState,
    UNiiData,
    UNiiDeviceStatus,
    UNiiDisarmSectionStatus,
    UNiiDisarmState,
    UNiiEquipmentInformation,
    UNiiInput,
    UNiiInputArrangement,
    UNiiInputState,
    UNiiInputStatus,
    UNiiInputStatusRecord,
    UNiiOutput,
    UNiiRawData,
    UNiiSection,
    UNiiSectionArrangement,
    UNiiSectionStatus,
)
from .unii_connection import (
    DEFAULT_PORT,
    UNiiConnection,
    UNiiConnectionError,
    UNiiTCPConnection,
)
from .unii_message import UNiiResponseMessage

logger = logging.getLogger(__name__)

_POLL_ALIVE_INTERVAL: Final = timedelta(seconds=30)


class UNiiFeature(IntFlag):
    """Features implemented by the UNii library."""

    ARM_SECTION: Final = auto()
    BYPASS_ZONE: Final = auto()
    SET_OUTPUT: Final = auto()


class UNii(ABC):
    """
    UNii base class for interfacing with Alphatronics UNii security systems.
    """

    unique_id: str | None = None
    model: str = "Unknown"
    connected: bool = False

    equipment_information: UNiiEquipmentInformation | None = None
    sections: dict[int, UNiiSection] = {}
    inputs: dict[int, UNiiInput] = {}
    outputs: dict[int, UNiiOutput] = {}
    device_status: UNiiDeviceStatus | None = None

    connection: UNiiConnection

    features: list[UNiiFeature] = []

    _event_occurred_callbacks: list[Any] = []

    def __init__(
        self,
    ):
        pass

    async def connect(self) -> bool:
        """
        Connect to Alphatronics UNii
        """
        raise NotImplementedError

    async def disconnect(self) -> bool:
        """
        Disconnect from Alphatronics UNii
        """
        raise NotImplementedError

    def add_event_occurred_callback(self, callback):
        """
        Adds an Event Occurred Callback to the UNii.
        """
        self._event_occurred_callbacks.append(callback)

    def _forward_to_event_occurred_callbacks(
        self, command: UNiiCommand, data: UNiiData | None
    ):
        for callback in self._event_occurred_callbacks:
            try:
                callback(command, data)
            # pylint: disable=broad-exception-caught
            except Exception as ex:
                logger.error("Exception in Event Occurred Callback: %s", ex)

    async def arm_section(self, number: int, code: str) -> bool:
        """Arm a section."""
        raise NotImplementedError

    async def disarm_section(self, number: int, code: str) -> bool:
        """Disarm a section."""
        raise NotImplementedError


class UNiiLocal(UNii):
    # pylint: disable=too-many-instance-attributes
    """
    UNii class for interfacing with Alphatronics UNii security systems on the local
    network.
    """

    _received_message_queue: dict[int, list[Any]] = {}
    _waiting_for_message: dict[int, UNiiCommand | None] = {}

    _poll_alive_task: asyncio.Task | None = None
    _stay_connected: bool = False

    def __init__(
        self, host: str, port: int = DEFAULT_PORT, shared_key: bytes | None = None
    ):
        # If the shared key is provided as hex string convert it to bytes.
        if shared_key is not None and isinstance(shared_key, str):
            shared_key = bytes.fromhex(shared_key)
        self.connection = UNiiTCPConnection(host, port, shared_key)
        self.unique_id = f"{host}:{port}"
        self._received_message_queue_lock = Lock()

    async def _connect(self) -> bool:
        await self.connection.connect()

        self.connection.set_message_received_callback(self._message_received_callback)
        response, _ = await self._send_receive(
            UNiiCommand.CONNECTION_REQUEST,
            None,
            UNiiCommand.CONNECTION_REQUEST_RESPONSE,
            False,
        )
        if response == UNiiCommand.CONNECTION_REQUEST_RESPONSE:
            response, data = await self._send_receive(
                UNiiCommand.REQUEST_EQUIPMENT_INFORMATION,
                None,
                UNiiCommand.RESPONSE_REQUEST_EQUIPMENT_INFORMATION,
                False,
            )
            if (
                response is None
                or data is None
                or response != UNiiCommand.RESPONSE_REQUEST_EQUIPMENT_INFORMATION
            ):
                self._disconnect()
                return False

            await self._send_receive(
                UNiiCommand.REQUEST_SECTION_ARRANGEMENT,
                None,
                UNiiCommand.RESPONSE_REQUEST_SECTION_ARRANGEMENT,
                False,
            )

            for _, section in self.sections.items():
                await self._send_receive(
                    UNiiCommand.REQUEST_SECTION_STATUS,
                    UNiiRawData(section.number.to_bytes(1)),
                    UNiiCommand.RESPONSE_REQUEST_SECTION_STATUS,
                    False,
                )

            block = 0
            while True:
                block += 1
                _, data = await self._send_receive(
                    UNiiCommand.REQUEST_INPUT_ARRANGEMENT,
                    UNiiRawData(block.to_bytes(2)),
                    UNiiCommand.RESPONSE_REQUEST_INPUT_ARRANGEMENT,
                    False,
                )
                if data is None:
                    break

            await self._send_receive(
                UNiiCommand.REQUEST_INPUT_STATUS,
                None,
                UNiiCommand.INPUT_STATUS_CHANGED,
                False,
            )

            if self.equipment_information is not None:
                try:
                    software_version = (
                        self.equipment_information.software_version.finalize_version()
                    )
                    if software_version.match(">=2.17.0"):
                        block = 0
                        while True:
                            block += 1
                            _, data = await self._send_receive(
                                UNiiCommand.REQUEST_OUTPUT_ARRANGEMENT,
                                UNiiRawData(block.to_bytes(2)),
                                UNiiCommand.RESPONSE_REQUEST_OUTPUT_ARRANGEMENT,
                                False,
                            )
                            if data is None:
                                break
                except ValueError as ex:
                    logger.warning(ex)

            await self._send_receive(
                UNiiCommand.REQUEST_DEVICE_STATUS,
                None,
                UNiiCommand.DEVICE_STATUS_CHANGED,
                False,
            )

            self.connected = True
            self._stay_connected = True

            self._forward_to_event_occurred_callbacks(
                UNiiCommand.CONNECTION_REQUEST_RESPONSE, None
            )

            return True
        return False

    async def connect(self) -> bool:
        try:
            if await self._connect():
                self._poll_alive_task = asyncio.create_task(
                    self._poll_alive_coroutine()
                )
                return True
        except UNiiConnectionError as ex:
            logger.error(str(ex))

        return False

    async def _disconnect(self) -> bool:
        await self._send(UNiiCommand.NORMAL_DISCONNECT, None, False)
        self.connected = False
        # Re-using the Normal Disconnect command to let the Event Occurred Callbacks know the UNii
        # is disconnected.
        self._forward_to_event_occurred_callbacks(UNiiCommand.NORMAL_DISCONNECT, None)
        return await self.connection.close()

    async def disconnect(self) -> bool:
        self._stay_connected = False

        if self.connection is not None and self.connection.is_open:
            try:
                if not await self._disconnect():
                    return False
            except UNiiConnectionError as ex:
                logger.error(str(ex))
                return False

        if self._poll_alive_task is not None:
            await self._poll_alive_task
        return True

    async def _send(
        self, command: UNiiCommand, data: UNiiData | None = None, reconnect: bool = True
    ) -> int:
        if self.connection is None and reconnect:
            logger.info("Trying to reconnect")
            await self._connect()
        elif not self.connection.is_open and reconnect:
            logger.info("Connection lost, trying to reconnect")
            await self._disconnect()
            await self._connect()
        elif self.connection is None or not self.connection.is_open:
            # ToDo: Throw exception?
            return None

        # logger.debug("Sending command %s", command)
        return await self.connection.send(command, data)

    async def _send_receive(
        self,
        command: UNiiCommand,
        data: UNiiData | None = None,
        expected_response: UNiiCommand | None = None,
        reconnect: bool = True,
    ) -> list[Any]:
        tx_sequence = await self._send(command, data, reconnect)
        if tx_sequence is not None:
            return await self._get_received_message(tx_sequence, expected_response)
        return [None, None]

    def _handle_equipment_information(self, data: UNiiEquipmentInformation):
        self.equipment_information = data

        # Get capabilities based on firmware version number
        # Library is currently read-only, so disabled for now
        # if self.equipment_information is not None:
        #     try:
        #         software_version = (
        #             self.equipment_information.software_version.finalize_version()
        #         )
        #         if software_version.match(">=2.17.0"):
        #             self.features.append(UNiiFeature.ARM_SECTION)
        #             self.features.append(UNiiFeature.BYPASS_ZONE)
        #             self.features.append(UNiiFeature.SET_OUTPUT)
        #     except ValueError as ex:
        #         logger.warning(ex)

    def _handle_section_arrangement(self, data: UNiiSectionArrangement):
        for _, section in data.items():
            if section.number not in self.inputs:
                self.sections[section.number] = section
            else:
                self.sections[section.number].update(section)

    def _handle_section_status(self, section_status: UNiiSectionStatus):
        if section_status.number in self.sections:
            self.sections[section_status.number]["armed_state"] = section_status[
                "armed_state"
            ]
        else:
            # This should never happen
            logger.warning(
                "Status for unknown section %i changed", section_status.number
            )

    def _handle_input_status_update(self, input_status: UNiiInputStatusRecord):
        if input_status.number in self.inputs:
            self.inputs[input_status.number].update(input_status)
        elif input_status.status != UNiiInputState.DISABLED:
            # This should never happen
            logger.warning("Status for unknown input %i changed", input_status.number)

    def _handle_input_status_changed(self, data: UNiiInputStatus):
        for _, input_status in data.items():
            self._handle_input_status_update(input_status)

    def _handle_input_arrangement(self, data: UNiiInputArrangement):
        if data is None:
            return
        for _, unii_input in data.items():
            # Expand sections
            for index, section in enumerate(unii_input.sections):
                unii_input["sections"][index] = self.sections[section]

            if unii_input.number not in self.inputs:
                self.inputs[unii_input.number] = unii_input
            else:
                # Retain the input status before updating the input with new data.
                unii_input.status = self.inputs[unii_input.number].status
                self.inputs[unii_input.number].update(unii_input)

    async def _message_received_callback(
        self, tx_sequence: int, command: UNiiCommand, data: UNiiData
    ):
        match command:
            case UNiiCommand.EVENT_OCCURRED:
                self._forward_to_event_occurred_callbacks(command, data)
                if self.connected:
                    await self._send(UNiiCommand.RESPONSE_EVENT_OCCURRED, None, False)
            case UNiiCommand.INPUT_STATUS_CHANGED:
                self._handle_input_status_changed(data)
            case UNiiCommand.INPUT_STATUS_UPDATE:
                self._handle_input_status_update(data)
            case UNiiCommand.DEVICE_STATUS_CHANGED:
                self.device_status = data
            case UNiiCommand.RESPONSE_REQUEST_SECTION_ARRANGEMENT:
                self._handle_section_arrangement(data)
            case UNiiCommand.RESPONSE_REQUEST_SECTION_STATUS:
                self._handle_section_status(data)
            case UNiiCommand.RESPONSE_REQUEST_INPUT_ARRANGEMENT:
                self._handle_input_arrangement(data)
            case UNiiCommand.RESPONSE_REQUEST_EQUIPMENT_INFORMATION:
                self._handle_equipment_information(data)

        if tx_sequence in self._waiting_for_message and self._waiting_for_message[
            tx_sequence
        ] in [None, command]:
            with self._received_message_queue_lock:
                self._received_message_queue[tx_sequence] = [command, data]

        self._forward_to_event_occurred_callbacks(command, data)

    async def _get_received_message(
        self, tx_sequence: int, expected_response: UNiiCommand | None = None
    ) -> list[Any]:
        timeout = time.time() + 5
        self._waiting_for_message[tx_sequence] = expected_response
        while self.connection.is_open and time.time() < timeout:
            with self._received_message_queue_lock:
                if tx_sequence in self._received_message_queue:
                    return self._received_message_queue.pop(tx_sequence)
            # logger.debug("Waiting for message %i to be received", tx_sequence)
            await asyncio.sleep(0.1)

        logger.error("Message %i was not received", tx_sequence)
        del self._waiting_for_message[tx_sequence]
        return [None, None]

    async def _poll_alive(self) -> bool:
        try:
            response, _ = await self._send_receive(
                UNiiCommand.POLL_ALIVE_REQUEST,
                None,
                UNiiCommand.POLL_ALIVE_RESPONSE,
                False,
            )
            # logger.debug("Response received: %s", response)
            if response == UNiiCommand.POLL_ALIVE_RESPONSE:
                # logger.debug("Poll Alive success")
                return True
        except UNiiConnectionError as ex:
            logger.error(str(ex))

        logger.error("Poll Alive failed")
        return False

    async def _poll_alive_coroutine(self):
        """
        To keep the connection alive (and NAT entries active) a poll message has to be sent every
        30 seconds if no other messages where sent during the last 30 seconds.
        """
        while self._stay_connected:
            if (
                datetime.now()
                > self.connection.last_message_sent + _POLL_ALIVE_INTERVAL
                and not await self._poll_alive()
            ):
                if self.connection.is_open:
                    await self._disconnect()
            await asyncio.sleep(1)
        # logger.debug("Poll Alive coroutine stopped")

    async def arm_section(self, number: int, code: str) -> bool:
        """Arm a section."""
        response, data = await self._send_receive(
            UNiiCommand.REQUEST_ARM_SECTION,
            UNiiArmDisarmSection(code, number),
            UNiiCommand.RESPONSE_ARM_SECTION,
        )
        if response == UNiiCommand.RESPONSE_ARM_SECTION and data.arm_state in [
            UNiiArmState.SECTION_ARMED,
            UNiiArmState.NO_CHANGE,
        ]:
            return True

        logger.error("Arming failed: %s", data.arm_state)
        return False

    async def disarm_section(self, number: int, code: str) -> bool:
        """Disarm a section."""
        response, data = await self._send_receive(
            UNiiCommand.REQUEST_DISARM_SECTION,
            UNiiArmDisarmSection(code, number),
            UNiiCommand.RESPONSE_DISARM_SECTION,
        )
        if response == UNiiCommand.RESPONSE_DISARM_SECTION and data.disarm_state in [
            UNiiDisarmState.SECTION_DISARMED,
            UNiiDisarmState.NO_CHANGE,
        ]:
            return True

        if data is not None:
            logger.error("Disarming failed: %s", data.disarm_state)
        else:
            logger.error("Disarming failed")
        return False
