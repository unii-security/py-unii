# pylint: disable=protected-access
# pylint: disable=R0801
"""
Tests encrypted connection to Alphatronics UNii.
"""

import asyncio
import json
import logging
import unittest

from unii import UNiiEncryptionError, UNiiLocal

from . import async_test

_SETTINGS_JSON = "settings.json"

_LOGGER = logging.getLogger(__name__)


class Test(unittest.TestCase):
    """
    Unit test for encrypted connecting to Alphatronics UNii.
    """

    _host = None
    _port: int = 6502
    _shared_key = None

    def setUp(self):
        # logging.basicConfig(
        #     format="%(asctime)s %(levelname)-8s %(message)s", level=logging.DEBUG
        # )
        with open(_SETTINGS_JSON, encoding="utf8") as settings_file:
            settings = json.load(settings_file)
            self._host = settings.get("host")
            self._port = settings.get("encrypted_port", self._port)
            self._shared_key = bytes.fromhex(settings.get("shared_key"))

    def test_create_unii_object(self):
        """
        Test creating an Alphatronics UNii object
        """
        unii = UNiiLocal(self._host, self._port, self._shared_key)
        self.assertIsNotNone(unii)

    @async_test
    async def test_connect(self):
        """
        Test connecting to Alphatronics UNii.
        """
        await asyncio.sleep(1)
        unii = UNiiLocal(self._host, self._port, self._shared_key)
        try:
            result = await unii.connect()
            self.assertTrue(result, "Failed to connect to UNii")
        finally:
            await asyncio.sleep(1)
            await unii.disconnect()

    @async_test
    async def test_connect_unavailable_host(self):
        """
        Test connecting to Alphatronics UNii.
        """
        await asyncio.sleep(1)
        unii = UNiiLocal("127.0.0.1", self._port, self._shared_key)
        try:
            result = await unii.connect()
            self.assertFalse(result, "Failed to connect to UNii")
        finally:
            await asyncio.sleep(1)
            await unii.disconnect()

    @async_test
    async def test_connect_invalid_shared_key(self):
        """
        Test connecting to Alphatronics UNii.
        """
        await asyncio.sleep(1)
        unii = UNiiLocal(self._host, self._port, b"invalidsharedkey")
        with self.assertRaises(UNiiEncryptionError):
            await unii.connect()

    @async_test
    async def test_disconnect(self):
        """
        Test disconnectiong from Alphatronics UNii.
        """
        await asyncio.sleep(1)
        unii = UNiiLocal(self._host, self._port, self._shared_key)
        await unii.connect()
        await asyncio.sleep(1)
        result = await unii.disconnect()
        self.assertTrue(result, "Failed to disconnect from UNii")

    @async_test
    async def test_poll_alive(self):
        """
        Test Poll Alive request.
        """
        await asyncio.sleep(1)
        unii = UNiiLocal(self._host, self._port, self._shared_key)
        try:
            await unii.connect()
            await asyncio.sleep(3)
            result = await unii._poll_alive()
            self.assertTrue(result, "Failed to poll alive UNii")
        finally:
            await asyncio.sleep(1)
            await unii.disconnect()

    @async_test
    async def test_poll_alive_timeout(self):
        """
        Test Poll Alive timeout.

        To keep the connection alive (and NAT entries active) a poll message has to be sent every
        30 seconds if no other messages where sent during the last 30 seconds.

        The UNii takes care of sending this poll message and should keep the connection
        alive.
        """
        await asyncio.sleep(1)
        unii = UNiiLocal(self._host, self._port, self._shared_key)
        try:
            await unii.connect()
            await asyncio.sleep(50)
            self.assertTrue(unii.connection.is_open, "Connection is not open")
        finally:
            await unii.disconnect()

    @async_test
    async def test_poll_alive_3x(self):
        """
        Test connecting to Alphatronics UNii
        """
        await asyncio.sleep(1)
        unii = UNiiLocal(self._host, self._port, self._shared_key)
        try:
            await unii.connect()
            n = 3
            for i in range(n):
                await asyncio.sleep(3)
                _LOGGER.debug("Poll alive %i/%i", i + 1, n)
                result = await unii._poll_alive()
                with self.subTest(msg="Poll alive"):
                    self.assertTrue(result, "Failed to poll alive UNii")
                    _LOGGER.debug("Poll alive %i/%i success", i + 1, n)
        finally:
            await asyncio.sleep(1)
            await unii.disconnect()

    @async_test
    async def test_poll_alive_10x(self):
        """
        Test connecting to Alphatronics UNii
        """
        await asyncio.sleep(1)
        unii = UNiiLocal(self._host, self._port, self._shared_key)
        try:
            await unii.connect()
            n = 10
            for i in range(n):
                await asyncio.sleep(1)
                _LOGGER.debug("Poll alive %i/%i", i + 1, n)
                result = await unii._poll_alive()
                with self.subTest(msg="Poll alive"):
                    self.assertTrue(result, "Failed to poll alive UNii")
                    _LOGGER.debug("Poll alive %i/%i success", i + 1, n)
        finally:
            await asyncio.sleep(1)
            await unii.disconnect()


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
