import os
import sys
import shutil
from com.log import auto_logger
from com.error import ReportException
from com.file import load_json


class AllureApi():

    # web服务端口
    port = 5002
    # report
    report_perfix = 'report'

    def __init__(self, allure_path):
        self.allure_path = allure_path
        self.has_env = self.cli_check()
        if not self.has_env:
            auto_logger.warning('{}无法使用，请检查环境')
        self.report_preview, self.statistics = [], []

    def cli_check(self):
        command = "{} --help".format(self.allure_path)
        with os.popen(command) as p:
            result = p.read()
            p.close()
            if 'Print commandline help.' in result:
                return True

    def open_web(self, report_path):
        if not self.has_env:
            return
        self.kill_web_server()
        if 'win32' == sys.platform.lower():
            command = 'start /min {} open {}  -p {}'.format(self.allure_path,
                                                            report_path, self.port)
        else:
            command = 'nohup {} open {} -p {} & > allure.log 2>&1 &'.format(self.allure_path,
                                                                            report_path, self.port)
        os.system(command)
        auto_logger.info('open_web')

    def kill_web_server(self):
        if not self.has_env:
            return
        if 'win32' == sys.platform.lower():
            os.popen('taskkill /pid ' + str(self.port) + ' /F')
        else:
            os.system('kill -9 `lsof -ti:{}`'.format(self.port))
        auto_logger.info('kill web')

    def gen_report(self, path):
        # allure generate ./temp -o ./report/{} --clean
        if not self.has_env:
            return
        os.system(
            '{} generate ./temp -o {}/{} --clean'.format(self.allure_path, self.report_perfix, path))
        shutil.rmtree(os.path.join('report','last'),ignore_errors=FileNotFoundError)
        shutil.copytree(os.path.join(self.report_perfix,path),
                        os.path.join(self.report_perfix,'last'))
        auto_logger.debug('gen_report')

    def preview(self, report_path):
        # TODO 加入模块
        # 读取的json结构
        # {   "total": 1,
        #     "items": [{
        #         "uid": "785761592430c80cb18dc5e45c948829",
        #         "name": "runner",
        #         "statistic": {
        #             "failed": 1, "broken": 0, "skipped": 1, "passed": 3, "unknown": 0,"total": 5
        #         }
        #     }]
        # }
        if self.report_preview or self.statistics:
            return self.report_preview, self.statistics
        statistics = {}
        report_preview_path = os.sep.join((self.report_perfix, report_path, 'widgets', 'suites.json'))
        auto_logger.info("suites.json file path is %s" % report_preview_path)
        report_preview = load_json(report_preview_path)
        if 0 < len(report_preview['items']):
            statistics = [i['statistic'] for i in report_preview['items']]
        self.report_preview, self.statistics = report_preview['items'], statistics
        return report_preview['items'], statistics

    def is_empty(self, path):
        result_preview, _ = self.preview(path)
        if len(result_preview) <= 0:
            raise ReportException('报告内容为空,框架执行异常')
