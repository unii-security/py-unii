# pylint: disable=R0801
"""
Test Input Status.
"""

import asyncio
import json
import logging
import unittest

from unii import DEFAULT_PORT, UNiiLocal

_SETTINGS_JSON = "settings.json"

_LOGGER = logging.getLogger(__name__)


class Test(unittest.IsolatedAsyncioTestCase):
    """
    Test Input Status.
    """

    _unii = None
    user_code = None

    def setUp(self):
        with open(_SETTINGS_JSON, encoding="utf8") as settings_file:
            settings = json.load(settings_file)
            host = settings.get("host")
            port = settings.get("encrypted_port", DEFAULT_PORT)
            shared_key = settings.get("shared_key")
            self.user_code = settings.get("user_code", "000000")

            self._unii = UNiiLocal(host, port, shared_key)

    async def test_sections(self):
        """
        Test connecting to Alphatronics UNii.
        """
        await asyncio.sleep(1)
        try:
            result = await self._unii.connect()
            self.assertTrue(result, "Failed to connect to UNii")
            self.assertIsNotNone(self._unii.sections, "Sections not set")
            for _, section in self._unii.sections.items():
                _LOGGER.info(section)
        finally:
            await asyncio.sleep(1)
            await self._unii.disconnect()

    async def test_arm_section(self):
        """
        Tests the arming of a section.
        """
        await asyncio.sleep(1)
        try:
            result = await self._unii.connect()
            self.assertTrue(result, "Failed to connect to UNii")
            self.assertIsNotNone(self._unii.sections, "Sections not set")
            await self._unii.disarm_section(1, self.user_code)
            result = await self._unii.arm_section(1, self.user_code)
            self.assertTrue(result, "Failed to arm section")
            await self._unii.disarm_section(1, self.user_code)
        finally:
            await asyncio.sleep(1)
            await self._unii.disconnect()

    async def test_disarm_section(self):
        """
        Tests the disarming of a section.
        """
        await asyncio.sleep(1)
        try:
            result = await self._unii.connect()
            self.assertTrue(result, "Failed to connect to UNii")
            self.assertIsNotNone(self._unii.sections, "Sections not set")
            await self._unii.arm_section(1, self.user_code)
            result = await self._unii.disarm_section(1, self.user_code)
            self.assertTrue(result, "Failed to disarm section")
        finally:
            await asyncio.sleep(1)
            await self._unii.disconnect()


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
