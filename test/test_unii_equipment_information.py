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


class Test(unittest.TestCase):
    """
    Test Equipment Information.
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
    async def test_equipment_information(self):
        """
        Test connecting to Alphatronics UNii.
        """
        try:
            result = await self._unii.connect()
            self.assertTrue(result, "Failed to connect to UNii")
            self.assertIsNotNone(self._unii.equipment_information)
            self.assertEqual(
                self._unii.equipment_information.device_name,
                "Unii",
                "Device name does not match",
            )
            self.assertEqual(self._unii.equipment_information.max_inputs, 210)
            self.assertEqual(self._unii.equipment_information.max_groups, 32)
            self.assertEqual(self._unii.equipment_information.max_sections, 4)
            self.assertEqual(self._unii.equipment_information.max_users, 50)
        finally:
            await asyncio.sleep(1)
            await self._unii.disconnect()


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
