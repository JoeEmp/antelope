from com.error import CaseTemplateException
from com.file import YamlReader


class StepsBlock():
    """将json数组转化成可执行步骤数组"""

    def __init__(self, steps_block, filename):
        self.filename = filename
        self.request_block = self.gen_request_block()
        self.steps = self.gen_can_execute_block(steps_block)

    def gen_can_execute_block(self, steps_block):
        from modules.step import STEP_TYPE
        steps = []
        for step in steps_block:
            if not isinstance(step, dict):
                raise CaseTemplateException('步骤编辑错误,内容为 %s' % step)
            try:
                for step_name, args in step.items():
                    # add step_class and class init args
                    steps.append((STEP_TYPE[step_name].value, args))
            except KeyError:
                can_use_step = [k for k in dir(
                    STEP_TYPE) if not k.startswith('__')]
                raise CaseTemplateException(
                    '%s步骤尚不支持\n支持步骤有%s' % (step_name, can_use_step))
        return steps

    def gen_request_block(self):
        from modules.case_template import CaseTemplate
        return CaseTemplate.gen_request_block(YamlReader.load_yaml_file(self.filename))

    def __add__(self, other):
        return self.steps + other

    def __radd__(self, other):
        return other + self.steps
