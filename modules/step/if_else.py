from modules.step import Step
from abc import ABCMeta
from com.error import BranchException, JudgeException
from modules.step_block import StepsBlock


class BranchStep(Step, metaclass=ABCMeta):

    def __init__(self, args, case_value, case_filename, step_type):
        self.args = StepsBlock(args, case_filename)
        self.case_value = case_value
        self.step_type = step_type
        self.case_filename = case_filename
        msg = '{} {}步骤格式错误'.format(case_filename, step_type)
        self.data_check(args, [], msg)

    def data_check(self, value, template, msg=''):
        super().data_check(value, template, msg=msg)
        if 0 == len(value):
            raise BranchException('%s文件%s块缺少步骤' % (
                self.case_filename, self.step_type))
        # NOTE 不是else的分支步骤，第一项必须是judge步骤
        if isinstance(value[0], dict) and 'judge' not in value[0].keys() and 'else' != self.step_type:
            raise BranchException('%s文件%s块缺少缺少判断条件' % (
                self.case_filename, self.step_type))

    def execute(self):
        pass

    def _judge_execute(self, executor):
        try:
            executor((self.args, self.case_value, self.case_filename),
                     self.case_value['_level']).execute()
            self.case_value['_if_value'] = True
        except JudgeException:
            self.case_value['_if_value'] = False


class IfStep(BranchStep):

    def __init__(self, args, case_value, case_filename):
        super().__init__(args, case_value, case_filename, 'if')

    def execute(self, executor):
        self._judge_execute(executor)

    @classmethod
    def snippet(self):
        return """
        - if_step:
            - judge: $1
        """, self.__doc__


class ElifStep(BranchStep):
    def __init__(self, args, case_value, case_filename):
        super().__init__(args, case_value, case_filename, 'elif')

    def execute(self, executor):
        if not self.case_value['_if_value']:
            self._judge_execute(executor)

    @classmethod
    def snippet(self):
        return """
        - elif_step:
            - judge: $1
        """, self.__doc__


class ElseStep(BranchStep):
    def __init__(self, args, case_value, case_filename):
        super().__init__(args, case_value, case_filename, 'else')

    def execute(self, executor):
        if not self.case_value['_if_value']:
            self._judge_execute(executor)

    @classmethod
    def snippet(self):
        return """
        - else_step:
            
        """, self.__doc__


class JudgeStep(Step):
    """判断条件步骤: 如 ”123 in {select_result}“ 具体可参考demo_case的用法"""

    _template = ''

    def __init__(self, args, case_value, case_filename):
        super().__init__(args, case_value, case_filename)
        msg = '{}文件judge格式错误'.format(case_filename)
        self.data_check(args, msg=msg)
        self.args = args

    def data_check(self, value, template='', msg=''):
        return super().data_check(value, template, msg=msg)

    def execute(self):
        # evil code
        result = bool(eval(self.args))
        if not result:
            raise JudgeException('%s is fail' % self.args)

    @classmethod
    def snippet(self):
        return """
        - judge:  # 字符串,python if 判断内容
        """, self.__doc__
