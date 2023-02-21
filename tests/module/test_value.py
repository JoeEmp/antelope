import unittest
from com.value import get_json_path_and_key
import allure


@allure.story('pass')
class TestJsonPath(unittest.TestCase):

    def template(self, s, target_keys, target_paths):
        key, path = get_json_path_and_key(s)
        with allure.step('%s == %s' % (key, target_keys)):
            self.assertEqual(key, target_keys)
        with allure.step('%s == %s' % (path, target_paths)):
            self.assertEqual(path, target_paths)

    def test_smoke(self):
        s = "{resp}.0.device"
        self.template(s, 'resp', '$.0.device')

    def test_in_str(self):
        s = "select {resp}.0.device"
        self.template(s, 'resp', '$.0.device')

    def test_without_path(self):
        s = "select {resp}"
        self.template(s, 'resp', '')

    def test_without_any(self):
        s = "select"
        self.template(s, '', '')
