from abc import ABCMeta, abstractmethod
from com.file import JsonCheck


class Step(JsonCheck, metaclass=ABCMeta):

    def __init__(self, args, case_value, case_filename):
        """
        Args:
            args (list or dict): 步骤自定义参数,是确定的值可直接使用, 目前只有断言支持列表
            case_value (ItemValue): 用例变量,用于步骤设置过程中产生的变量
            case_filename (str): 用例名字, 异常报错时, 方便用户修改
        """
        pass

    @abstractmethod
    def execute(self):
        """步骤执行函数
        """

    @classmethod
    def snippet(self):
        return "", self.__doc__

    def __repr__(self):
        return str(type(self))