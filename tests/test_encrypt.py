import unittest
from unittest.mock import patch, Mock, MagicMock

from app import gnupg, CONFIG
from app.encrypt import encrypt_output


class TestInit(unittest.TestCase):

    def setUp(self):
        with open('tests/test_key.txt', 'r') as file:
            test_key = file.read()
        gpg = gnupg.GPG()
        gpg.import_keys(test_key)
        CONFIG.ENCRYPTION_KEY = test_key
        CONFIG.GPG = gpg

    def test_encrypt(self):
        with self.assertLogs('app.encrypt', level='INFO') as actual:
            test_data = b'{data to be encrypted}'
            encrypt_output(test_data)
        self.assertEqual(actual.output[0], 'INFO:app.encrypt:{"event": "Successfully encrypted output", "level": '
                                           '"info", "logger": "app.encrypt"}')

    @patch('app.encrypt.CONFIG')
    def test_encrypt_bad(self, mock_encrypt):
        with self.assertLogs('app.encrypt', level='ERROR') as actual:
            mock_encrypted = MagicMock()
            mock_encrypted.ok = False
            mock_encrypt.GPG.encrypt.return_value = mock_encrypted
            test_data = b'{data to be encrypted}'
            encrypt_output(test_data)
        self.assertEqual(actual.output[0], 'ERROR:app.encrypt:{"event": "Failed to encrypt output", "level": '
                                           '"error", "logger": "app.encrypt"}')
