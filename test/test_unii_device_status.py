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
            port = settings.get("unencrypted_port", 6502)

            self._unii = UNiiLocal(host, port)

    def tearDown(self):
        pass

    @async_test
    async def test_device_status(self):
        """
        Test connecting to Alphatronics UNii.
        """
        try:
            result = await self._unii.connect()
            self.assertTrue(result, "Failed to connect to UNii")
            # while self._unii.device_status is None:
            #     await asyncio.sleep(0.1)
            self.assertIsNotNone(self._unii.device_status, "Device Status not set")
        finally:
            await asyncio.sleep(1)
            await self._unii.disconnect()


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
