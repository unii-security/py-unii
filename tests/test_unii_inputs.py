# pylint: disable=R0801
# pylint: disable=missing-function-docstring
"""
Test Input Status.
"""
import asyncio
import json
import logging
import unittest

from unii import UNiiInputState, UNiiLocal

_SETTINGS_JSON = "settings.json"

_LOGGER = logging.getLogger(__name__)


class Test(unittest.IsolatedAsyncioTestCase):
    """
    Test Input Status.
    """

    _unii = None

    async def asyncSetUp(self):
        with open(_SETTINGS_JSON, encoding="utf8") as settings_file:
            settings = json.load(settings_file)
            host = settings.get("host")
            port = settings.get("encrypted_port", 6502)
            shared_key = settings.get("shared_key", 6502)
            self.user_code = settings.get("user_code", "123456")

            self._unii = UNiiLocal(host, port, shared_key)
            await asyncio.sleep(1)
            result = await self._unii.connect()
            self.assertTrue(result, "Failed to connect to UNii")

    async def asyncTearDown(self):
        await asyncio.sleep(1)
        await self._unii.disconnect()

    async def test_inputs(self):
        """
        Test connecting to Alphatronics UNii.
        """
        self.assertIsNotNone(self._unii.inputs, "Input Status not set")
        for _, unii_input in self._unii.inputs.items():
            if unii_input.status != UNiiInputState.DISABLED:
                _LOGGER.info(unii_input)

    async def test_bypass_wired_input(self):
        await self._unii.unbypass_input(2, self.user_code)
        result = await self._unii.bypass_input(2, self.user_code)
        self.assertTrue(result, "Failed to bypass input")

    async def test_bypass_wired_input_fail(self):
        await self._unii.unbypass_input(2, self.user_code)
        result = await self._unii.bypass_input(2, "")
        self.assertFalse(result)

    async def test_unbypass_wired_input(self):
        await self._unii.bypass_input(2, self.user_code)
        result = await self._unii.unbypass_input(2, self.user_code)
        self.assertTrue(result, "Failed to bypass input")

    async def test_unbypass_wired_input_fail(self):
        await self._unii.bypass_input(2, self.user_code)
        result = await self._unii.unbypass_input(2, "")
        self.assertFalse(result)

    async def test_bypass_keypad_input(self):
        await self._unii.unbypass_input(701, self.user_code)
        result = await self._unii.bypass_input(701, self.user_code)
        self.assertTrue(result, "Failed to bypass input")

    async def test_bypass_keypad_input_fail(self):
        await self._unii.unbypass_input(701, self.user_code)
        result = await self._unii.bypass_input(701, "")
        self.assertFalse(result)
