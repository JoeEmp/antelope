# 在项目项目根目录执行
# 用于接口录制
import sys
import os
if os.path.dirname(os.getcwd()) == os.path.dirname(__file__):
    sys.path.append("..")
else:
    sys.path.append('.')
import json
from mitmproxy import http
from datetime import datetime
from com.excel import ExcelWirter
import copy


nt = datetime.now()


class logRecord:
    def __init__(self):
        self.ts = nt.strftime("%Y%m%d%H%M%S")
        # 需要录制的主机
        self.target_hosts = []
        self.filename = '%s.xlsx' % self.ts
        self.use_header = [
            'authorization',
            'user-agent',
            'userid',
            'tenantid',
            'content-type'
        ]
        self.request_log = {}

    def request(self, flow: http.HTTPFlow):
        if not self.target_hosts or flow.request.host in self.target_hosts:
            self.request_log['title'] = flow.request.url.split('/')[-1]
            self.request_log['module'] = ''
            self.request_log['url'] = flow.request.url
            self.request_log['level'] = ''
            self.request_log['method'] = flow.request.method
            self.request_log['headers'] = dict()
            headers = copy.deepcopy(flow.request.headers)
            for key, value in headers.items():
                if key in self.use_header:
                    self.request_log['headers'][key] = value
            self.request_log['headers'] = json.dumps(
                self.request_log['headers'], ensure_ascii=False)
            self.request_log['body'] = flow.request.text

            ExcelWirter().save(list(self.request_log.keys()), rows=[
                self.request_log], row_type='dict', filename=self.filename, sheet_name='Sheet')


addons = [
    logRecord()
]
