from modules.step import Step
from modules.case_value import ItemValue
from com.error import OssException
import oss2


class OssStep(Step):
    """
    # 用户自定义方法
    oss_upload:
        oss_name: 
        bucket_name: 
        // 本地文件路径
        path: 本地文件路径
        // 上传文件的url存放的变量名
        result_name: file_url
    """

    _template = {"oss_name": "", "bucket_name": '',
                 "path": "", 'result_name': ''}

    def __init__(self, oss_connects: ItemValue, args, case_value, case_name):
        self.oss_connects = oss_connects
        self.args = args
        self.case_value = case_value
        self.case_name = case_name
        self.data_check(self.args, self._template)
        self.oss_name, self.bucket_name, self.path, self.result_name = args[
            'oss_name'], args['bucket_name'], args['path'], args['result_name']

    def data_check(self, value, template, msg=''):
        msg = '步骤编写错误，请参考\n%s' % __doc__
        super().data_check(value, template, msg=msg)

    def execute(self):
        oss_obj = self.oss_connects.get_oss(self.oss_name)
        try:
            url = oss_obj.upload(self.bucket_name, self.path)
        except oss2.exceptions.AccessDenied:
            raise OssException('oss权限不足')
        self.case_value[self.result_name] = url
        return url

    @classmethod
    def snippet(self):
        return """
        # 用户自定义方法
        oss_upload:
            oss_name: 
            bucket_name: 
            path:
            result_name: 
        """, self.__doc__
