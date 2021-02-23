import hashlib
import json
import unittest

from unittest import mock
from unittest.mock import patch
from app.meta_wrapper import MetaWrapper
from app.output_type import OutputType
from app.publish import get_formatted_current_utc, send_message, create_message_data
from app import CONFIG


class TestPublish(unittest.TestCase):

    def test_get_formatted_current_utc(self):
        with mock.patch('datetime.datetime') as date_mock:
            date_mock.utcnow.return_value = "2021-02-15T21:45:51.991Z"
            result = get_formatted_current_utc()
            return result

    @patch('app.publish.get_formatted_current_utc', return_value="2021-10-10T08:42:24.737Z")
    def test_create_message_data_dap(self, mock_time):
        filename = "9010576d-f3df-4011-aa41-adecd9bee011"
        meta_data = MetaWrapper(filename)
        meta_data.output_type = OutputType.DAP
        meta_data.survey_id = "023"
        meta_data.period = "0216"
        meta_data.ru_ref = "12345"
        data_bytes = b"bytes"
        meta_data.sizeBytes = len(data_bytes)
        meta_data.md5sum = hashlib.md5(b"bytes").hexdigest()
        actual = create_message_data(meta_data)
        expected = {
            'version': '1',
            'files': [{
                'name': filename,
                'sizeBytes': meta_data.sizeBytes,
                'md5sum': meta_data.md5sum
            }],
            'sensitivity': 'High',
            'sourceName': CONFIG.PROJECT_ID,
            'manifestCreated': mock_time.return_value,
            'description': "023 survey response for period 0216 sample unit 12345",
            'dataset': meta_data.survey_id,
            'schemaversion': '1',
            'iterationL1': meta_data.period
        }
        self.assertEqual(json.dumps(expected), actual)

    @patch('app.publish.create_message_data')
    @patch('app.publish.publish_data')
    def test_send_message_dap(self, mock_publish_data, mock_create_message_data):
        filename = "9010576d-f3df-4011-aa41-adecd9bee011"
        meta_data = MetaWrapper(filename)
        meta_data.survey_id = "134"
        meta_data.period = "201605"
        meta_data.ru_ref = "12346789012A"
        data_bytes = b"bytes"
        meta_data.sizeBytes = len(data_bytes)
        meta_data.md5sum = hashlib.md5(b"bytes").hexdigest()
        meta_data.output_type = OutputType.DAP
        message_data = {
            'version': '1',
            'files': [{
                'name': filename,
                'sizeBytes': meta_data.sizeBytes,
                'md5sum': meta_data.md5sum
            }],
            'sensitivity': 'High',
            'sourceName': CONFIG.PROJECT_ID,
            'manifestCreated': self.test_get_formatted_current_utc(),
            'description': "134 survey response for period 201605 sample unit 12346789012A",
            'dataset': meta_data.survey_id,
            'schemaversion': '1'
        }

        str_dap_message = json.dumps(message_data)
        meta_data = MetaWrapper(filename)
        meta_data.tx_id = "9010576d-f3df-4011-aa41-adecd9bee011"
        path = "dap/"
        mock_create_message_data.return_value = str_dap_message
        send_message(meta_data, path)
        mock_publish_data.assert_called_with(str_dap_message, filename, path)

    @patch('app.publish.create_message_data')
    @patch('app.publish.publish_data')
    def test_send_message_feedback(self, mock_publish_data, mock_create_message_data):
        filename = "9010576d-f3df-4011-aa41-adecd9bee001"
        meta_data = MetaWrapper(filename)
        data_bytes = b"bytes"
        meta_data.survey_id = "023"
        meta_data.period = "2016-02-01"
        meta_data.ru_ref = "432423423423"
        meta_data.sizeBytes = len(data_bytes)
        meta_data.md5sum = hashlib.md5(b"bytes").hexdigest()
        meta_data.output_type = OutputType.FEEDBACK
        message_data = {
            'version': '1',
            'files': [{
                'name': filename,
                'sizeBytes': meta_data.sizeBytes,
                'md5sum': meta_data.md5sum
            }],
            'sensitivity': 'High',
            'sourceName': CONFIG.PROJECT_ID,
            'manifestCreated': self.test_get_formatted_current_utc(),
            'description': "023 feedback response for period 2016-02-01 sample unit 432423423423",
            'dataset': meta_data.survey_id,
            'schemaversion': '1',
            'iterationL1': meta_data.period,
            'iterationL2': 'feedback'
        }

        str_dap_message = json.dumps(message_data)
        meta_data = MetaWrapper(filename)
        meta_data.tx_id = "9010576d-f3df-4011-aa41-adecd9bee001"
        path = "feedback/"
        mock_create_message_data.return_value = str_dap_message
        send_message(meta_data, path)
        mock_publish_data.assert_called_with(str_dap_message, filename, path)

    @patch('app.publish.create_message_data')
    @patch('app.publish.publish_data')
    def test_send_message_comment(self, mock_publish_data, mock_create_message_data):
        filename = "0f534ffc-9442-414c-b39f-a756b4adc6cb"
        meta_data = MetaWrapper(filename)
        meta_data.survey_id = "023"
        meta_data.period = "201605"
        meta_data.ru_ref = "12346789012A"
        data_bytes = b"bytes"
        meta_data.sizeBytes = len(data_bytes)
        meta_data.md5sum = hashlib.md5(b"bytes").hexdigest()
        meta_data.output_type = OutputType.COMMENTS
        message_data = {
            'version': '1',
            'files': [{
                'name': filename,
                'sizeBytes': meta_data.sizeBytes,
                'md5sum': meta_data.md5sum
            }],
            'sensitivity': 'High',
            'sourceName': CONFIG.PROJECT_ID,
            'manifestCreated': self.test_get_formatted_current_utc(),
            'description': "023 comment response for period 201605 sample unit 12346789012A",
            'dataset': "comments",
            'schemaversion': '1',
            'iterationL1': None,
        }

        str_dap_message = json.dumps(message_data)
        meta_data = MetaWrapper(filename)
        meta_data.tx_id = "0f534ffc-9442-414c-b39f-a756b4adc6cb"
        path = "comment/"
        mock_create_message_data.return_value = str_dap_message
        send_message(meta_data, path)
        mock_publish_data.assert_called_with(str_dap_message, filename, path)

    @patch('app.publish.create_message_data')
    @patch('app.publish.publish_data')
    def test_send_message_legacy(self, mock_publish_data, mock_create_message_data):
        filename = "9010576d-f3df-4011-aa41-adecd9bee011"
        meta_data = MetaWrapper(filename)
        meta_data.survey_id = "134"
        meta_data.period = "201605"
        meta_data.ru_ref = "12346789012A"
        data_bytes = b"bytes"
        meta_data.sizeBytes = len(data_bytes)
        meta_data.md5sum = hashlib.md5(b"bytes").hexdigest()
        meta_data.output_type = OutputType.LEGACY
        message_data = {
            'version': '1',
            'files': [{
                'name': filename,
                'sizeBytes': meta_data.sizeBytes,
                'md5sum': meta_data.md5sum
            }],
            'sensitivity': 'High',
            'sourceName': CONFIG.PROJECT_ID,
            'manifestCreated': self.test_get_formatted_current_utc(),
            'description': "134 survey response for period 201605 sample unit 12346789012A",
            'dataset': meta_data.survey_id,
            'schemaversion': '1'
        }

        str_dap_message = json.dumps(message_data)
        meta_data = MetaWrapper(filename)
        meta_data.tx_id = "9010576d-f3df-4011-aa41-adecd9bee011"
        path = "survey/"
        mock_create_message_data.return_value = str_dap_message
        send_message(meta_data, path)
        mock_publish_data.assert_called_with(str_dap_message, filename, path)

    @patch('app.publish.create_message_data')
    @patch('app.publish.publish_data')
    def test_send_message_seft(self, mock_publish_data, mock_create_message_data):
        filename = "0f534ffc-9442-414c-b39f-a756b4adc6cb"
        meta_data = MetaWrapper(filename)
        meta_data.survey_id = "134"
        meta_data.period = "201605"
        meta_data.ru_ref = "12346789012A"
        data_bytes = b"bytes"
        meta_data.sizeBytes = len(data_bytes)
        meta_data.md5sum = hashlib.md5(b"bytes").hexdigest()
        meta_data.output_type = OutputType.SEFT
        message_data = {
            'version': '1',
            'files': [{
                'name': filename,
                'sizeBytes': meta_data.sizeBytes,
                'md5sum': meta_data.md5sum
            }],
            'sensitivity': 'High',
            'sourceName': CONFIG.PROJECT_ID,
            'manifestCreated': self.test_get_formatted_current_utc(),
            'description': "134 seft response for period 201605 sample unit 12346789012A",
            'dataset': meta_data.survey_id,
            'schemaversion': '1'
        }

        str_dap_message = json.dumps(message_data)
        meta_data = MetaWrapper(filename)
        meta_data.tx_id = "0f534ffc-9442-414c-b39f-a756b4adc6cb"
        path = "seft/"
        mock_create_message_data.return_value = str_dap_message
        send_message(meta_data, path)
        mock_publish_data.assert_called_with(str_dap_message, filename, path)
