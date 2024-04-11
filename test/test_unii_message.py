# pylint: disable=R0801
"""
Test creating UNii messages.
"""

import logging
import unittest

from unii.unii_command import UNiiCommand
from unii.unii_message import UNiiChecksumError, UNiiRequestMessage, UNiiResponseMessage

_LOGGER = logging.getLogger(__name__)


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
        message.session_id = 0xffff
        message.tx_sequence = 0x08be2c53
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
        self.assertEqual(message.session_id, 0xf109)
        self.assertEqual(message.tx_sequence, 0x441a3896)
        self.assertEqual(message.rx_sequence, 0x08be2c53)
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

    def test_unencrypted_event_occurred(self):
        message = UNiiResponseMessage(
            bytes.fromhex(
                "b11177c121e200007ca20402004501020031000381b17c030b021d1116436f6e66696775726174696520676577696a7a696764000000000000000000000000000020204a12"
            )
        )
        self.assertEqual(message.session_id, 0xb111)
        self.assertEqual(message.tx_sequence, 0x77c121e2)
        self.assertEqual(message.rx_sequence, 0x00007ca2)
        self.assertEqual(message.command, UNiiCommand.EVENT_OCCURRED)
        self.assertIsNotNone(message.data)
        self.assertEqual(message.data.event_description, "Configuratie gewijzigd")
        self.assertEqual(message.data.sia_code, "  ")

    def test_encrypted_event_occurred_1(self):
        message = UNiiResponseMessage(
            bytes.fromhex(
                "22f816f54ec00000d64405020043bff2b8de0eda43d9ce70ca2ee5db0e5822f33b013682af245fb4d693d4620906bb681a26cde01779ad351de49b7ee0afa0e91492e6"
            ),
            b"1234567890abcdef"
        )
        _LOGGER.debug(message)
        self.assertEqual(message.session_id, 0x22f8)
        self.assertEqual(message.tx_sequence, 0x16f54ec0)
        self.assertEqual(message.rx_sequence, 0x0000d644)
        self.assertEqual(message.command, UNiiCommand.EVENT_OCCURRED)
        self.assertIsNotNone(message.data)
        self.assertEqual(message.data.event_description, "Brand Alarm")
        self.assertEqual(message.data.sia_code, "FA")

    def test_encrypted_event_occurred_2(self):
        message = UNiiResponseMessage(
            bytes.fromhex(
                "22f816f54ec00000d64405020043bff2b8de0eda43d9ce70ca2ee5db0e5822f33b013682af245fb4d693d4620906bb681a26cde01779ad351de49b7ee0afa0e91492e6"
            ),
            b"1234567890abcdef"
        )
        _LOGGER.debug(message)
        self.assertEqual(message.session_id, 0x22f8)
        self.assertEqual(message.tx_sequence, 0x16f54ec0)
        self.assertEqual(message.rx_sequence, 0x0000d644)
        self.assertEqual(message.command, UNiiCommand.EVENT_OCCURRED)
        self.assertIsNotNone(message.data)
        self.assertEqual(message.data.event_description, "Brand Alarm")
        self.assertEqual(message.data.sia_code, "FA")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
