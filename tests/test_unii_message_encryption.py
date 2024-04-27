# pylint: disable=protected-access
# pylint: disable=R0801
"""
Test UNii message encryption.
"""

import logging
import unittest

from unii.unii_command import UNiiCommand
from unii.unii_message import UNiiRequestMessage, UNiiResponseMessage

_LOGGER = logging.getLogger(__name__)


class Test(unittest.TestCase):
    """
    Test UNii message encryption correctness.
    """

    def test_message_encryption(self):
        # pylint: disable=line-too-long
        """
        Creates an encrypted connection request message and validates it's correctness
        """
        message = UNiiRequestMessage()
        message.session_id = 0xFFFF
        message.tx_sequence = 0x84AC0B7A
        message.rx_sequence = 0x00000000
        message.command = UNiiCommand.CONNECTION_REQUEST
        self.assertEqual(
            message.to_bytes(bytes.fromhex("31323334353637383930616263646566")).hex(),
            "ffff84ac0b7a000000000501002093458e6de62e1d5ea0e5281d5261f1845303",
        )

    def test_message_decryption(self):
        # pylint: disable=line-too-long
        """
        Creates an encrypted connection request message and validates it's correctness
        """
        message = UNiiResponseMessage(
            bytes.fromhex(
                "ffff84ac0b7a000000000501002093458e6de62e1d5ea0e5281d5261f1845303"
            ),
            bytes.fromhex("31323334353637383930616263646566"),
        )
        self.assertEqual(message.session_id, 0xFFFF)
        self.assertEqual(message.tx_sequence, 0x84AC0B7A)
        self.assertEqual(message.rx_sequence, 0x00000000)
        self.assertEqual(message.command, UNiiCommand.CONNECTION_REQUEST)
        self.assertIsNone(message.data)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
