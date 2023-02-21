from com.file import load_json
import unittest
import allure

@allure.story('pass')
class TestFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = {'a': "中文"}
        cls.uft8_json = 'utf8.json'
        cls.gbk_json = 'gbk.json'

    @unittest.skip('未完成')
    def test_utf8_json(self):
        assert load_json(self.uft8_json) == self.context

    @unittest.skip('未完成')
    def test_gbk_json(self):
        gbk_dict = load_json(self.gbk_json)
        assert gbk_dict == self.context
