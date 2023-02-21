from datetime import datetime
import xlrd
from cli import gen_template
import re

DATETIME_FMT = '%H:%M:%S'


class MyExcel():
    def __init__(self, xls, sheet_name='Sheet1'):
        self.xls, self.sheet_name = xls, sheet_name
        self.header, self.rows = self.read_excel_xls()
        self.dict_table = self.to_dict()

    def read_excel_xls(self, xls='', sheet_name=''):
        """读取excel,返回字段名和数据(以行为单位) 
        [['name','local'],
         ['joe','china']]
        """
        xls = xls or self.xls
        sheet_name = sheet_name or self.sheet_name
        self.workbook = xlrd.open_workbook(xls)
        self.sheet = self.workbook.sheet_by_name(sheet_name)
        rows = []
        for row in range(self.sheet.nrows):
            line = []
            for col in range(self.sheet.ncols):
                line.append(self.dispaly_value(row, col))
            rows.append(line)
        header = rows.pop(0)
        return header, rows

    def dispaly_value(self, row, col):
        """return dispaly value which your edit"""
        # 兼容日期value为浮点数的情况
        value = self.sheet.cell(row, col)
        if 3 == value.ctype:
            date_tuple = xlrd.xldate_as_tuple(
                self.sheet.cell_value(row, col), self.workbook.datemode)
            return datetime(*date_tuple).strftime(DATETIME_FMT)
        return value

    def to_dict(self, header=None, rows=None):
        """行数据转json格式
        [{"name","joe"},{"local","china"}]
        """
        dict_table = []
        rows = rows or self.rows
        header = header or self.header
        for row in rows:
            d = {}
            for i in range(len(row)):
                key, value = header[i].value.split('/')[-1], row[i].value
                d[key] = value
            dict_table.append(d)
        return dict_table


class Excel2Case():
    def __init__(self, excel_filename, debug=False):
        self.root_path = 'debug_case' if debug else 'case'
        self.excel_table = MyExcel(excel_filename).dict_table

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
        conf['module'] = row.get('module')
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
    Excel2Case('xxx.xlsx').gen_case()
