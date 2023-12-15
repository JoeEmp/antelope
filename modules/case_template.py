
from abc import abstractmethod
from ast import Dict
import re
from com.error import CaseTemplateException
from com.log import auto_logger
from com.file import YamlReader
from modules.step import STEP_TYPE, RequestStep
from modules.step_block import StepsBlock
import json


class CaseTemplateInterFace(YamlReader):
    """用例模板接口。"""

    def __init__(self, filename, template=None):
        """载入用例模板, 请求模板,方法模版, 生成可执行的用例
        Args:
            filename (str): 模板具体的文件
        """
        self._template = template or dict()
        self.filename = filename
        self.content = self.load_yaml_file(filename)
        self.is_skip = self.content.get('is_skip', False)
        auto_logger.debug(f'case_template: {self.content}')
        self.data_check(self.content, self._template,msg='用例模板 %s,格式错误' % filename)
        self.request_block = self.gen_request_block(self.content, filename)
        self.template_block_dict = self.gen_template_block_dict(self.content, filename)

    def data_check(self, value, template, msg=''):
        if value.get('is_api_case', True):
            auto_logger.info('is not api case, init request block')
            self._template['request'] = RequestStep.template_request
        else:
            auto_logger.info('is not api case')
        auto_logger.info('case template %s' % value)
        super().data_check(value, template, msg=msg)

    @staticmethod
    def gen_request_block(case_template: dict, filename='') -> dict:
        request_block = case_template.get('request', None)
        auto_logger.debug('request block is %s' % request_block)
        if request_block:
            try:
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
            except json.JSONDecodeError:
                raise CaseTemplateException('用例 %s , requests编写错误' % filename)
        return request_block

    def gen_steps_block(self, case_block: list) -> list:
        """json列表转为可以执行列表
        Args:
            case_block (list):json列表
        Raises:
            CaseTemplateException: _description_
        Returns:
            list: 执行列表
        """
        steps = []
        for step_block in case_block:
            # TODO 好像是无效代码，追加测试用例
            if not step_block:
                break
            try:
                for step_name, args in step_block.items():
                    # add step_class and class init args
                    steps.append((STEP_TYPE[step_name].value, args))
            except KeyError:
                can_use_step = [k for k in dir(STEP_TYPE) if not k.startswith('__')]
                auto_logger.warning('step is %s' % step_name)
                raise CaseTemplateException('%s步骤尚不支持\n支持步骤有%s' % (step_name, can_use_step))
        return steps

    @staticmethod
    def gen_template_block_dict(case_template, filename='') -> dict:
        template_block_dict = {}
        for key in case_template:
            if not re.compile(r'template.*').search(key):
                continue
            steps = case_template[key]
            if not isinstance(steps, list):
                raise CaseTemplateException(f'文件:{filename},{key}模版类型错误,应为list类型')
            template_block_dict[key] = steps
        return template_block_dict


    @abstractmethod
    def gen_steps(self) -> list:
        return []


class CaseTemplate(CaseTemplateInterFace):
    """用例模板V1
    返回
    [  
        (steps , args),
        (steps , args),
    ]
    """

    def __init__(self, filename):
        auto_logger.debug('v2 case validate')
        super().__init__(filename, {'case': []})
        self.steps = self.gen_steps()

    def gen_steps(self):
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
        case_block = self.content['case']
        steps = []
        if self.content.get('is_skip', False):
            return steps
        return self.gen_steps_block(case_block)

    def __repr__(self):
        return "CaseTemplate('%s')" % self.filename


class CaseTemplateV2(CaseTemplateInterFace):
    """用例模板V2
    step_dict = 
    {
    "case1" : [  
        (steps , args)
    ],
    "case2" : [  
        (steps , args)
    ]
    }
    """

    def __init__(self, filename):
        super().__init__(filename, {
            '_version': 2.0,
            '^case.*': {
                'test_step': []
            }
        })
        self.step_dict = self.gen_steps()

    def get_case_block_keys(self):
        for key in self.content:
            if re.compile(r'^case.*').search(key):
                yield key

    def gen_steps(self) -> dict:
        step_dict = {}
        for key in self.get_case_block_keys():
            step_dict[key] = self.gen_steps_block(
                self.content[key]['test_step'])
        return step_dict

    def json_to_schema(self, to_schema_json) -> dict:
        return super().json_to_schema(to_schema_json, 'pattern')

    def __repr__(self):
        return "CaseTemplateV2('%s')" % self.filename
