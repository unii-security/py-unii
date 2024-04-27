# pylint: disable=R0801
"""
Test UNii Command Data helper functions.
"""

import logging
import unittest

from unii.unii_command_data import bcd_encode, bit_position_to_numeric

_LOGGER = logging.getLogger(__name__)


class Test(unittest.TestCase):
    """
    Test UNii Command Data helper function correctness.
    """

    def test_bit_position_to_numeric_1(self):
        result = bit_position_to_numeric(0b0000000000000001.to_bytes(2))
        self.assertListEqual(result, [1])

    def test_bit_position_to_numeric_2(self):
        result = bit_position_to_numeric(0b0000000000000010.to_bytes(2))
        self.assertListEqual(result, [2])

    def test_bit_position_to_numeric_3(self):
        result = bit_position_to_numeric(0b0000000000000011.to_bytes(2))
        self.assertListEqual(result, [1, 2])

    def test_bcd_encode(self):
        result = bcd_encode("00000000")
        self.assertEqual(result, 0x0000000000000000.to_bytes(8))

    def test_bcd_encode_12345678(self):
        result = bcd_encode("12345678")
        self.assertEqual(result, 0x1234567800000000.to_bytes(8))

    def test_bcd_encode_22170302(self):
        result = bcd_encode("22170302")
        self.assertEqual(result, 0x2217030200000000.to_bytes(8))
