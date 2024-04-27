# pylint: disable=R0801
"""
Test Device Status.
"""
import asyncio
import json
import logging
import unittest

from unii import UNiiLocal

from . import async_test

_SETTINGS_JSON = "settings.json"

_LOGGER = logging.getLogger(__name__)


class Test(unittest.TestCase):
    """
    Test Device Status.
    """

    _unii = None

    def setUp(self):
        with open(_SETTINGS_JSON, encoding="utf8") as settings_file:
            settings = json.load(settings_file)
            host = settings.get("host")
            port = settings.get("encrypted_port", 6502)
            shared_key = settings.get("shared_key", 6502)

            self._unii = UNiiLocal(host, port, shared_key)

    @async_test
    async def test_device_status(self):
        """
        Test connecting to Alphatronics UNii.
        """
        await asyncio.sleep(1)
        try:
            result = await self._unii.connect()
            self.assertTrue(result, "Failed to connect to UNii")
            self.assertIsNotNone(self._unii.device_status, "Device Status not set")
            _LOGGER.debug(self._unii.device_status)
            self.assertEqual(len(self._unii.device_status.io_devices), 15)
            self.assertEqual(len(self._unii.device_status.keyboard_devices), 16)
            self.assertEqual(len(self._unii.device_status.wiegand_devices), 16)
            self.assertEqual(len(self._unii.device_status.uwi_devices), 2)
        finally:
            await asyncio.sleep(1)
            await self._unii.disconnect()


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
