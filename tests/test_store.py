import unittest

from unittest.mock import patch, MagicMock
from app.output_type import OutputType
from app.store import write_to_bucket


class TestStore(unittest.TestCase):

    @patch('app.store.CONFIG')
    def test_write_to_bucket(self, mock_config):
        mock_blob = MagicMock()
        mock_config.BUCKET.blob.return_value = mock_blob
        filename = "9010576d-f3df-4011-aa42-adecd9bee011"
        data = "my data"

        write_to_bucket(data, filename, OutputType.DAP)

        mock_config.BUCKET.blob.assert_called_with(f"dap/{filename}")
        mock_blob.upload_from_string.assert_called_with(data)
