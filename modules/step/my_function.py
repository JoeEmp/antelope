from com.log import auto_logger
from modules.step import Step
from importlib import import_module
from com.error import AutoTestException, FunctionException


class MyFunctionStep(Step):
    """
    # 用户自定义方法
    func:
        # 方法路径
        name: func_path
        args: 
            - 123
            - 456
        kwargs:
            name: Joe
        # 可以不填，目前用例变量会传入到自定义函数，函数可以直接操作用例变量
        func_result: name
    """

    _template = {"name": ""}

    def __init__(self, args, case_value, case_filename):
        self.args, self.case_value, self.case_filename = args, case_value, case_filename
        msg = "%s的自定义步骤编写错误,参考%s" % (case_filename, self.__doc__)
        self.data_check(self.args, self._template, msg)
        self.gen_func(self.name, self.func_args, self.func_kwargs)

    def gen_func(self, name, args, kwargs):
        index = name[::-1].index('.') + 1
        if 2 == index:
            raise FunctionException('无法引用runnner文件的方法')
        self.func, self.pkg = name[-index+1:], name[:-index]
        auto_logger.warning("%s %s " % (self.func, self.pkg))
        try:
            self.pkg = import_module(self.pkg)
        except ModuleNotFoundError:
            pkg_file = './' + self.pkg.replace('.', '/')
            raise FunctionException('文件 %s 未找到' % pkg_file)
        try:
            self.func = getattr(self.pkg, self.func)
        except AttributeError:
            raise FunctionException('文件 %s 缺少方法或类%s' %
                                    (self.pkg.__file__, self.func))

    def data_check(self, value, template, msg=''):
        super().data_check(value, template, msg=msg)
        self.name = value['name']
        if isinstance(value.get('args', []), list):
            self.func_args = value.get('args', [])
        else:
            raise AutoTestException('args参数错误')
        if isinstance(value.get('kwargs', {}), dict):
            self.func_kwargs = value.get('kwargs', {})
        else:
            raise AutoTestException('kwargs参数错误')
        func_result = value.get('func_result')
        if func_result and not isinstance(func_result, str):
            raise AutoTestException('kwargs参数错误')
        else:
            self.func_result = func_result

    def execute(self):
        result = self.func(case_value=self.case_value,
                           *self.func_args, **self.func_kwargs)
        # if self.func_result:
        #     self.case_value[self.func_result] = result
