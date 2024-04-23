# pylint: disable=protected-access
"""
Test UNii message CRC-16 checksums.

Calculating the CRC-16 checksum for validation is done using:
https://crccalc.com/
"""

# import logging
import unittest

from unii.unii_message import _UNiiMessage


class Test(unittest.TestCase):
    """
    Test UNii message checksum correctness.
    """

    def test_checksum_1(self):
        """
        Tests the correct working of the checksum algorithm.
        """
        message = _UNiiMessage()

        crc = message._calculate_crc16(bytes.fromhex("0123456789abcdef"))
        self.assertEqual(crc, 0xA955)

    def test_checksum_2(self):
        """
        Tests the correct working of the checksum algorithm.
        """
        message = _UNiiMessage()

        crc = message._calculate_crc16(bytes.fromhex("0123456789"))
        self.assertEqual(crc, 0x6282)

    def test_checksum_3(self):
        """
        Tests the correct working of the checksum algorithm.
        """
        message = _UNiiMessage()

        crc = message._calculate_crc16(
            bytes.fromhex(
                "ffff08be2c53000000000401002000010000000000000000000000000000"
            )
        )
        self.assertEqual(crc, 0x5ED3)

    def test_checksum_4(self):
        """
        Tests the correct working of the checksum algorithm.
        """
        message = _UNiiMessage()

        crc = message._calculate_crc16(
            bytes.fromhex("f109441a389608be2c530402001400020000")
        )
        self.assertEqual(crc, 0x853E)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
