from abc import ABCMeta, abstractmethod


class SetUpAll(metaclass=ABCMeta):
    @abstractmethod
    def execute(self):
        """该方法去自行调用,请勿在初始化中调用"""