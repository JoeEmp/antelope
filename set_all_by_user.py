from com.setup_all import SetUpAll


class SetUpAllByUser(SetUpAll):
    """用户自定义setup all操作, 仅需实现execute方法"""

    def __init__(self, global_value):
        self.global_value = global_value

    # def login(self):
    #     pass

    def execute(self):
        """用户自行实现"""
        # status, token = self.login()
        # self.global_value['token'] = token

def setup_all():
    pass

def tear_all():
    pass