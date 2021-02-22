import unittest

from app.meta_wrapper import MetaWrapper
from app.output_type import OutputType


class TestMetaWrapper(unittest.TestCase):

    def test_get_description(self):
        filename = "9010576d-f3df-4011-aa41-adecd9bee011"
        expected = "023 survey response for period 0216 sample unit 12345"
        meta_data = MetaWrapper(filename)
        meta_data.output_type = OutputType.DAP
        meta_data.survey_id = "023"
        meta_data.period = "0216"
        meta_data.ru_ref = "12345"
        actual = meta_data.get_description()
        self.assertEqual(expected, actual)
