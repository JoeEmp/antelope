from modules.step.step import Step
from com.log import auto_logger


class SetStep(Step):
    """设置变量
    set_step:
        name: "device"
        value: "MP"
    """

    _template = {'name': ''}

    def __init__(self, kwargs, case_value, case_name):
        self.data_check(kwargs, self._template)
        self.kwargs = kwargs
        self.case_value = case_value

    def data_check(self, kwargs, template):
        msg = '编写错误, 请参考{}'.format(self.__doc__)
        super().data_check(kwargs, template, msg=msg)
        if 'value' not in kwargs:
            raise KeyError('缺少value')

    def execute(self):
        auto_logger.debug("%s" % self.kwargs)
        self.case_value[self.kwargs['name']] = self.kwargs['value']

    @classmethod
    def snippet(self):
        return """
        - set_step:
            name: "device"
            value: "MP"
        """, self.__doc__
