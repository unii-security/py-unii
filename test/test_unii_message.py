# pylint: disable=R0801
"""
Test creating UNii messages.
"""

# import logging
import unittest

from unii.unii_command import UNiiCommand
from unii.unii_message import UNiiChecksumError, UNiiRequestMessage, UNiiResponseMessage


class Test(unittest.TestCase):
    """
    Test UNii message.
    """

    # def setUp(self):
    #     logging.basicConfig(
    #         format="%(asctime)s %(levelname)-8s %(message)s", level=logging.DEBUG
    #     )

    def test_unencrypted_connection_request(self):
        """
        Creates an unencrypted connection request message and validates it's correctness.
        """
        message = UNiiRequestMessage()
        message.session_id = 0xFFFF
        message.tx_sequence = 0x08BE2C53
        message.rx_sequence = 0x00000000
        message.command = UNiiCommand.CONNECTION_REQUEST
        self.assertEqual(
            message.to_bytes().hex(),
            "ffff08be2c530000000004010020000100000000000000000000000000005ed3",
        )

    def test_unencrypted_connection_response(self):
        """
        Creates an unencrypted connection response message and validates it's correctness.
        """
        message = UNiiResponseMessage(
            bytes.fromhex("f109441a389608be2c530402001400020000853e")
        )
        self.assertEqual(message.session_id, 0xF109)
        self.assertEqual(message.tx_sequence, 0x441A3896)
        self.assertEqual(message.rx_sequence, 0x08BE2C53)
        self.assertEqual(message.command, UNiiCommand.CONNECTION_REQUEST_RESPONSE)
        self.assertIsNone(message.data)

    def test_unencrypted_connection_response_wrong_checksum(self):
        """
        Creates an unencrypted connection response message with an invallid checksum.

        Should throw an UNiiChecksumError
        """
        self.assertRaises(
            UNiiChecksumError,
            UNiiResponseMessage,
            bytes.fromhex("f109441a389608be2c530402001400020000853d"),
        )


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
