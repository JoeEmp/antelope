
from com.error import CaseTemplateException
from com.log import auto_logger
from com.file import YamlReader
from modules.step import STEP_TYPE, RequestStep
import json


class CaseTemplate(YamlReader):
    """用例模板
    返回
    (steps , args)
    """

    def __init__(self, filename):
        """载入用例模板, 请求模板, 生成可执行的用例
        Args:
            filename (str): 模板具体的文件
        """
        self._template = {'case': []}
        self.filename = filename
        self.case_template = self.load_yaml_file(filename)
        self.is_skip = self.case_template.get('is_skip', False)
        self.data_check(self.case_template, self._template,
                        msg=' %s 模板格式错误' % filename)
        self.case_block = self.case_template['case']
        self.request_block = self.gen_request_block(self.case_template)
        self.steps = self.gen_case()

    def data_check(self, value, template, msg=''):
        auto_logger.info(template)
        if value.get('is_api_case', True):
            self._template['request'] = RequestStep.template_request
        auto_logger.info('case template %s' % template)
        super().data_check(value, self._template, msg=msg)

    @staticmethod
    def gen_request_block(case_template):
        request_block = case_template.get('request', None)
        auto_logger.debug('request block is %s' % request_block)
        if request_block:
            body = request_block.get('body', None)
            if body and isinstance(body, str):
                request_block['body'] = json.loads(body)
            elif body and isinstance(body, dict):
                request_block['body'] = body
            headers = request_block.get('headers', None)
            if headers and isinstance(headers, str):
                request_block['headers'] = json.loads(headers)
            elif headers and isinstance(headers, dict):
                request_block['headers'] = headers
        return request_block

    def gen_case(self):
        """
        case_block
        {"case":[
            {
                'sql_exec':{"db":'test','sql':"select {one}",'sql_result_name':'num'}
            }
        ]}
        返回
        [
            (step_class, args),
            (step_class, args),
        ]
        """
        steps = []
        if self.case_template.get('is_skip', False):
            return steps
        for step_block in self.case_block:
            # TODO 好像是无效代码，追加测试用例
            if not step_block:
                break
            try:
                for step_name, args in step_block.items():
                    # add step_class and class init args
                    steps.append((STEP_TYPE[step_name].value, args))
            except KeyError:
                can_use_step = [k for k in dir(
                    STEP_TYPE) if not k.startswith('__')]
                auto_logger.warning('step is %s' % step_name)
                raise CaseTemplateException(
                    '%s步骤尚不支持\n支持步骤有%s' % (step_name, can_use_step))
        return steps

    def __repr__(self):
        return "CaseTemplate('%s')" % self.filename
