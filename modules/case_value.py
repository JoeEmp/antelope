
from json import JSONDecodeError
import os
from typing import Union
from com.error import AutoTestException, CaseValueException
from com.log import auto_logger
from com.file import YamlReader
from com.value import Value, ValueTemplate
from modules.global_value import GlobalValue
import copy
import json
from com.macro import *


class CaseValues(YamlReader):
    """初始化用例变量
    返回
    [
        {"k":1,"k1":2,""},
        {"k":1,"k1":3},
    ]
    """

    def __init__(self, filename, env, global_value):
        self._tmeplate = {'value': []}  # value里每一个item的格式交给 ItemValue处理
        self.case_values = []
        self._value = {}
        self.filename = filename
        # 文件转对象
        self._value = self.load_yaml_file(filename)
        self.data_check(self._value, self._tmeplate, '%s文件编写错误' % filename)
        # 用例变量
        # TODO 先获取value_block,global同理
        self.global_value_copy = self.gen_global_value_copy(env, global_value)
        self.value_block = self._value.get('value')
        # 根据用户配置生成的变量, 对应value的每一项。
        self.case_values = self.gen_case_values(
            self.value_block, self.global_value_copy)

    def gen_global_value_copy(self, env: str, global_value: GlobalValue) -> GlobalValue:
        """检查环境是否正确并使用全局变量初始化用例变量。"""
        case_env_value = self._value.get(env, {})
        if not isinstance(case_env_value, dict):
            raise CaseValueException("%s %s环境变量编写错误" % (self.filename, env))
        # 使用拷贝避免内存共用
        global_value_copy = global_value.copy()
        global_value_copy.update(case_env_value)
        return global_value_copy

    def gen_case_values(self, value_block: list, global_value_copy: GlobalValue) -> list:
        """生成具体的变量."""
        case_values = []
        for index, item_conf in enumerate(value_block):
            # 二次复制，使用拷贝避免内存共用
            case_value_copy = global_value_copy.copy()
            item_value = ItemValue(
                item_conf, case_value_copy, case_value_copy.env)
            case_values.append(item_value)
        return case_values

    def data_check(self, value, template, msg=''):
        return super().data_check(value, template, msg=msg)

    def __len__(self):
        return self.case_values

    def __next__(self):
        try:
            self.case_values.pop(0)
        except IndexError:
            raise StopIteration

    def __iter__(self):
        return iter(self.case_values)

    def __repr__(self):
        return str(self.case_values)

    def sort(self, key=None):
        if key:
            self.case_values.sort(key=key)
        else:
            self.case_values.sort()


class ItemValue(Value):
    """单个用例使用的参数和配置 """
    # 各个参数的格式
    _template = {'args': ''}
    _template_dict = {'args': {}}
    # 可选参数
    optional_keys = (
        # 用户写的关键字,存入关键字,默认值,值类型
        ('level', '_level', DEF_LEVEL, int),
        ('is_skip', '_is_skip', False, bool),
        ('remark', '_remark', '', str),
        ('module_path', '_module_path', '', str),
        ('skip_reason', '_skip_reason', '', str),
        ('title', '_title', '', str),
        ('exec_env', '_exec_env', '', str)
    )

    @classmethod
    def init_by_global_value(cls, global_value: GlobalValue):
        """用例无配置变量时, 使用全局变量初始化"""
        db_conf = global_value.pop('_db', None)
        oss_conf = global_value.pop('_oss', None)
        global_value_copy = copy.deepcopy(global_value._value)
        if db_conf:
            global_value_copy['_db'] = db_conf
            global_value._value['_db'] = db_conf
        if oss_conf:
            global_value_copy['_oss'] = oss_conf
            global_value._value['_oss'] = oss_conf
        args = {}
        for k in global_value:
            args[k] = '{%s}' % k
        args_str = json.dumps(args)
        return cls({'args': args_str}, global_value_copy, global_value.env)

    def __init__(self, item_conf: dict, item_value: Union[GlobalValue, dict], running_env: str) -> dict:
        item_conf = self.data_check(item_conf)
        self._value = self.gen_value(item_conf, item_value)
        self.running_env = running_env

    def gen_value(self, item_conf: dict, item_value: GlobalValue) -> dict:
        """将每一个args转化成既定的参数,供用例执行.


                    Args:
            item_conf (dict):  xx_value.yaml的value块的某一项
            item_value (GlobalValue): 用例/全局变量的copy

        Returns:
            dict: 具体的参数
        """
        # 处理value的args参数
        try:
            _value = self.replace(item_conf['args'], item_value)
        except KeyError as e:
            raise CaseValueException('用例变量缺少%s' % e)
        # 加入 _下划线参数
        for sep_key, value in item_value.items():
            if sep_key.startswith('_'):
                _value[sep_key] = value
        # 加入args外的可选关键字
        for key, save_key, def_value, optional_value_type in self.optional_keys:
            result = item_conf.get(key, def_value)
            if isinstance(result, optional_value_type):
                _value[save_key] = result
            else:
                raise ValueError('可选参数编写错误')
        return _value

    def replace(self, args: dict, tmp_value: dict) -> dict:
        for key, value in args.items():
            if isinstance(value, str) and 2 < len(value) and '{' == value[0] and '}' == value[-1]:
                args[key] = tmp_value[value[1:-1]]
            elif isinstance(value, dict):
                args[key] = self.replace(value, tmp_value)
        return args

    def data_check(self, value):
        try:
            super().data_check(value, self._template, msg='str类型的args解析错误, 请检查用例变量文件')
            value['args'] = json.loads(value['args'])
            return value
        except AutoTestException as e:
            auto_logger.debug(type(value))
            auto_logger.debug(value)
            super().data_check(value, self._template_dict,
                               msg='json类型的args解析错误或编写异常, 请查看用例变量文件')
            return value
        except JSONDecodeError as e:
            raise CaseValueException('args字符串不是json字符串,请检查用例变量文件')


class CaseValuesV2(Value):
    """ Mapping {case_perfix}_value.yaml file
    """

    def __init__(self, env, global_value: GlobalValue, file_path):
        if os.path.exists(file_path):
            super().__init__(file_path)
        else:
            auto_logger.warning(f'未找到{file_path}文件,用例变量为空')
            self._value = {}
        self._value = self._value.get(env, {})
        if not self._value:
            auto_logger.warning(f'{file_path}用例变量配置文件在{env}环境下,无任何配置')
        for key, value in self._value.items():
            global_copy = global_value.copy()
            global_copy.update(value)
            self._value[key] = global_copy

    def __repr__(self):
        return f'{self._value}'
