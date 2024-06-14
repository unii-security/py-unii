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
        self.assertEqual(message.data.device_number, 5016)
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
        self.assertEqual(message.data.device_number, 5016)
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
        self.assertEqual(message.data.device_number, 5016)
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
        self.assertEqual(message.data.device_number, 5016)
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
        self.assertEqual(message.data.device_number, 5000)
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

    def test_response_request_input_arrangement(self):
        """
        Test special characters in input name.
        """
        # pylint: disable=line-too-long
        message = UNiiResponseMessage(
            bytes.fromhex(
                "3fe151586c9f00007b21050202085a28f03ab0176ace4a6ad46d78ffdfbe3fbb787deb4900641c76fdac26b8dc05f8caadd668b29039a76e284e87d949ce0fa53e899b06ad0aaf66605129521d82c141c67091fb0f48c3cadebc960313ece81fef4772c810d42f7f6d092ffcf04f842ce01f7acb1f3fa529eafc1ec2e1f6502667ea35396df1bfdda867fabe17f6c46cc120e251112c50cbefb33ecd1aa64923116b4eedda480f2120ea8c65d98b68131694c1dffd0060b9ab7845036352a184ec617aa35036e3ef4d0fef1db6710e8322b00b1a90fc576b4c904ac1b9e4e5821df26ab6e6b5c879047a24eeaf12a77acedceaa7d27531572d4fa7d81363795610df521ec62082f78fb77f453978e08d4ee85a9d1528fd79960a600e869f2c041474fdb77ec05dbd207ad73782df904c6c52a03101dbf22117d283936f07dc806090c5e7a1b9e64850a663a5a0585a473ccda610bd09b3dcc5727de5c708cc8166a0b39c89dd578ed88a3393c516bf9ff12c7c8fedab05ce47584dee193e15cb7bac2b31ed7e9c2b9e24cb11c3613b82a191ebf8666c15fd9e947612cc7e09e1abedeaa7fa8b7e56412798c97c3266b2cdebf9808fe65fe58abeca61479cf6bc62ac76e54dee5a9773d128798960352b5cc5fd7dbed0502a852f7576dc6172dcb54a2cb40a65b28c79fbb5c81a255c32f5305e3934b9925a99a584b087bd0c3d60e51eee79541695"
            ),
            bytes.fromhex("30313233343536373839616263646566"),
        )
        _LOGGER.debug(message)
        self.assertEqual(message.session_id, 0x3FE1)
        self.assertEqual(message.tx_sequence, 0x51586C9F)
        self.assertEqual(message.rx_sequence, 0x00007B21)
        self.assertEqual(
            message.command, UNiiCommand.RESPONSE_REQUEST_INPUT_ARRANGEMENT
        )
        self.assertIsNotNone(message.data)
        self.assertEqual(message.data[1].name, "Ingang 1 é ë ê 1ï  B")

    def test_response_request_output_arrangement(self):
        # pylint: disable=line-too-long
        message = UNiiResponseMessage(
            bytes.fromhex(
                "03a7155e79ad000093570502017d63849572e1395027d3310f4f6bdecb825097a6c2a28a03aad4a22985b0672d96513e390ab0c510e4875d00c875079f2a9d45cd6183f6ec632a57639336f7bfcb84074321c3cdff270347516063d03c6d4e8ae2e548e31d5726cc44d3361dea3075ec2ce2b826a8083778e1b95d244e7861b6f0abcbc24cdef47dc1f65a0f426fbf287090280eaf91ad21c54ebac2442b2827c805a37b3e4acd90431e4ab159be08ae713b873fe7c0c83b5c795f08543ee7d9439e3b7bebe9e66f0b3fea9aa9e0ac023e1da64c1a95a71ac93e82a4a78dc7b29f5325a3ccfc2f5420167ac4c4c0c344da7d05a202f921fb9491e155a822f891acb046eabb323459393e1e2b1746ca4bf1d9f93097d1560dd50eed4870d135f5e695e83b850a1e0cfe9685e90ace419a656668e07405a7e28d190014ade143328f8ad956f76a10bda1e078ec171f591bb102174f8945b62e0ba8beef85a8207bb5b1f9b6e486f5c1ecbbdf5686b34041b97e7a1a9afcab54cec4b9c9b6"
            ),
            bytes.fromhex("31323334353637383930616263646566"),
        )
        _LOGGER.debug(message)

    def test_response_request_section_status(self):
        # pylint: disable=line-too-long
        message = UNiiResponseMessage(
            bytes.fromhex("d3f5659325030000c8320502001af6c258882c6a41117f248f8f"),
            bytes.fromhex("31323334353637383930616263646566"),
        )
        _LOGGER.debug(message)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
