# py文件的兼容测试
from unittest import TestCase
import allure

@allure.story('pass')
class A(TestCase):
    def test_1(self):
        self.assertEqual(1, 1)
