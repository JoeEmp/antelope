from com.error import CaseTemplateException
from com.macro import *
from com.log import auto_logger, error_print
from modules.case_value import CaseValues, ItemValue
from modules.case_template import CaseTemplate
import os
from modules.global_value import GlobalValue



class Case():
    """ template文件和value文件组合成若干用例
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
        self.case_template_file_name = case_template_file_name
        self.case_perfix = case_template_file_name.replace(
            '_template.yaml', '')
        self.case_value_file_name = case_value_file_name or self.case_value_file_name.format(
            self.case_perfix)
        self.level = level
        global_value = global_value or GlobalValue('', env)
        auto_logger.debug('%s 模板生成用例变量' % case_template_file_name)
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
                    cases.append((case_template, case_value,
                             self.case_template_file_name))
                except CaseTemplateException as e:
                    error_print('%s 用例生成失败\n%s'%(self.case_template_file_name,e))
                    auto_logger.error('%s 用例生成失败\n%s'%(self.case_template_file_name,e))
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

    def get_cases(self):
        """list of (CaseTemplate,CaseValue,case_file_name)"""
        return self.cases

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.cases.pop(0)
        except IndexError:
            raise StopIteration
