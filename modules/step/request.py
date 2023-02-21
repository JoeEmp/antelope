import requests
from com.error import YamlSyntaxException, AutoTestException, RequestException
from modules.step.step import Step
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from requests import Response
from com.log import auto_logger
from enum import Enum, unique
import time


@unique
class CHECK_RESPONSE_TYPE(Enum):
    # 不同的用例对应响应格式校验
    success = '{}_schema_success.json'
    fail = '{}_schema_fail.json'


class RequestStep(Step):
    """
    request:
        host:
        method:
        url:
        #可选
        headers:
        #可选
        body:
        response_value_name: response
    """

    template_request = {'host': '', 'method': '', 'url': ''}
    # template_reponse = {'host': '', 'method': '', 'url': ''}

    def __init__(self, args, case_value, case_name):
        self.proxies = {
            "http": "http://127.0.0.1:8888",
            "https": "http://127.0.0.1:8888",
        }
        self.args = args
        self.response_value_name = 'response'
        self.case_value = case_value
        self.case_name = case_name
        self.data_check(self.args)

    # def _request(self,**kwargs):
    #     result = requests.request(timeout=(5,10),**kwargs)
    #     return result

    #
    def _request(self, **kwargs):
        s = requests.session()
        s.mount('http://', HTTPAdapter(max_retries=2))
        s.mount('https://', HTTPAdapter(max_retries=2))
        # result = s.request(timeout=5, **kwargs,proxies=self.proxies,verify=False)
        # 超时5s
        result = s.request(timeout=5, **kwargs)
        if isinstance(result, Response):
            auto_logger.info("{} {} {}".format('-'*33, 'request result', '-'*33))
            auto_logger.info("url: %s" % result.url)
            auto_logger.info("headers: %s" % result.request.headers)
            auto_logger.info("body: %s" % result.request.body)
            auto_logger.info("response: %s" % result.text)
            auto_logger.info("-"*80)
        return result

    def data_check(self, args: dict):
        msg = '编写错误, 请参考{}'.format(self.__doc__)
        super().data_check(args, self.template_request, msg=msg)
        argkey = args.keys()
        if args['host'] and args['url']:
            args['url'] = urljoin(args['host'], args['url'])
            args.pop('host')
        else:
            raise YamlSyntaxException('用例%s,host或url编写错误' % self.case_name)
        if 'response_value_name' in argkey:
            self.response_value_name = args['response_value_name']
            args.pop('response_value_name')
        if 'body' in argkey:
            args['json'] = args.pop('body')

        self.args = args

    def execute(self):
        try:
            start_time = time.time()
            auto_logger.info("url: %s" % self.args['url'])
            auto_logger.info("headers: %s" % self.args.get(
                'headers', 'requests def headers'))
            auto_logger.info("body: %r" % self.args.get('json', {}))
            result = self._request(**self.args)
            auto_logger.info('requests time is %dms' % int((time.time() - start_time)*1000))
            code = result.status_code
            self.case_value[self.response_value_name] = result.json()
            # TODO 针对conten-type 做不同的返回
            return code, result.json()
        except requests.Timeout as e:
            raise RequestException('%s请求超时' % self.args['url'])
        except requests.RequestException as e:
            print('Url==> {} 请求异常 \n 错误信息为==> {}'.format(self.args["url"], e))
        except Exception as e:
            raise AutoTestException(str(e))


    def check_responese(self):
        pass


class AIoTRequestStep(RequestStep):
    pass
    # def check_responese(self):
    #     if self.case_value[self.response_value_name].get('code', '') in ['', '500']:
    #         raise RequestException('响应异常')
