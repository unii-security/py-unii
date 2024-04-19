# pylint: disable=protected-access
# pylint: disable=R0801
"""
Tests automatic reconnect to Alphatronics UNii.
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
    Unit test for automatic reconnect to Alphatronics UNii.
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
            self._shared_key = settings.get("shared_key")

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
            self.assertTrue(unii.connection.is_open, "Connection is not open")
            while True:
                await asyncio.sleep(10)
                with self.subTest(msg="Connection open"):
                    self.assertTrue(unii.connection.is_open, "Connection is not open")
        finally:
            await unii.disconnect()


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
