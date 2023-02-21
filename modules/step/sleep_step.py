from modules.step.step import Step
from com.log import auto_logger
import time


class SleepStep(Step):
    """思考时间(单位: 秒)
    sleep_step: 1.2
    """

    _template = 1.01

    def __init__(self, sec, case_value, case_name):
        self.data_check(sec, self._template)
        self.sec = sec
        self.case_value = case_value

    def data_check(self, kwargs, template):
        msg = '编写错误, 请参考{}'.format(self.__doc__)
        super().data_check(kwargs, template, msg=msg)

    def execute(self):
        auto_logger.info('sleep %ss' % self.sec)
        time.sleep(self.sec)

    @classmethod
    def snippet(self):
        return "- sleep_step: $1", __doc__
