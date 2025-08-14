import os
import unittest
from sf2utils.sf2parse import Sf2File


class TestSf2File(unittest.TestCase):
    @classmethod
    def open_file(cls, filename):
        return open(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename), 'rb')

    def test_basic_parse(self):
        """make sure that parsing a simple file loads the right amount of instruments, samples and presets"""
        with self.open_file('sf2utils_test.sf2') as file:
            sf2_file = Sf2File(file)
            self.assertEqual(len(sf2_file.instruments), 3)
            self.assertEqual(len(sf2_file.samples), 3)
            self.assertEqual(len(sf2_file.presets), 2)

            self.assertEqual(sf2_file.instruments[0].name, 'inst1')
            self.assertEqual(sf2_file.instruments[1].name, 'inst2')

            self.assertEqual(sf2_file.presets[0].bank, 13)
            self.assertEqual(sf2_file.presets[0].preset, 37)


if __name__ == '__main__':
    unittest.main()
