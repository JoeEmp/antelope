import logging
import unittest
from com.value import get_json_path_and_key_v2
import allure

@allure.story('pass')
class TestJsonPath(unittest.TestCase):

    def template(self, s, items):
        try:
            key_path_items = get_json_path_and_key_v2(s)
        except Exception as e:
            logging.exception(e)
        for index, item in enumerate(items):
            target_key, target_path,  target_value_type = item
            key, path, value_type = key_path_items[index]
            with allure.step('index %d: key %s == target_key %s' % (index, key, target_key)):
                self.assertEqual(key, target_key)
            with allure.step('index %d: path %s == target_path %s' % (index, path, target_path)):
                self.assertEqual(path, target_path)
            with allure.step('index %d: value_type %s == target_value_type %s' % (index, value_type, target_value_type)):
                self.assertEqual(value_type, target_value_type)

    @allure.title('无参数')
    def test_without_any(self):
        s = "select"
        self.template(s, [])

    @allure.title('原数据类型')
    def test_rt_smoke(self):
        s = "${resp}"
        self.template(s, [('resp', '', 'raw')])

    @allure.title('字符串中原数据类型')
    def test_rt_without_path(self):
        s = "select ${resp}"
        self.template(s, [('resp', '', 'raw')])

    @allure.title('原数据类型带jsonpath')
    def test_rt_smoke(self):
        s = "${resp}.0.device"
        self.template(s, [('resp', '$.0.device', 'raw')])

    @allure.title('字符串中原数据类型带jsonpath')
    def test_rt_in_str(self):
        s = "select ${resp}.0.device"
        self.template(s, [('resp', '$.0.device', 'raw')])

    @allure.title('字符串中原数据类型带jsonpath,末尾带空格')
    def test_rt_in_str2(self):
        s = "select ${resp}.0.device "
        self.template(s, [('resp', '$.0.device', 'raw')])

    @allure.title('原始数据类型和字符串类型混合显示')
    def test_rt_in_str3(self):
        s = "select ${resp}.0.device ${resp}.0.store {resp}.0.id"
        self.template(s, [
            ('resp', '$.0.device', 'raw'),
            ('resp', '$.0.store', 'raw'),
            ('resp', '$.0.id', 'str'),
        ])

    def test_smoke(self):
        s = "{resp}"
        self.template(s, [['resp', '', 'str']])

    def test_with_path(self):
        s = "{resp}.0.device"
        self.template(s, [['resp', '$.0.device', 'str']])

    def test_in_str(self):
        s = "select {resp}.0.device"
        self.template(s, [['resp', '$.0.device', 'str']])

    def test_without_path(self):
        s = "select {resp}"
        self.template(s, [['resp', '', 'str']])

    @allure.title('原始数据类型和字符串类型混合显示2')
    def test_rt_in_str4(self):
        s = "select ${resp}.0.device ${resp}.0.store {resp}.0.id  ${resp}.0.id"
        self.template(s, [
            ('resp', '$.0.device', 'raw'),
            ('resp', '$.0.store', 'raw'),
            ('resp', '$.0.id', 'str'),
            ('resp', '$.0.id', 'raw'),
        ])

    @allure.title('原始数据类型和字符串类型混合显示3')
    def test_rt_in_str5(self):
        s = "{resp}.0.name select ${resp}.0.device ${resp}.0.store {resp}.0.id  ${resp}.0.id"
        self.template(s, [
            ('resp', '$.0.name', 'str'),
            ('resp', '$.0.device', 'raw'),
            ('resp', '$.0.store', 'raw'),
            ('resp', '$.0.id', 'str'),
            ('resp', '$.0.id', 'raw'),
        ])