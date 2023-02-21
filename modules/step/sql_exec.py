from decimal import Decimal
from modules.step.step import Step
from com.error import CaseValueException
from com.log import auto_logger
from com.error import AutoTestException
from _datetime import date, datetime


class SqlExecStep(Step):
    """
    # 步骤写法
    sql_exec:
        db: mysql
        sql: select 1
        sql_result_name: sql_select
    """
    # 最小模板
    template = {"db": "", "sql": 'select 1', "sql_result_name": 'sql_select'}

    def __init__(self, db_connects, args, case_value, case_name):
        self.db_connects = db_connects
        self.args = args
        self.case_value = case_value
        self.case_name = case_name
        self.data_check(self.args, self.template)

    @classmethod
    def by_code(cls, db_connects, db_connect_name, sql, case_value, case_name, sql_result_name='sql_select'):
        """python代码使用sql步骤
        Args:
            db_connects 用例变量或者是全局变量,主要是用例变量: 
            db_connect_name : 链接名
            sql (_type_): 执行sql
            case_value (_type_): 用例变量
            case_name : 用例名，调用是传入 __file__ 即可
            sql_result_name : 结果的key,结果存入 case_value
        """
        args = {"db": db_connect_name, "sql": sql,
                "sql_result_name": sql_result_name}
        return cls(db_connects, args, case_value, case_name)

    @classmethod
    def snippet(self):
        return """
        - sql_exec:
            db: 
            sql: 
            sql_result_name: 
        """, self.__doc__

    def _query(self, sql: str, params=None, time_format='', *args, **kwargs):
        """返回查询数据

        Args:
            sql : sql
            value_name : 结果存储的变量名
            params : sql的参数
        """
        time_format = time_format or '%Y-%m-%d %H:%M:%S'

        if not params:
            params = dict()
        params.pop('fetchall', None)
        auto_logger.info(sql)
        auto_logger.info(str(params))
        if self.is_dml(sql):
            row = self.db.query(sql, **params)
            return row
        else:
            rows = self.db.query(sql, fetchall=True, **params)
        rows = rows.all(as_dict=True)
        rows = self.to_json(rows, time_format)
        if 0 == len(rows):
            auto_logger.warning('查询为空')
        rows_str = '\n'.join([str(row) for row in rows])
        auto_logger.info('query rows\n[%s]' % rows_str)
        return rows

    def is_dml(self, sql: str) -> bool:
        sql = sql.strip().lower()
        return sql.startswith('update') or sql.startswith('delete') or sql.startswith('insert')

    def to_json(self, rows: list, time_format):
        """将查询结果的datetime对象转字符串

        Args:
            rows (list): 记录
            time_format (str, optional): 时间格式.

        Returns:
            list: 
        """
        for row in rows:
            for k, v in row.items():
                if isinstance(v, Decimal):
                    row[k] = int(v)
                if isinstance(v, (datetime, date)):
                    row[k] = v.strftime(time_format)
        return rows

    def data_check(self, case_value, template):
        """检验的同时从用例变量内获取db链接。"""
        msg = '用例%s,sql步骤编写错误,参考文档' % (self.case_name)
        super().data_check(case_value, self.template, msg=msg)
        try:
            self.db = self.db_connects.get_db(self.args['db'])
        except KeyError:
            raise CaseValueException('无%s数据库配置,无法执行步骤' % self.args['db'])

    def execute(self, params=None):
        result = self._query(self.args['sql'], params)
        try:
            value_name = self.args['sql_result_name']
            self.case_value[value_name] = result
            return result
        except KeyError as e:
            auto_logger.warning('查询结果没有存入变量')
        except Exception as e:
            raise AutoTestException(str(e))
