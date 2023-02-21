# https://stackoverflow.com/questions/56344997/what-is-a-python-mapping
from collections.abc import Mapping
import copy
from typing import List
from com.log import auto_logger
from com.file import YamlReader
from com.error import AutoTestException
import re
from jsonpath import jsonpath
from com.db import BaseDatabase
from com.xw_oss import XwOss


def get_json_path_and_key(s: str):
    """获取替换关键字和json_path
    """
    # TODO 兼容数组缺省.的写法
    pattern = r'{.+?}\.'
    try:
        key, path = s[s.index('{')+1:s.index('}')], ''
        start, end = re.search(pattern, s, flags=0).span()
        key, path = s[start+1:end-2], '$'+s[end-1:]
        return key, path
    except ValueError:
        return '', ''
    except AttributeError as e:
        return key, path


def get_json_path_and_key_v2(s: str) -> List[List[str]]:
    """获取参数化数据
    Returns:
        list: _description_
    """
    l = []
    raw_re = r'{[_A-Za-z0-9\u4e00-\u9fa5]+?}'
    keys = re.compile(raw_re).findall(s)
    after_key_index = 0
    for _, key in enumerate(keys):
        after_key_index = s.index(key, after_key_index)+len(key)
        if after_key_index == len(s) or '.' != s[after_key_index]:
            path = ''
        else:
            path = s[after_key_index:].split(' ')[0]
            auto_logger.debug(s.find(path), len(path))
            path = '$'+path
        # print(s[s.index(key, after_key_index-len(key))-1],
        #       s.index(key, after_key_index-len(key))-1)
        if '$' == s[s.index(key, after_key_index-len(key))-1]:
            value_type = 'raw'
        else:
            value_type ='str'
        l.append([
            key.replace('{', '').replace('}', ''),
            path,
            value_type
        ])
    return l

def get_value_by_jsonpath(obj, path):
    """用jsonpath转实际值。"""
    result = jsonpath(obj, path)
    if not result:
        return result
    elif 1 == len(result):
        return result[0]
    return result


class ValueMixin(Mapping):
    # 字典化能力

    _value = {}

    def __init__(self, value: dict):
        if not isinstance(value, dict):
            raise ValueError('value类型错误, 初始化化失败')
        self._value = value

    def __len__(self):
        return len(self._value)

    def __getitem__(self, k):
        return self._value[k]

    def __setitem__(self, k, value):
        self._value[k] = value

    def __iter__(self):
        return iter(list(self._value.keys()))

    def __repr__(self):
        return str(self._value)

    def update(self, other_value: dict):
        try:
            self._value.update(other_value)
        except Exception as e:
            auto_logger.error('{} {}'.format(type(e), e))
            raise AutoTestException('Value更新失败')

    def get(self, key, default=None):
        return self._value.get(key, default)

    def keys(self):
        return self._value.keys()

    def pop(self, k, value):
        return self._value.pop(k, value)


class ValueTemplate(ValueMixin):
    # 变量通用能力

    def get_db(self, db_link_name) -> BaseDatabase:
        return self._value['_db'][db_link_name]

    def set_db(self, value):
        self._value['_db'] = value

    def get_oss(self, oss_name) -> XwOss:
        return self._value['_oss'][oss_name]

    def set_oss(self, value):
        self._value['_oss'] = value

    def copy(self):
        # 网络类型的对象深拷贝会报错
        db_conf = self.pop('_db', None)
        oss_conf = self.pop('_oss', None)
        copy_value = copy.deepcopy(self)
        if db_conf:
            copy_value.set_db(db_conf)
            self.set_db(db_conf)
        if oss_conf:
            copy_value.set_oss(oss_conf)
            self.set_oss(oss_conf)
        return copy_value

    def show(self):
        return self._value

    def __bool__(self):
        return bool(self._value)


class Value(YamlReader, ValueTemplate):

    _template = {}

    def __init__(self, file_path):
        result = self.load_yaml_file(file_path)
        self.data_check(result, self._template, '文件%s格式错误' % file_path)
        self._value = result

    def data_check(self, value, template, msg=''):
        return super().data_check(value, template, msg=msg)
