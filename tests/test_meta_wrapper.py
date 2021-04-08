import unittest

from app.meta_wrapper import MetaWrapper
from app.output_type import OutputType


class TestMetaWrapper(unittest.TestCase):

    test_seft = {
        'filename': '11110000014H_202009_057_20210121143526',
        'md5sum': '12345',
        'period': '202009',
        'ru_ref': '20210121143526',
        'sizeBytes': 42,
        'survey_id': '057',
        'tx_id': 'd8cfc292-90bc-4e2f-8cf9-3e5d5da5a1ff'
    }

    test_bytes = b'testing bytes'

    test_survey = {
            "collection": {
                "exercise_sid": "XxsteeWv",
                "instrument_id": "0167",
                "period": "2019"
            },
            "data": {
                "46": "123",
                "47": "456",
                "50": "789",
                "51": "111",
                "52": "222",
                "53": "333",
                "54": "444",
                "146": "different comment.",
                "d12": "Yes",
                "d40": "Yes"
            },
            "flushed": False,
            "metadata": {
                "ref_period_end_date": "2016-05-31",
                "ref_period_start_date": "2016-05-01",
                "ru_ref": "49900108249D",
                "user_id": "UNKNOWN"
            },
            "origin": "uk.gov.ons.edc.eq",
            "started_at": "2017-07-05T10:54:11.548611+00:00",
            "submitted_at": "2017-07-05T14:49:33.448608+00:00",
            "type": "uk.gov.ons.edc.eq:surveyresponse",
            "version": "0.0.1",
            "survey_id": "009",
            "tx_id": "c37a3efa-593c-4bab-b49c-bee0613c4fb2",
            "case_id": "4c0bc9ec-06d4-4f66-88b6-2e42b79f17b3"
        }

    def test_set_dap(self):
        filename = "c37a3efa-593c-4bab-b49c-bee0613c4fb2"
        expected = "009 survey response for period 2019 sample unit 49900108249D"
        meta_data = MetaWrapper(filename)
        meta_data.set_dap(self.test_survey, self.test_bytes)
        actual = meta_data.get_description()
        self.assertEqual(expected, actual)

    def test_set_legacy(self):
        filename = "c37a3efa-593c-4bab-b49c-bee0613c4fb2"
        expected = "009 survey response for period 2019 sample unit 49900108249D"
        meta_data = MetaWrapper(filename)
        meta_data.set_legacy(self.test_survey, self.test_bytes)
        actual = meta_data.get_description()
        self.assertEqual(expected, actual)

    def test_set_feedback(self):
        filename = "c37a3efa-593c-4bab-b49c-bee0613c4fb2"
        expected = "009 feedback response for period 2019 sample unit 49900108249D"
        meta_data = MetaWrapper(filename)
        meta_data.set_feedback(self.test_survey, self.test_bytes)
        actual = meta_data.get_description()
        self.assertEqual(expected, actual)

    def test_set_comments(self):
        filename = "c37a3efa-593c-4bab-b49c-bee0613c4fb2"
        expected = "Comments.zip"
        meta_data = MetaWrapper(filename)
        meta_data.set_comments(self.test_bytes)
        actual = meta_data.get_description()
        self.assertEqual(expected, actual)

    def test_set_seft(self):
        filename = "c37a3efa-593c-4bab-b49c-bee0613c4fb2"
        expected = "057 seft response for period 202009 sample unit 20210121143526"
        meta_data = MetaWrapper(filename)
        meta_data.set_seft(self.test_seft)
        actual = meta_data.get_description()
        self.assertEqual(expected, actual)



