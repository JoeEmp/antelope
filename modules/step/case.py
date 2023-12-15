from modules.step.step import Step
from com.error import AutoTestException
import os


class CaseStep(Step):
    "调用已存在用例,参数为路径"

    _template = ''
    # 用例模板文件名格式
    template_file_name = "{}_template.yaml"
    # 接口返回基本校验文件
    schema_file_name = "{}_schema.json"
    # 用户期望响应
    check_file_name = "{}_check.json"

    def __init__(self, case_file_name, case_value):
        self.case_file_name = case_file_name
        self.case_values = [case_value]
        self.level = case_value['_level']
        self.cases = self.gen_sub_case()

    def gen_sub_case(self) -> list:
        """生成子用例。
        [
            (case_template , case_value, case_file_name)
            (case_template , case_value, case_file_name)
        ]
        """
        from modules.case_template import CaseTemplate
        cases = []
        # 没有用例变量直接使用环境变量
        for case_value in self.case_values:
            cases.append((CaseTemplate(self.case_file_name),
                         case_value, self.case_file_name))
        return cases

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

    def data_check(self, value, template, msg=''):
        super().data_check(value, template, msg=msg)
        if not os.path.exist(value):
            raise AutoTestException('模板路径错误')

    def execute(self, executor):
        # 用例作为步骤等级和父用例等级一样
        executor(self.cases[0], self.level).execute()

    @classmethod
    def snippet(self):
        return """
        - case: 
        """, self.__doc__



class CaseStepV2(Step):
    """调用已存在的V2用例,仅引用test_step
    filename为文件路径
    case_name为需要运行的用例
    """

    _template = {"filename": "", "case_name": ""}
    # 用例模板文件名格式
    template_file_name = "{}_template.yaml"
    # 接口返回基本校验文件
    schema_file_name = "{}_schema.json"
    # 用户期望响应
    check_file_name = "{}_check.json"

    def __init__(self, args, case_value):
        self.case_file_name = args['filename']
        self.case_name = args['case_name']
        self.case_value = case_value
        self.level = case_value['_level']
        self.cases = self.gen_sub_case()

    def gen_sub_case(self) -> list:
        """生成子用例。
        [
            (case_template , case_value, case_file_name)
            (case_template , case_value, case_file_name)
        ]
        """
        from modules.case_template import CaseTemplateV2
        """生成子用例。
        [
            (CaseTemplate()[case1] , ItemValue(), case_file_name)
            (CaseTemplate()[case2] , ItemValue(), case_file_name)
        ]
        """
        cases = []
        template = CaseTemplateV2(self.case_file_name)
        case_block_keys = template.get_case_block_keys()
        if self.case_name in case_block_keys:
            case_block = template.content[self.case_name]
            template.test_step = template.gen_steps_block(
                case_block['test_step'])
        cases.append((template, self.case_value, self.case_file_name))
        return cases

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

    def data_check(self, value, template, msg=''):
        super().data_check(value, template, msg=msg)
        if not os.path.exist(value['filename']):
            raise AutoTestException('模板路径错误')

    def execute(self, executor):
        # 用例作为步骤等级和父用例等级一样
        executor(self.cases[0], self.level).execute()

    @classmethod
    def snippet(self):
        return """
        - case_v2:
            filename:
            case_name: 
        """, self.__doc__
