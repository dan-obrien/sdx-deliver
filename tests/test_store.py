import unittest

from app.output_type import OutputType
from app.store import write_to_bucket


class TestStore(unittest.TestCase):

    def test_write_to_bucket(self):
        output_type = OutputType.DAP
        filename = "9010576d-f3df-4011-aa42-adecd9bee011"
        path = write_to_bucket("This is tha data", filename, output_type)
        self.assertEqual(path, "dap/9010576d-f3df-4011-aa42-adecd9bee011")
