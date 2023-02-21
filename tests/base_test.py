import unittest
import os


class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_path = os.sep.join(__file__.split(os.sep)[:-1])

    def del_file(self, filename):
        os.system('rm -f %s' % filename)
        return filename
