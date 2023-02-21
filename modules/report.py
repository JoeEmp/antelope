from com.allure_api import AllureApi
from com.send_mail import MailCheck, SendMail
from com.net import get_host_ip
from com.log import auto_logger
from com.error import EmailException
import os
from abc import abstractmethod, ABCMeta


class Report(metaclass=ABCMeta):

    last_report_path = './report/last'

    def __init__(self, mail_conf: str, allure_path: str, report_path: str):
        """
        Args:
            mail_conf (str): 邮箱配置文件
            allure_path (str): allure可执行路径
            report_path (str): 报告生成位置，默认在allure的report_perfix下生成
        """
        self.allure_api = AllureApi(allure_path)
        try:
            self.mail_check = MailCheck(mail_conf)
        except Exception as e:
            auto_logger.warning(e)
            self.mail_check = None
        self.report_path = report_path

    def send_mail(self, title='', content='', content_type='plain', is_debug=False):
        """发送邮件
        Args:
            title (str, optional): 邮件标题. Defaults to ''.
            content (str, optional): 邮件正文. Defaults to ''.
        """
        self.gen_report()
        self.open_web()
        if not title or not content:
            title, content, content_type = self.gen_title_and_content()
        try:
            SendMail(**self.mail_check.value).send(
                **self.mail_check.value,
                title=title,
                content=content,
                content_type=content_type)
        except Exception as e:
            raise EmailException('发送邮件异常,请检查邮件配置文件')

    def gen_report(self):
        self.allure_api.gen_report(self.report_path)

    def open_web(self):
        self.allure_api.open_web(self.last_report_path)

    @abstractmethod
    def gen_title_and_content(self):
        """自定义生成 标题和内容及内容格式

        Returns:
            tuple: title, content, content_type
        content_type 支持类型见 MIMEText
        """
        title = "测试报告_" + self.report_path.replace('_', '')
        auto_logger.info(os.sep.join(
            (self.allure_api.report_perfix, self.report_path, 'widgets', 'suites.json')))
        self.allure_api.is_empty(self.report_path)
        _, statistics = self.preview()
        auto_logger.debug(statistics)
        total = sum([s['total'] for s in statistics])
        failed = sum([s['failed'] for s in statistics]) + \
            sum([s['broken'] for s in statistics])
        passed = sum([s['passed'] for s in statistics])
        skipped = sum([s['skipped'] for s in statistics])
        content = """
            <html>
            <head>
                <style type="text/css">
                    p { border: 3px }
                    .error { color: red; }
                    .skip { color: rgb(151, 151, 151);}
                    .succ { color: rgb(145, 204, 58);}
                </style>
            </head>

            <body>
                <p><a href="%s" target="_blank">测试报告查看地址</a></p>
                <p>运行总数: %s</p>
                <p class="error">运行失败: %s</p>
                <p class="succ">运行成功: %s</p>
                <p class="skip">运行跳过: %s</p>
            </body>

            </html>
        """ % (
            'http://{}:{}'.format(get_host_ip(), self.allure_api.port),
            total,
            failed,
            passed,
            skipped
        )
        return title, content, 'html'

    def preview(self):
        return self.allure_api.preview(self.report_path)


class MyReport(Report):
    def gen_title_and_content(self):
        return super().gen_title_and_content()
