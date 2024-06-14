"""
Tests encrypted connection to Alphatronics UNii.
"""

import asyncio
import json
import logging
import unittest

from unii import DEFAULT_PORT, UNiiLocal

from . import async_test

_SETTINGS_JSON = "settings.json"

_LOGGER = logging.getLogger(__name__)


class Test(unittest.TestCase):
    """
    Unit test for encrypted connecting to Alphatronics UNii.
    """

    _host = None
    _port: int = DEFAULT_PORT

    def setUp(self):
        # logging.basicConfig(
        #     format="%(asctime)s %(levelname)-8s %(message)s", level=logging.DEBUG
        # )
        with open(_SETTINGS_JSON, encoding="utf8") as settings_file:
            settings = json.load(settings_file)
            self._host = settings.get("host")
            self._port = settings.get("encrypted_port", self._port)

    @async_test
    async def test_connect_byte_array(self):
        """
        Test connecting to Alphatronics UNii.
        """
        shared_key = b"halloditiseenkey"

        await asyncio.sleep(1)
        unii = UNiiLocal(self._host, self._port, shared_key)
        try:
            result = await unii.test_connection()
            self.assertTrue(result, "Failed to connect to UNii")
        finally:
            # await asyncio.sleep(1)
            await unii.disconnect()

    @async_test
    async def test_connect_string_encode(self):
        """
        Test connecting to Alphatronics UNii.
        """
        shared_key = "halloditiseenkey".encode()

        await asyncio.sleep(1)
        unii = UNiiLocal(self._host, self._port, shared_key)
        try:
            result = await unii.test_connection()
            self.assertTrue(result, "Failed to connect to UNii")
        finally:
            # await asyncio.sleep(1)
            await unii.disconnect()

    @async_test
    async def test_connect_hex_string(self):
        """
        Test connecting to Alphatronics UNii.
        """
        shared_key = "68616C6C6F646974697365656E6B6579"

        await asyncio.sleep(1)
        unii = UNiiLocal(self._host, self._port, shared_key)
        try:
            result = await unii.test_connection()
            self.assertTrue(result, "Failed to connect to UNii")
        finally:
            # await asyncio.sleep(1)
            await unii.disconnect()

    @async_test
    async def test_connect_bytes_fromhex(self):
        """
        Test connecting to Alphatronics UNii.
        """
        shared_key = bytes.fromhex("68616C6C6F646974697365656E6B6579")

        await asyncio.sleep(1)
        unii = UNiiLocal(self._host, self._port, shared_key)
        try:
            result = await unii.test_connection()
            self.assertTrue(result, "Failed to connect to UNii")
        finally:
            # await asyncio.sleep(1)
            await unii.disconnect()


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
