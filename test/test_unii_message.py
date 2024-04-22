# pylint: disable=R0801
"""
Test creating UNii messages.
"""

import logging
import unittest

from unii.sia_code import SIACode
from unii.unii_command import UNiiCommand
from unii.unii_message import UNiiChecksumError, UNiiRequestMessage, UNiiResponseMessage

_LOGGER = logging.getLogger(__name__)


class Test(unittest.TestCase):
    """
    Test UNii message.
    """

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

    def test_unencrypted_event_occurred(self):
        # pylint: disable=line-too-long
        message = UNiiResponseMessage(
            bytes.fromhex(
                "b11177c121e200007ca20402004501020031000381b17c030b021d1116436f6e66696775726174696520676577696a7a696764000000000000000000000000000020204a12"
            )
        )
        self.assertEqual(message.session_id, 0xB111)
        self.assertEqual(message.tx_sequence, 0x77C121E2)
        self.assertEqual(message.rx_sequence, 0x00007CA2)
        self.assertEqual(message.command, UNiiCommand.EVENT_OCCURRED)
        self.assertIsNotNone(message.data)
        self.assertEqual(message.data.event_description, "Configuratie gewijzigd")
        self.assertIsNone(message.data.sia_code)

    def test_encrypted_event_occurred_1(self):
        # pylint: disable=line-too-long
        message = UNiiResponseMessage(
            bytes.fromhex(
                "22f816f54ec00000d64405020043bff2b8de0eda43d9ce70ca2ee5db0e5822f33b013682af245fb4d693d4620906bb681a26cde01779ad351de49b7ee0afa0e91492e6"
            ),
            bytes.fromhex("31323334353637383930616263646566"),
        )
        _LOGGER.debug(message)
        self.assertEqual(message.session_id, 0x22F8)
        self.assertEqual(message.tx_sequence, 0x16F54EC0)
        self.assertEqual(message.rx_sequence, 0x0000D644)
        self.assertEqual(message.command, UNiiCommand.EVENT_OCCURRED)
        self.assertIsNotNone(message.data)
        self.assertEqual(message.data.event_description, "Brand Alarm")
        self.assertEqual(message.data.sia_code, SIACode.FIRE_ALARM)

    def test_encrypted_event_occurred_2(self):
        # pylint: disable=line-too-long
        message = UNiiResponseMessage(
            bytes.fromhex(
                "22f816f54ec00000d64405020043bff2b8de0eda43d9ce70ca2ee5db0e5822f33b013682af245fb4d693d4620906bb681a26cde01779ad351de49b7ee0afa0e91492e6"
            ),
            bytes.fromhex("31323334353637383930616263646566"),
        )
        _LOGGER.debug(message)
        self.assertEqual(message.session_id, 0x22F8)
        self.assertEqual(message.tx_sequence, 0x16F54EC0)
        self.assertEqual(message.rx_sequence, 0x0000D644)
        self.assertEqual(message.command, UNiiCommand.EVENT_OCCURRED)
        self.assertIsNotNone(message.data)
        self.assertEqual(message.data.event_description, "Brand Alarm")
        self.assertEqual(message.data.sia_code, SIACode.FIRE_ALARM)

    def test_encrypted_event_occurred_3(self):
        # pylint: disable=line-too-long
        message = UNiiResponseMessage(
            bytes.fromhex(
                "ed6c37c13cfb0000a9c905020055ed4b1fa1b14709845e8895825e64005d3cc502c5a54c7f16ae04e7525ca1c3e895ce2b8d5e1125d818cade5d5f778b0cd22c7476d510c3194644b76d79e6fd8d9be76a73302236"
            ),
            bytes.fromhex("31323334353637383930616263646566"),
        )
        _LOGGER.debug(message)
        self.assertEqual(message.session_id, 0xED6C)
        self.assertEqual(message.tx_sequence, 0x37C13CFB)
        self.assertEqual(message.rx_sequence, 0x0000A9C9)
        self.assertEqual(message.command, UNiiCommand.EVENT_OCCURRED)
        self.assertIsNotNone(message.data)
        self.assertEqual(message.data.event_description, "Sabotage schakelaar alarm")
        self.assertEqual(message.data.device_id, 5016)
        self.assertEqual(message.data.device_name, "UNii keypad 1")
        self.assertEqual(message.data.sia_code, SIACode.TAMPER)

    def test_encrypted_event_occurred_4(self):
        # pylint: disable=line-too-long
        message = UNiiResponseMessage(
            bytes.fromhex(
                "bdc57b6ed1f9000038740502005e023995b766cc5cbcaf338306bc9adeedba83f1e4f04d720941ad52ef4b45fda57abd2115bd09018bd78b637a9ac55d7a985b69ffecbc334dac4b0e317c0503a7abe2cd85b789c8d85b0806e33f169c7a"
            ),
            bytes.fromhex("31323334353637383930616263646566"),
        )
        _LOGGER.debug(message)
        self.assertEqual(message.session_id, 0xBDC5)
        self.assertEqual(message.tx_sequence, 0x7B6ED1F9)
        self.assertEqual(message.rx_sequence, 0x00003874)
        self.assertEqual(message.command, UNiiCommand.EVENT_OCCURRED)
        self.assertIsNotNone(message.data)
        self.assertEqual(message.data.event_description, "Sabotage schakelaar herstel")
        self.assertEqual(message.data.device_id, 5016)
        self.assertEqual(message.data.device_name, "UNii keypad 1")
        self.assertEqual(message.data.sia_code, SIACode.TAMPER_RESTORAL)

    def test_encrypted_event_occurred_5(self):
        # pylint: disable=line-too-long
        message = UNiiResponseMessage(
            bytes.fromhex(
                "ed6c37c13cfb0000a9ca0502004d9350e2cae2ee6eb18dd9ae3aca0f3f073189fb6c1c0df68b7aada71d33985b3cd788853a02e9248ab2b0cb25fc1c6a59e40a1f99e2390ef6ac2f3a5e792e5b"
            ),
            bytes.fromhex("31323334353637383930616263646566"),
        )
        _LOGGER.debug(message)
        self.assertEqual(message.session_id, 0xED6C)
        self.assertEqual(message.tx_sequence, 0x37C13CFB)
        self.assertEqual(message.rx_sequence, 0x0000A9CA)
        self.assertEqual(message.command, UNiiCommand.EVENT_OCCURRED)
        self.assertIsNotNone(message.data)
        self.assertEqual(message.data.event_description, "Communicatie fout")
        self.assertEqual(message.data.device_id, 5016)
        self.assertEqual(message.data.device_name, "UNii keypad 1")
        self.assertEqual(message.data.sia_code, SIACode.TAMPER)

    def test_encrypted_event_occurred_6(self):
        # pylint: disable=line-too-long
        message = UNiiResponseMessage(
            bytes.fromhex(
                "bdc57b6ed1f900003873050200575df1479ce5177f839875bacdee013675d70e1a9ddc9b116e81d3f0986fdfbd8feb3b98fd198df3fb9b013d2a69295dbba95d2eaaa2c80dc07e776e6be73abd28c0ac765be39b498ffd"
            ),
            bytes.fromhex("31323334353637383930616263646566"),
        )
        _LOGGER.debug(message)
        self.assertEqual(message.session_id, 0xBDC5)
        self.assertEqual(message.tx_sequence, 0x7B6ED1F9)
        self.assertEqual(message.rx_sequence, 0x00003873)
        self.assertEqual(message.command, UNiiCommand.EVENT_OCCURRED)
        self.assertIsNotNone(message.data)
        self.assertEqual(message.data.event_description, "Communicatie herstel")
        self.assertEqual(message.data.device_id, 5016)
        self.assertEqual(message.data.device_name, "UNii keypad 1")
        self.assertEqual(message.data.sia_code, SIACode.TAMPER_RESTORAL)

    def test_encrypted_event_occurred_7(self):
        # pylint: disable=line-too-long
        message = UNiiResponseMessage(
            bytes.fromhex(
                "bdc57b6ed1f90000386b05020057c70b74b84c85b840568667e0054f03feeda2eff0eff4f1a57f98b9c3957896c855a6ab068755f675dcf0079c4b68633819cc67223099a1b54e652e7d5a7d1fa93a5628520d2dc54e0d"
            ),
            bytes.fromhex("31323334353637383930616263646566"),
        )
        _LOGGER.debug(message)
        self.assertEqual(message.session_id, 0xBDC5)
        self.assertEqual(message.tx_sequence, 0x7B6ED1F9)
        self.assertEqual(message.rx_sequence, 0x0000386B)
        self.assertEqual(message.command, UNiiCommand.EVENT_OCCURRED)
        self.assertIsNotNone(message.data)
        self.assertEqual(message.data.event_description, "Config gewijzigd op afstand")
        self.assertEqual(message.data.device_id, 5000)
        self.assertEqual(message.data.device_name, "UNii centrale")
        self.assertEqual(message.data.sia_code, SIACode.REMOTE_PROGRAM_SUCCESS)

    def test_section_arrangement(self):
        # pylint: disable=line-too-long
        message = UNiiResponseMessage(
            bytes.fromhex(
                "a6947bb0970e0000c78e05020040308e8d444538679e74bfde534279bf107e1df375b473bb91c40cd5b99d9316491e5b4b43cb806c8520cdb12660359db150c2"
            ),
            bytes.fromhex("31323334353637383930616263646566"),
        )
        _LOGGER.debug(message)
        self.assertEqual(message.session_id, 0xA694)
        self.assertEqual(message.tx_sequence, 0x7BB0970E)
        self.assertEqual(message.rx_sequence, 0x0000C78E)
        self.assertEqual(
            message.command, UNiiCommand.RESPONSE_REQUEST_SECTION_ARRANGEMENT
        )
        self.assertIsNotNone(message.data)
        self.assertEqual(message.data[1].active, True)
        self.assertEqual(message.data[1].name, "Sectie 1")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
