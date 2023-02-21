# 须修复历史数据

from typing import Any
from com.log import auto_logger
from abc import ABCMeta, abstractmethod
import jsonschema
import json
from com.log import auto_logger
from com.error import AssertException
from ast import literal_eval


class AssertStep(metaclass=ABCMeta):
    """各类断言步骤(基本可以照抄unittest)"""

    def __init__(self, paramers, *args, **kwargs):
        self.unzip_paramers(paramers)

    @abstractmethod
    def execute(self):
        pass

    def unzip_paramers(self, paramers):
        if isinstance(paramers, list):
            self.set_args(paramers)
        elif isinstance(paramers, dict):
            self.set_kwargs(paramers)

    def set_kwargs(self, paramers: dict):
        for k, v in paramers.items():
            setattr(self, k, v)

    @abstractmethod
    def set_args(self, args: list):
        pass

    @staticmethod
    def assertRegexpMatches(self, s, r):
        """断言s是否符合正则r"""

    @staticmethod
    def assertDictContainsSubset(self, a, b):
        """断言a字典是b字典的子集"""

    @classmethod
    def snippet(self):
        pass


class AssertEqualStep(AssertStep):
    """断言str(first)和str(second)相等"""

    def set_args(self, args):
        self.first, self.second, self.msg, *_ = args
        self.first, self.second = str(self.first), str(self.second)

    def execute(self):
        assert self.first == self.second, self.msg

    @classmethod
    def snippet(self):
        return """
        - assertEqual:
            first:
            second:
            msg:
        """, self. __doc__


class AssertNotEqualStep(AssertEqualStep):
    """断言str(first)和str(second)不相等"""

    def execute(self):
        assert self.first != self.second, self.msg

    @classmethod
    def snippet(self):
        return """
        - assertNotEqual:
            first:
            second:
            msg:
        """, self. __doc__


class AssertInStep(AssertStep):
    """断言member在container内"""

    def set_args(self, args):
        self.member, self.container, self.msg, *_ = args
        self.member, self.container = str(self.member), str(self.container)

    def execute(self):
        # fr=open("products.json",'r',encoding='utf-8')
        # content=fr.read()
        assert self.member in self.container, self.msg

    @classmethod
    def snippet(self):
        return """
        - assertIn:
            member:
            container:
            msg:
        """, self. __doc__


class AssertNotInStep(AssertInStep):
    """断言member不在container内"""

    def execute(self):
        assert self.member not in self.container, self.msg

    @classmethod
    def snippet(self):
        return """
        - assertNotIn:
            member:
            container:
            msg:
        """, self. __doc__


class AssertJsonInStep(AssertStep):
    """ 断言返回json的格式与jsonschema定义是否相符"""

    def set_args(self, args):
        """ 入参：
        response：接口返回数据, json字符串, 如：{response}.resp_data
        schema：返回数据的jsonschema模板的文件目录路径, 如：test_case/apaas/login/login_schema.json
        """
        self.response, self.schema, self.msg, *_ = args

    def execute(self):
        fr = open(self.schema, 'r', encoding='utf-8')
        content = fr.read()
#         content = {
#   "$schema": "http://json-schema.org/draft-07/schema#",
#   "type": "object",
#   "required": [],
#   "properties": {
#     "code": {
#       "type": "number"
#     },
#     "msg": {
#       "type": "string"
#     },
#     "data": {
#       "type": "array",
#       "items": {
#         "type": "string"
#       }
#     }
#   }
# }
#         auto_logger.info('ss value %s' % json.loads(self.response))
        try:
            # jsonschema.validate(instance = json.loads(self.response), schema = content)
            jsonschema.validate(instance=self.response, schema=json.loads(
                content.replace('\\', '\\\\'), strict=False))

        except Exception as err:
            self.msg = (self.msg or 'Json格式返回错误：') + '\n'
            # auto_logger.info('AssertJsonInStep(json格式断言) Error is %s' % str(err))
            raise AssertException(self.msg + str(err))


class AssertLen(AssertStep):
    def set_args(self, args: list):
        return super().set_args(args)

    def execute(self):
        if isinstance(self, str) and self.len.isdigit():
            self.len = int(self.len)


class AssertLenEqualStep(AssertLen):
    """变量长度判断等于指定长度。"""

    def execute(self):
        # TODO 优化
        assert self.len == len(eval(self.obj)), self.msg

    @classmethod
    def snippet(self):
        return """
        - assertLenEqual:
            len:
            obj:
            msg:
        """, self. __doc__


class AssertLenNotEqualStep(AssertLen):
    """变量长度判断不等于指定长度。"""

    def set_args(self, args: list):
        return super().set_args(args)

    def execute(self):
        # TODO 优化
        assert self.len != len(eval(self.obj)), self.msg

    @classmethod
    def snippet(self):
        return """
        - assertLenNotEqual:
            len:
            obj:
            msg:
        """, self. __doc__


class AssertLenNotLessThanStep(AssertLen):
    """变量长度判断小于指定长度。"""

    def set_args(self, args: list):
        return super().set_args(args)

    def execute(self):
        # TODO 优化
        assert len(eval(self.obj)) < int(self.len), self.msg


