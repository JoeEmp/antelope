from modules.step import Step
from com.log import auto_logger


class EchoStep(Step):
    """打印变量类型和变量值
    """

    _template = ""

    def __init__(self, args, case_value, case_filename):
        self.args, self.case_value, self.case_filename = args, case_value, case_filename
        msg = "%s的echo步骤编写错误,参考 %s" % (case_filename, self.__doc__)
        self.data_check(self.args, self._template, msg)

    def data_check(self, value, template, msg=''):
        pass

    def execute(self):
        auto_logger.info("%s %s " % (type(self.args), self.args))

    @classmethod
    def snippet(self):
        """
        - echo: 
        """, self.__doc__
