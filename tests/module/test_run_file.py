import unittest
import allure


@allure.story('pass')
class TestRunFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @unittest.skipIf(False, '未完成')
    def test_not_exist_file(self):
        """运行不存在的文件，提示文件/文件夹不存在
        """
    @unittest.skipIf(False, '未完成')
    def test_not_exist_dir(self):
        """运行不存在的文件，提示文件/文件夹不存在
        """
    @unittest.skipIf(False, '未完成')
    def test_empty_dir(self):
        """运行不存在的文件，提示文件夹下无测试用例
        """
    @unittest.skipIf(False, '未完成')
    def test_empty_dir(self):
        """运行不存在的文件，提示文件夹下无测试用例
        """