class AssertLenNotMoreThanStep(AssertLen):
    """变量长度判断大于指定长度。"""

    def set_args(self, args: list):
        return super().set_args(args)

    def execute(self):
        # TODO 优化
        assert int(self.len) < len(eval(self.obj)), self.msg


class AssertListEqualStep(AssertStep):
    """断言first和second列表相等
    - assertListEqual:
        - "{sql_select}"      # 预期结果
        - "{devices}"         # 实际结果
        - "{error_msg}"       # 错误信息
        - "{is_ignore_null}"  # 可选,默认不忽略null值的key
        - "{is_sort}"         # 可选,默认为不排序
    """

    def __init__(self, paramers, *args, **kwargs):
        self.is_sort = False
        self.is_ignore_null = False
        super().__init__(paramers, *args, **kwargs)

    def set_args(self, args):
        self.first, self.second, self.msg, *other_args = args
        if len(other_args) == 1 and other_args[0]:
            self.is_ignore_null = True
        else:
            self.is_ignore_none = False
        if len(other_args) == 2 and other_args[1]:
            self.is_sort = True
        else:
            self.is_sort = False
        try:
            if isinstance(self.first, str):
                self.first = literal_eval(self.first)
            if isinstance(self.second, str):
                self.second = literal_eval(self.second)
        except ValueError as e:
            raise AssertException('断言参数无法列表化,请使用另外的断言方式')

    def execute(self):
        first_len, second_len = len(self.first), len(self.second)
        assert first_len == second_len, '期望结果和实际结果,长度不同'
        if self.is_ignore_null:
            self.pop_none()
        auto_logger.debug('期望结果: %s\n实际结果: %s\n' % (self.first, self.second))
        if self.is_sort:
            self.first.sort(key=lambda x: str(x))
            self.second.sort(key=lambda x: str(x))
            try:
                for i in range(first_len):
                    assert self.first[i] == self.second[i], ''
            except AssertionError:
                assert self.first[i] == self.second[i], '期望结果和实际结果,第%d项不同\n%s\n%s' % (
                    i+1, self.first[i], self.second[i])
        else:
            try:
                assert self.first == self.second
            except AssertionError:
                auto_logger.error('期望结果 - 实际结果:\n%s' %
                                  [i for i in self.first if i not in self.second])
                auto_logger.error('实际结果 - 预期结果:\n%s' %
                                  [i for i in self.second if i not in self.first])
                assert self.first == self.second, '期望结果和实际结果不同，详情见日志的差集比较'

    def pop_none(self):
        self.first = [
            {key: val for key, val in item.items() if val != None} for item in self.first
        ]
        self.second = [
            {key: val for key, val in item.items() if val != None} for item in self.second
        ]

    @ classmethod
    def snippet(self):
        return """
        - assertListEqual:
            first:      # 预期结果
            second:     # 实际结果
            msg:        # 错误信息
            is_ignore_null: false  # 可选,默认不忽略null值的key
            is_sort: false         # 可选,默认不排序
        """, self.__doc__


class AssertJsonStep(AssertStep):
    """断言first和second列表相等
    - assertJson:
        - "{sql_select}"      # 预期结果
        - "{devices}"         # 实际结果
        - "{error_msg}"       # 错误信息
        - "{is_ignore_null}"  # 可选,默认不忽略null值的key 使用了item为json的步骤
    """

    def set_args(self, args):
        self.first, self.second, self.msg, *other_args = args
        try:
            self.first = self.first if isinstance(
                self.first, dict) else json.loads(self.first)
            self.second = self.second if isinstance(
                self.second, dict) else json.loads(self.second)
        except json.JSONDecodeError:
            raise AssertException('实际结果或者期望结果,不是json')

    def execute(self):
        assert self.first == self.second, self.msg

    @ classmethod
    def snippet(self):
        return """
        - assertJson:
            first:                 # 预期结果
            second:                # 实际结果
            msg:                   # 错误信息
            is_ignore_null: false  # 可选,默认不忽略null值的key
            is_sort: false         # 可选,默认不排序
        """, self.__doc__


class AssertItemInListStep(AssertStep):
    """断言member在container内"""

    def set_args(self, args):
        self.member, self.container, self.msg, *_ = args
        self.member, self.container = self.member, self.container

    def execute(self):
        assert self.member in self.container, self.msg

    @ classmethod
    def snippet(self):
        return """
        - assertItemInList:
            member:                 # 预期结果
            container:                # 实际结果
            msg:                   # 错误信息
        """, self.__doc__


class AssertItemNotInListStep(AssertItemInListStep):
    """断言member不在container内"""

    def execute(self):
        assert self.member not in self.container, self.msg

    @ classmethod
    def snippet(self):
        return """
        - assertItemNotInList:
            member:                 # 预期结果
            container:                # 实际结果
            msg:                   # 错误信息
        """, self.__doc__


class AssertValueType(AssertStep):
    """断言value的类型"""

    def __init__(self, paramers, *args, **kwargs):
        super().__init__(paramers, *args, **kwargs)
        self.type_map = {
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
        }

    def set_args(self, args):
        self.value, self.type, self.msg, *_ = args

    def execute(self):
        assert isinstance(self.value, self.type_map.get(
            self.type, Any)), self.msg

    @classmethod
    def snippet(self):
        return """
        - assertValueType:
            value:
            type: 
            msg: 类型错误
        """, self.__doc__
