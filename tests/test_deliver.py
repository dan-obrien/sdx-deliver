import unittest

from unittest.mock import patch
from app.deliver import deliver
from app.meta_wrapper import MetaWrapper


class TestDeliver(unittest.TestCase):

    @patch('app.deliver.encrypt_output')
    @patch('app.deliver.write_to_bucket')
    @patch('app.deliver.send_message')
    def test_deliver(self, mock_send_message, mock_write_to_bucket, mock_encrypt_output):
        encrypted_message = "This has been encrypted"
        path = "dap/"
        filename = "9010576d-f3df-4011-aa41-adecd9bee011"
        meta_data = MetaWrapper(filename)
        mock_encrypt_output.return_value = encrypted_message
        mock_write_to_bucket.return_value = path
        deliver(meta_data, b"bytes")
        mock_send_message.assert_called_with(meta_data, path)
