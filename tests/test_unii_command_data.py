# pylint: disable=R0801
# pylint: disable=missing-function-docstring
"""
Test UNii Command Data helper functions.
"""

import logging
import unittest

from unii.unii_command_data import UNiiBypassMode, UNiiBypassUnbypassZoneInput

_LOGGER = logging.getLogger(__name__)


class Test(unittest.TestCase):
    """
    Test UNii Command Data helper function correctness.
    """

    def test_bypass_input(self):
        data = UNiiBypassUnbypassZoneInput(UNiiBypassMode.USER_CODE, "123456", 1)
        self.assertEqual(data.mode, 0)
        self.assertEqual(data.code, "12345600")
        self.assertEqual(data.number, 1)
        self.assertEqual(data.to_bytes(), bytes.fromhex("0012345600000000000001"))
