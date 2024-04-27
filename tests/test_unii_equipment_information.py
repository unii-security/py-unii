# pylint: disable=R0801
"""
Test Equipment Information.
"""
import asyncio
import json
import logging
import unittest

from unii import UNiiLocal

from . import async_test

_SETTINGS_JSON = "settings.json"

_LOGGER = logging.getLogger(__name__)

# These values apply to my system, check the specs of your system and adjust accordingly.
MAX_INPUTS = 978
MAX_GROUPS = 32
MAX_SECTIONS = 4
MAX_USERS = 50


class Test(unittest.TestCase):
    """
    Test Equipment Information.
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
    async def test_equipment_information(self):
        """
        Test connecting to Alphatronics UNii.
        """
        await asyncio.sleep(1)
        try:
            result = await self._unii.connect()
            self.assertTrue(result, "Failed to connect to UNii")
            self.assertIsNotNone(self._unii.equipment_information)
            _LOGGER.debug(self._unii.equipment_information)
            self.assertEqual(
                self._unii.equipment_information.device_name,
                "Unii",
                "Device name does not match",
            )
            self.assertEqual(self._unii.equipment_information.max_inputs, MAX_INPUTS)
            self.assertEqual(self._unii.equipment_information.max_groups, MAX_GROUPS)
            self.assertEqual(
                self._unii.equipment_information.max_sections, MAX_SECTIONS
            )
            self.assertEqual(self._unii.equipment_information.max_users, MAX_USERS)
        finally:
            await asyncio.sleep(1)
            await self._unii.disconnect()


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
