# pylint: disable=R0801
"""
Test Input Status.
"""
import asyncio
import json
import logging
import unittest

from unii import UNiiInputState, UNiiLocal

from . import async_test

_SETTINGS_JSON = "settings.json"

_LOGGER = logging.getLogger(__name__)


class Test(unittest.TestCase):
    """
    Test Input Status.
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
    async def test_inputs(self):
        """
        Test connecting to Alphatronics UNii.
        """
        await asyncio.sleep(1)
        try:
            result = await self._unii.connect()
            self.assertTrue(result, "Failed to connect to UNii")
            self.assertIsNotNone(self._unii.inputs, "Input Status not set")
            for _, unii_input in self._unii.inputs.items():
                if unii_input.status != UNiiInputState.DISABLED:
                    _LOGGER.info(unii_input)
        finally:
            await asyncio.sleep(1)
            await self._unii.disconnect()


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
