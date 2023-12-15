from com.value import Value
from com.error import GlobalValueException, AutoTestException
from com.log import auto_logger
from com.db import DB_TYPE


class GlobalValue(Value):
    """
    初始化全局变量
    通用的配置连接(如数据库、webdriver、mqtt连接)
    """

    def __init__(self, file_path, env):
        self._template = {}
        self.file_path = file_path
        if file_path:
            super().__init__(file_path)
        else:
            self._value = {}
        self._value = self.get_env_value(self._value, env)
        self._value['_db'] = self.gen_db()
        self.env = env

    def get_env_value(self, value, env):
        value = value.get(env, {})
        if not value:
            auto_logger.warning('%s环境的全局变量未配置, 或配置为空' % env)
        return value

    def gen_db(self):
        db_links = {}
        for db_link_name, conf in self._value.get('db', {}).items():
            db_type = conf.pop("type", None)
            if not db_type:
                raise GlobalValueException('缺少数据库类型无法生成链接')
            try:
                db_class = DB_TYPE[db_type].value
                db_links[db_link_name] = db_class.init_by_conf(**conf)
            except KeyError as e:
                raise AutoTestException('%s类型的db没有具体的实现,请联系开发者' % db_type)
        return db_links

    def __repr__(self):
        return "GlobalValue('%s')" % self.file_path
