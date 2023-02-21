# 全局变量的测试用例
from tests.base_test import BaseTestCase
from modules.global_value import *
from com.file import gen_yaml
import logging
from urllib.parse import quote
import allure


@allure.story('pass')
class TestGlobalValue(BaseTestCase):

    def setUp(self):
        if 'test_empty_env' == self._testMethodName:
            self.gen_without_test_env_file()
        elif 'test_gen_test_value' == self._testMethodName:
            self.gen_test_env_file()
        elif 'test_show_name' == self._testMethodName:
            self.gen_without_test_env_file()
        elif self._testMethodName in ['test_gen_db_value', 'test_gen_copy']:
            self.gen_test_db_file()
        elif 'test_db_without_type' == self._testMethodName:
            self.gen_test_db_file(without_type=True)
        elif 'test_db_unsupport_type' == self._testMethodName:
            self.gen_test_db_file(db_type='not_db_type')

    @allure.title('全局变量路径为空,只返回 _ 变量')
    def test_empty_file_path(self):
        self.assertDictEqual({"_db": {}, '_oss': {}},
                             GlobalValue('', 'test')._value)

    @allure.title('全局变量无指定的环境,只返回 _ 变量')
    def test_empty_env(self):
        self.assertDictEqual({"_db": {}, '_oss': {}}, GlobalValue(
            self.filename, 'test')._value)

    def test_gen_test_value(self):
        test_value = self.d.get(self.env)
        test_value.update({"_db": {}, "_oss": {}})
        self.assertDictEqual(test_value, GlobalValue(
            self.filename, 'test')._value)

    def test_gen_db_value(self):
        db_conf = self.d[self.env]['db']['mysql']
        db_conf['pwd'] = quote(db_conf['pwd'], 'utf-8')
        db_url = 'mysql+pymysql://{username}:{pwd}@{host}:{port}'.format(
            **db_conf)
        g = GlobalValue(self.filename, self.env)
        self.assertEqual(db_url, g.get_db('mysql').db_url)

    def test_gen_copy(self):
        g = GlobalValue(self.filename, self.env)
        self.assertNotEqual(id(g), id(g.copy()))
        self.assertEqual(g, g.copy())

    def test_update_by_dict(self):
        g = GlobalValue('', 'test')
        d1, d2 = {'name': 'joe'}, {'name': 'joe'}
        d3 = {"_db": {}, '_oss': {}}
        d3.update(d1)
        d2.update(g)
        self.assertDictEqual(d2, d3)

    def test_db_without_type(self):
        try:
            GlobalValue(self.filename, self.env)
        except GlobalValueException as e:
            self.assertIn('缺少数据库类型', e.reason)

    def test_db_unsupport_type(self):
        try:
            GlobalValue(self.filename, self.env)
        except AutoTestException as e:
            self.assertIn('没有具体的实现', e.reason)

    def test_show_name(self):
        self.assertIn(self.filename, str(GlobalValue(self.filename, '')))

    def tearDown(self):
        try:
            self.del_file(self.filename)
        except AttributeError as e:
            logging.info("%s without filename" % self._testMethodName)

    def gen_without_test_env_file(self):
        self.filename = 'without_test_env.yaml'
        d = {'show': {}}
        gen_yaml(self.filename, d)

    def gen_test_env_file(self):
        self.env = 'test'
        self.filename = 'test_env.yaml'
        self.d = {self.env: {'name': 'joe'}}
        gen_yaml(self.filename, self.d)

    def gen_test_db_file(self, db_type='', without_type=False):
        self.env = 'test'
        self.filename = 'test_env.yaml'
        self.d = {self.env: {'name': 'joe',
                             'db': {"mysql": {
                                 "host": "106.14.106.74",
                                 "port": 3306,
                                 "username": "xw_aiot",
                                 "pwd": "xuanwuAIOT2021!@#$",
                                 'type': 'mysql'
                             }}}}
        if db_type:
            self.d[self.env]['db']['mysql']['type'] = 'not_db'
        if without_type:
            self.d[self.env]['db']['mysql'].pop('type')
        gen_yaml(self.filename, self.d)
