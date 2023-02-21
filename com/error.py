"""自动化测试错误,通过这个错误去处理一些异常"""


class AutoTestException(BaseException):
    """自动化测试错误,通过这个错误去处理一些异常"""

    def __init__(self, reason, *args, **kwargs):
        self.reason = reason
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.reason


class YamlSyntaxException(AutoTestException):
    """用例编写错误"""


class CaseValueException(AutoTestException):
    """用例变量错误"""


class GlobalValueException(AutoTestException):
    """用例变量错误"""


class CaseTemplateException(AutoTestException):
    """用例模板错误"""


class RequestException(AutoTestException):
    """发送请求错误"""


class AssertException(AutoTestException):
    """断言请求错误"""


class BranchException(AutoTestException):
    """分支错误"""


class JudgeException(AutoTestException):
    """判断错误"""


class FunctionException(AutoTestException):
    """自定义方法编写错误"""


class OssException(AutoTestException):
    """oss步骤错误"""


class ReportException(AutoTestException):
    """报告异常"""


class EmailException(AutoTestException):
    """邮件异常"""
