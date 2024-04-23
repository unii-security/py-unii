# pylint: disable=R0801
"""
Test Input Status.
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
    async def test_sections(self):
        """
        Test connecting to Alphatronics UNii.
        """
        try:
            result = await self._unii.connect()
            self.assertTrue(result, "Failed to connect to UNii")
            self.assertIsNotNone(self._unii.sections, "Sections not set")
            for _, section in self._unii.sections.items():
                _LOGGER.info(section)
        finally:
            await asyncio.sleep(1)
            await self._unii.disconnect()


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
