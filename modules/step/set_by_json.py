from modules.step.step import Step
from com.log import auto_logger
from modules.case_value import ItemValue
 
 
class SetByJsonStep(Step):
    """设置变量
    set_by_json: {}
    """
 
    _template = {}
 
    def __init__(self, kwargs, case_value: ItemValue, case_name: str):
        self.data_check(kwargs, self._template)
        self.kwargs = kwargs
        self.case_value = case_value
 
    def data_check(self, kwargs, template):
        msg = '编写错误, 请参考{}'.format(self.__doc__)
        super().data_check(kwargs, template, msg=msg)
 
    def execute(self):
        auto_logger.debug("%s" % self.kwargs)
        self.case_value.update(self.kwargs)
 
    @classmethod
    def snippet(self):
        return """
        - set_by_json: {}
        """, self.__doc__