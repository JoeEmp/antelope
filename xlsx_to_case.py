from cli import gen_template
import re
from com.excel import ExcelReader

DATETIME_FMT = '%H:%M:%S'


class Excel2Case():
    """execl转测试用例
    execl表头
    title   会转成用例名
    module  所属模块名称
    level   优先级(可选）
    url     接口
    method  请求方式
    header  请求头(可选)
    body    请求体(可选)
    response  响应(可选)
    """

    def __init__(self, excel_filename, debug=False):
        self.root_path = 'debug_case' if debug else 'case'
        self.excel_table = ExcelReader(excel_filename).get_json_line()

    def gen_host_url(self, url: str):
        if '//' in url:
            begin, end = re.search(r'//.+?/', url).span()
            return url[:end-1], url[end-1:]
        else:
            begin, end = re.search(r'}}', url).span()
            return url[:end], url[end:]

    def gen_case_conf(self, row):
        conf = {}
        conf['path'] = row['title'].replace('/', "_")
        conf['host'], conf['url'] = self.gen_host_url(row.get('url'))
        level = row.get('level', None)
        if not level:
            conf['level'] = level
        conf['method'] = row.get('method')
        conf['module'] = row.get('module') or ''
        conf['headers'] = row.get('headers', '')
        body = row.get('body', '')
        if body:
            conf['body'] = body
        return conf

    def gen_case(self):
        for i, row in enumerate(self.excel_table):
            try:
                conf = self.gen_case_conf(row)
                gen_template(**conf)
            except Exception as e:
                print(e)


if '__main__' == __name__:
    Excel2Case('').gen_case()
