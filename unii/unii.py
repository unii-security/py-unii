"""
Classes for interfacing with Alphatronics UNii security systems.
"""

import asyncio
import logging
import time
from abc import ABC
from datetime import datetime, timedelta
from threading import Lock
from typing import Final

from .unii_command import UNiiCommand
from .unii_command_data import (
    UNiiData,
    UNiiDeviceStatus,
    UNiiEquipmentInformation,
    UNiiInputArrangement,
    UNiiInputStatus,
    UNiiRawData,
)
from .unii_connection import (
    DEFAULT_PORT,
    UNiiConnection,
    UNiiConnectionError,
    UNiiTCPConnection,
)

logger = logging.getLogger(__name__)

_POLL_ALIVE_INTERVAL: Final = timedelta(seconds=30)


class UNii(ABC):
    """
    UNii base class for interfacing with Alphatronics UNii security systems.
    """

    unique_id = None
    model = "Unknown"
    connected = False

    equipment_information: UNiiEquipmentInformation = None
    inputs = {}
    device_status: UNiiDeviceStatus = None

    connection: UNiiConnection = None

    _event_occurred_callbacks = []

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
        Adds an Event Occured Callback to the UNii.
        """
        self._event_occurred_callbacks.append(callback)

    def _forward_to_event_occurred_callbacks(
        self, command: UNiiCommand, data: UNiiData
    ):
        for callback in self._event_occurred_callbacks:
            callback(command, data)


class UNiiLocal(UNii):
    # pylint: disable=too-many-instance-attributes
    """
    UNii class for interfacing with Alphatronics UNii security systems on the local
    network.
    """

    _received_message_queue = {}
    _waiting_for_message = []

    _poll_alive_task: asyncio.Task = None
    _stay_connected: bool = False

    def __init__(
        self, host: str, port: int = DEFAULT_PORT, shared_key: (str, bytes) = None
    ):
        # If the shared key is provided as string convert it to bytes.
        if shared_key is not None and isinstance(shared_key, str):
            shared_key = shared_key.encode()
        self.connection = UNiiTCPConnection(host, port, shared_key)
        self.unique_id = f"{host}:{port}"
        self._received_message_queue_lock = Lock()

    async def _connect(self) -> bool:
        await self.connection.connect()

        self.connection.set_message_received_callback(self._message_received_callback)
        response, _ = await self._send_receive(
            UNiiCommand.CONNECTION_REQUEST, None, False
        )
        # response, _ = await self._get_received_message(tx_sequence)
        if response == UNiiCommand.CONNECTION_REQUEST_RESPONSE:
            self.connected = True
            self._stay_connected = True

            self._forward_to_event_occurred_callbacks(response, None)

            await self._send_receive(
                UNiiCommand.REQUEST_EQUIPMENT_INFORMATION, None, False
            )

            await self._send_receive(
                UNiiCommand.REQUEST_INPUT_ARRANGEMENT, UNiiRawData(b"\x00\x01"), False
            )
            await self._send_receive(
                UNiiCommand.REQUEST_INPUT_ARRANGEMENT, UNiiRawData(b"\x00\x02"), False
            )
            await self._send_receive(
                UNiiCommand.REQUEST_INPUT_ARRANGEMENT, UNiiRawData(b"\x00\x03"), False
            )
            await self._send_receive(
                UNiiCommand.REQUEST_INPUT_ARRANGEMENT, UNiiRawData(b"\x00\x04"), False
            )
            await self._send_receive(
                UNiiCommand.REQUEST_INPUT_ARRANGEMENT, UNiiRawData(b"\x00\x05"), False
            )
            await self._send_receive(
                UNiiCommand.REQUEST_INPUT_ARRANGEMENT, UNiiRawData(b"\x00\x06"), False
            )
            await self._send_receive(
                UNiiCommand.REQUEST_INPUT_ARRANGEMENT, UNiiRawData(b"\x00\x07"), False
            )
            await self._send_receive(
                UNiiCommand.REQUEST_INPUT_ARRANGEMENT, UNiiRawData(b"\x00\x08"), False
            )
            await self._send_receive(
                UNiiCommand.REQUEST_INPUT_ARRANGEMENT, UNiiRawData(b"\x00\x09"), False
            )
            await self._send_receive(
                UNiiCommand.REQUEST_INPUT_ARRANGEMENT, UNiiRawData(b"\x00\x0a"), False
            )
            await self._send_receive(
                UNiiCommand.REQUEST_INPUT_ARRANGEMENT, UNiiRawData(b"\x00\x0b"), False
            )
            await self._send_receive(
                UNiiCommand.REQUEST_INPUT_ARRANGEMENT, UNiiRawData(b"\x00\x0c"), False
            )
            await self._send_receive(
                UNiiCommand.REQUEST_INPUT_ARRANGEMENT, UNiiRawData(b"\x00\x0d"), False
            )
            await self._send_receive(
                UNiiCommand.REQUEST_INPUT_ARRANGEMENT, UNiiRawData(b"\x00\x0e"), False
            )

            await self._send_receive(UNiiCommand.REQUEST_INPUT_STATUS, None, False)
            await self._send_receive(UNiiCommand.REQUEST_DEVICE_STATUS, None, False)

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
        self, command: UNiiCommand, data: UNiiData = None, reconnect: bool = True
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

        logger.debug("Sending command %s", command)
        return await self.connection.send(command, data)

    async def _send_receive(
        self, command: UNiiCommand, data: UNiiData = None, reconnect: bool = True
    ) -> [UNiiCommand, UNiiData]:
        tx_sequence = await self._send(command, data, reconnect)
        if tx_sequence is not None:
            return await self._get_received_message(tx_sequence)
        return [None, None]

    def _handle_input_status_changed(self, data: UNiiInputStatus):
        for input_number, input_status in data.items():
            if input_number in self.inputs:
                self.inputs[input_number].update(input_status)
            else:
                pass

    def _handle_input_arrangement(self, data: UNiiInputArrangement):
        for input_number, unii_input in data.items():
            if input_number not in self.inputs:
                self.inputs[input_number] = unii_input
            else:
                self.inputs[input_number].update(unii_input)

    async def _message_received_callback(
        self, tx_sequence: int, command: UNiiCommand, data: UNiiData
    ):
        match command:
            case UNiiCommand.EVENT_OCCURRED:
                self._forward_to_event_occurred_callbacks(command, data)
                await self._send(UNiiCommand.RESPONSE_EVENT_OCCURRED, None, False)
            case UNiiCommand.INPUT_STATUS_CHANGED:
                self._handle_input_status_changed(data)
                # self.inputs = data
            case UNiiCommand.DEVICE_STATUS_CHANGED:
                self.device_status = data
            case UNiiCommand.RESPONSE_REQUEST_INPUT_ARRANGEMENT:
                self._handle_input_arrangement(data)
            case UNiiCommand.RESPONSE_REQUEST_EQUIPMENT_INFORMATION:
                self.equipment_information = data

        if tx_sequence in self._waiting_for_message:
            with self._received_message_queue_lock:
                self._received_message_queue[tx_sequence] = [command, data]

        self._forward_to_event_occurred_callbacks(command, data)

    async def _get_received_message(self, tx_sequence: int) -> [UNiiCommand, UNiiData]:
        timeout = time.time() + 1
        self._waiting_for_message.append(tx_sequence)
        while self.connection.is_open and time.time() < timeout:
            with self._received_message_queue_lock:
                if tx_sequence in self._received_message_queue:
                    return self._received_message_queue.pop(tx_sequence)
            # logger.debug("Waiting for message %i to be received", tx_sequence)
            await asyncio.sleep(0.1)

        logger.error("Message %i was not recieved", tx_sequence)
        self._waiting_for_message.remove(tx_sequence)
        return [None, None]

    async def _poll_alive(self) -> bool:
        try:
            tx_sequence = await self._send(UNiiCommand.POLL_ALIVE_REQUEST)
            response, _ = await self._get_received_message(tx_sequence)
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
        logger.debug("Poll Alive coroutine stopped")
