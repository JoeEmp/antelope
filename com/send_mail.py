import smtplib
from email.mime.text import MIMEText
import re
from email.utils import formataddr
from com.file import YamlReader


class SendMail():

    mail_pattern = r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$'

    def __init__(self, sender_addr, sender_pwd, host, port=None, use_ssl=True, *args, **kwargs):
        if not self.is_email(sender_addr):
            raise ValueError('发送者邮箱错误')
        self.sender_addr = sender_addr
        self.sender_pwd = sender_pwd
        self.host = host
        self.port = port or 25
        self.use_ssl = use_ssl
        self._login()

    def is_email(self, addr):
        return re.search(self.mail_pattern, addr, flags=0)

    def _login(self):
        if self.use_ssl:
            self.conn = smtplib.SMTP_SSL(self.host, self.port)
        else:
            self.conn = smtplib.SMTP(self.host, self.port)
        self.conn.login(self.sender_addr, self.sender_pwd)

    def check_to_addrs(self, to_addrs):
        if isinstance(to_addrs, str):
            to_addrs = [to_addrs]
        for to_addr in to_addrs:
            if not self.is_email(to_addr):
                raise ValueError('接受者邮箱[%s]错误' % to_addr)
        return ','.join(to_addrs)

    def send(self, title, to_addrs, content, sender_name='', content_type='plain', *args, **kwargs):
        msg = MIMEText(content, content_type, 'utf-8')
        # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        sender_name = sender_name or self.sender_addr
        msg['From'] = formataddr((sender_name, self.sender_addr))
        msg['To'] = self.check_to_addrs(to_addrs)
        msg['Subject'] = title
        self.conn.sendmail(self.sender_addr, to_addrs, msg.as_string())

    def _close(self):
        self.conn.close()

    def __del__(self):
        self._close()


class MailCheck(YamlReader):

    def __init__(self, filename):
        self._tmeplate = {'sender_addr': '',
                          'sender_pwd': '',
                          'host': '',
                          'port': 25
                          }
        self.filename = filename
        self.value = self.load_yaml_file(filename)
        self.data_check(self.value, self._tmeplate)

    def data_check(self, value, template, msg=''):
        msg = '%s格式错误' % self.filename
        super().data_check(value, template, msg=msg)
        if 'to_addrs' not in value.keys():
            raise ValueError('收件人邮箱不能为空')
        if not isinstance(value['to_addrs'], (str, list)):
            raise ValueError('to_addrs类型错误应该列表或者字符串')
        if value.get('sender_name', None) and not isinstance(value['sender_name'], str):
            raise ValueError
        else:
            value['sender_name'] = value['sender_addr']
        value['use_ssl'] = value.get('use_ssl', True)
        value['is_debug'] = value.get('is_debug', False)
