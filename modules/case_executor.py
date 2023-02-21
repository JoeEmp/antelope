from typing import List
from com.log import auto_logger
from modules.step import SqlExecStep, CaseStep, RequestStep, IfStep, ElifStep, BranchStep, OssStep, ElseStep
from com.value import get_value_by_jsonpath, get_json_path_and_key_v2
from com.error import CaseValueException
from modules.step import STEP_TYPE
from modules.case_value import ItemValue
import allure
from unittest.case import SkipTest


class CaseExecutor():
    """用例执行器
    参数化变量和执行步骤
    """

    def __init__(self, case: tuple, level: int):
        """初始化内容,优先级小于指定优先级的
        Args:
            case (tuple): (用例模板,用例变量,用例模板文件名)
            level (int): 优先级
        """
        self.case_template, self.case_value, self.case_file_name = case
        # 0为必然执行
        if 0 == self.case_value['_level']:
            pass
        elif level < self.case_value['_level']:
            self.case_template.steps = []
        auto_logger.debug('init case_value id is %s' %
                          id(self.case_value))

    def execute(self):
        """用例执行"""
        if self.case_value['_is_skip']:
            raise SkipTest(self.case_value.get('_skip_reason', ''))
        if self.case_value['_exec_env'] and self.case_value.running_env != self.case_value['_exec_env']:
            raise SkipTest(self.case_value.get('用例只在%s环境运行' %
                           self.case_value['_exec_env']))
        for step_class, step_args in self.case_template.steps:
            step_args = self.parametric(step_class, step_args)
            self.execute_step(step_class, step_args)

    # TODO 优化代码, 写的很烂
    def gen_step_args(self, args, case_value: ItemValue):
        """生成具体的步骤参数，供步骤执行"""
        # auto_logger.debug('gen step args\nargs: %s\ncase_value: %s' % (args, case_value))
        if isinstance(args, list):
            for index, arg in enumerate(args):
                if isinstance(arg, dict) or isinstance(arg, list):
                    args[index] = self.gen_step_args(arg, case_value)
                if isinstance(arg, str):
                    value_items = get_json_path_and_key_v2(arg)
                    args[index] = self.to_value(arg, value_items, case_value)
        if isinstance(args, dict):
            for k, arg in args.items():
                if isinstance(arg, dict) or isinstance(arg, list):
                    args[k] = self.gen_step_args(arg, case_value)
                if isinstance(arg, str):
                    value_items = get_json_path_and_key_v2(arg)
                    args[k] = self.to_value(arg, value_items, case_value)
        if isinstance(args, str):
            value_items = get_json_path_and_key_v2(args)
            auto_logger.debug('value item is %s' % value_items)
            args = self.to_value(args, value_items, case_value)
        return args

    def gen_step_str(self, step_class, step_args):
        step_args_str = str(step_args)
        step_args_str = step_args_str if len(
            step_args_str) < 200 else step_args_str[:200]
        action = str(STEP_TYPE(step_class)).split('.')[-1]
        return action, step_args_str

    # NOTE 可能会存在bug
    def to_value(self, s: str, value_items: List[List[str]], case_value):
        if 1 == len(value_items):
            value_key, value_path, value_type = value_items[0]
            if 'raw' == value_type and '${%s}%s' % (value_key, value_path.lstrip('$')) == s:
                if value_path:
                    s = get_value_by_jsonpath(case_value[value_key], value_path)
                else:
                    s = case_value[value_key]
                return s
        for value_item in value_items:
            value_key, value_path, value_type = value_item
            old_str = '{%s}%s' % (value_key, value_path.lstrip(
                '$')) if 'str' == value_type else '${%s}%s' % (value_key, value_path.lstrip('$'))
            new_str = str(get_value_by_jsonpath(
                case_value[value_key], value_path)) if value_path else str(case_value[value_key])
            s = s.replace(old_str, new_str, 1)
        return s

    def parametric(self, step_class, step_args):
        """参数化用例变量."""
        try:
            # request步骤从用例模板取
            if issubclass(step_class, RequestStep):
                step_args = self.case_template.request_block
            # if 和 elif 只做judge的参数化
            if issubclass(step_class, (IfStep, ElifStep)):
                step_args[0] = self.gen_step_args(
                    step_args[0], self.case_value)
                auto_logger.debug(step_args[0])
            elif issubclass(step_class, ElseStep):
                pass
            else:
                step_args = self.gen_step_args(step_args, self.case_value)
        except KeyError as e:
            raise CaseValueException("用例模板%s缺少变量%s" %
                                     (self.case_file_name, str(e)))
        return step_args

    def execute_step(self, step_class, step_args):
        """步骤执行."""
        step_action, step_args_str = self.gen_step_str(
            step_class, step_args)
        auto_logger.debug('%s exec %s' % (step_action, step_args_str))
        with allure.step('%s exec %s' % (step_action, step_args_str)):
            # sql、oss步骤
            if issubclass(step_class, (SqlExecStep, OssStep)):
                # 用例变量获取数据库链接
                connects = self.case_value
                step_class(connects, step_args, self.case_value,
                           self.case_template.filename).execute()
            # 用例步骤
            elif issubclass(step_class, CaseStep):
                step_class(step_args, self.case_value).execute(
                    CaseExecutor)
            # 分支步骤
            elif BranchStep.__name__ in step_class.__base__.__name__:
                step_class(step_args, self.case_value,
                           self.case_template.filename).execute(CaseExecutor)
            # 其他步骤
            else:
                step_class(step_args, self.case_value,
                           self.case_template.filename).execute()

    def __repr__(self):
        return "%s,%s" % (self.case_template, self.case_value)
