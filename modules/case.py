from abc import ABCMeta, abstractmethod
import copy
from com.error import CaseTemplateException, CaseValueException
from com.file import YamlReader
from com.macro import *
from com.log import auto_logger, error_print
from com.macro import DEF_LEVEL
from modules.case_value import CaseValues, CaseValuesV2, ItemValue
from modules.case_template import CaseTemplate, CaseTemplateV2
import os
from modules.global_value import GlobalValue


def get_template_version(case_template_file_name):
    return YamlReader.load_yaml_file(case_template_file_name).get('_version', 1.0)


def get_all_case(case_template_file_name, env, global_value, level) -> list:
    auto_logger.info(f'加载用例{case_template_file_name}')
    version = get_template_version(case_template_file_name)
    if 1 == version:
        return Case(case_template_file_name, env, global_value=global_value, level=level)
    elif 2 == version:
        try:
            return CaseV2(case_template_file_name, env, global_value=global_value, level=level)
        except CaseTemplateException as e:
            auto_logger.error(e)
            error_print(e.reason)
            return []


class CaseInterFace(metaclass=ABCMeta):
    """用例生成接口类
    """
    # 用例模板文件名格式
    template_file_name = "{}_template.yaml"
    # 用例变量文件名格式
    case_value_file_name = '{}_value.yaml'
    # 接口返回基本校验文件
    schema_file_name = "{}_schema.json"
    # 用户期望响应
    check_file_name = "{}_check.json"

    def __init__(self, case_template_file_name: str, env: str, level=DEF_LEVEL, has_case_value=True, global_value=None, case_value_file_name='', case_values=None):
        """用例和变量的初始化

        Args:
            env (str): 命令行指定环境
            level (int, optional): 用例等级. Defaults to DEF_LEVEL.
            has_case_value (bool, optional): 是否有用例变量文件. Defaults to True.
            global_value (GlobalValue, optional): 全局变量. Defaults to None.
            case_value_file_name (str, optional): 用例变量文件名. Defaults to ''.
            case_values (CaseValues, optional): 用例变量，用于嵌套用例，使用父用例的用例变量初始化. Defaults to None.
        """
        self._version = 1
        self.case_template_file_name = case_template_file_name
        self.case_perfix = case_template_file_name.replace(
            '_template.yaml', '')
        self.case_value_file_name = case_value_file_name or self.case_value_file_name.format(
            self.case_perfix)
        self.level = level
        global_value = global_value or GlobalValue('', env)
        auto_logger.debug('%s 模板生成用例变量' % case_template_file_name)

    def get_cases(self):
        """list of (CaseTemplate,CaseValue,case_file_name)"""
        return self.cases

    @abstractmethod
    def gen_sub_case(self) -> list:
        return []

    @abstractmethod
    def gen_case_values(self):
        pass

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.cases.pop(0)
        except IndexError:
            raise StopIteration


class Case(CaseInterFace):

    def __init__(self, case_template_file_name: str, env: str, level=DEF_LEVEL, has_case_value=True, global_value=None, case_value_file_name='', case_values=None):
        super().__init__(case_template_file_name, env, level, has_case_value,
                         global_value, case_value_file_name, case_values)
        self.case_values = case_values or self.gen_case_values(
            env, has_case_value, global_value)
        auto_logger.debug('case value %s' % self.case_values)
        self.cases = self.gen_sub_case()

    def gen_sub_case(self) -> list:
        """生成子用例。
        [
            (CaseTemplate() , ItemValue(), case_file_name)
            (CaseTemplate() , ItemValue(), case_file_name)
        ]
        """
        cases = []
        self.case_values.sort(key=lambda x: x['_level'])
        # 没有用例变量直接使用环境变量
        for case_value in self.case_values:
            # 优先级过滤
            if case_value['_level'] <= self.level:
                try:
                    case_template = CaseTemplate(self.case_template_file_name)
                    case_value['_is_skip'] |= case_template.is_skip
                    cases.append((self._version, case_template,
                                 case_value, self.case_template_file_name))
                except CaseTemplateException as e:
                    error_print('%s 用例生成失败\n%s' %
                                (self.case_template_file_name, e))
                    auto_logger.error('%s 用例生成失败\n%s' %
                                      (self.case_template_file_name, e))
        return cases

    def gen_case_values(self, env, has_case_value, global_value) -> list:
        """生成用例变量"""
        # 使用深拷贝避免内存共用
        global_value_copy = global_value.copy()
        if not has_case_value:
            return [ItemValue.init_by_global_value(global_value_copy)]
        if not os.path.exists(self.case_value_file_name):
            auto_logger.warning('%s未找到用例变量文件, 默认只使用全局变量' %
                                self.case_template_file_name)
            return [ItemValue.init_by_global_value(global_value_copy)]
        elif os.path.isfile(self.case_value_file_name):
            case_values = CaseValues(
                self.case_value_file_name, env, global_value_copy)
        return case_values


class CaseV2(CaseInterFace):
    """ template文件和value文件组合成若干用例"""

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

    def __init__(self, case_template_file_name: str, env: str, level=DEF_LEVEL, has_case_value=True, global_value=None, case_value_file_name='', case_values=None):
        super().__init__(case_template_file_name, env, level, has_case_value,
                         global_value, case_value_file_name, case_values)
        self.global_value = global_value
        self.case_values = case_values or CaseValuesV2(
            env, global_value, self.case_value_file_name)
        auto_logger.debug('case value %s' % self.case_values)
        self.cases = self.gen_sub_case()
        auto_logger.debug('v2 cases')
        auto_logger.debug(f'{self.cases}')
        

    def gen_sub_case(self, ignore_optional_keys=False) -> list:
        """生成子用例。
        [
            (CaseTemplate()[case1] , ItemValue(), case_file_name)
            (CaseTemplate()[case2] , ItemValue(), case_file_name)
        ]
        """
        cases = []
        template = CaseTemplateV2(self.case_template_file_name)
        for case_key in template.get_case_block_keys():
            template_copy = copy.deepcopy(template)
            case_block = template_copy.content[case_key]
            template_copy.case_block = case_block
            template_copy.test_step = template_copy.gen_steps_block(case_block['test_step'])
            if 'use_value' in case_block:
                case_value = ItemValue.init_by_global_value(self.case_values.get(case_block['use_value'], GlobalValue('', 'def')))
            else:
                case_value = ItemValue.init_by_global_value(self.global_value)
            if not ignore_optional_keys:
                case_value = self.update_optional_keys_by_case_template(case_value, case_block)
            template_is_skip = template.content.get('is_skip', False)
            case_value['_is_skip'] = template_is_skip or case_value['_is_skip']
            if case_value['_level'] <= self.level:
                cases.append((2, template_copy, case_value,
                             self.case_template_file_name))
            auto_logger.debug(
                f'\ncase content: {template_copy}\ncase value: {case_value}')
        return cases

    def update_optional_keys_by_case_template(self, case_value, case_block):
        # 加入args外的可选关键字
        for key, save_key, def_value, optional_value_type in self.optional_keys:
            result = case_block.get(key, def_value)
            if isinstance(result, optional_value_type):
                case_value[save_key] = result
            else:
                raise ValueError('可选参数编写错误')
        return case_value

    def gen_case_values(self, env, global_value) -> CaseValuesV2:
        return CaseValuesV2(self.case_value_file_name, env, global_value)
