import os
from com.error import AutoTestException
from modules.step.step import Step
from com.log import auto_logger
from modules.step_block import StepsBlock


class TemplateBlockStep(Step):
    """
    用例外模版引用:
        有文件 aiot_case/yaml/a_case/a_case_template.yaml内,有模板 template2、template3
        - template: aiot_case.yaml.a_case.a_case_template.template3
    用例内模版引用:
        模板 template2、template3
        - template: template3
    """

    def __init__(self, args, case_value, case_filename):
        self.case_value = case_value
        self.case_filename = case_filename
        self.data_check(args, [], '引用template步骤错误')
        self.steps = StepsBlock(self.quote_template, self.filename)

    def execute(self, executor) -> list:
        executor((self.steps, self.case_value, self.case_filename),
                 self.case_value['_level']).execute()

    def data_check(self, value, template, msg=''):
        super().data_check(value, template, msg)
        if '.' not in value:
            self.filename, self.quote_template = self.case_filename, value
        else:
            self.filename, self.quote_template = value.rsplit('.', 1)
            self.filename.replace('.', os.sep.path)
            if not os.path.exist(self.filename):
                raise AutoTestException('引用文件路径错误')
        auto_logger.info(f'{self.filename}, {self.quote_template}')

    @classmethod
    def snippet(self):
        return """
        - template: 
        """, self.__doc__
