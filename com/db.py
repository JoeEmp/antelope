from records import Database, Connection, Record, RecordCollection
from com.log import auto_logger
from urllib.parse import quote
from enum import Enum, unique
from abc import abstractmethod
from sqlalchemy import text, exc


class BaseDatabase(Database):


    @classmethod
    @abstractmethod
    def gen_db_url(cls, *args, **kwargs):
        pass

    @classmethod
    def init_by_conf(cls, *args, **kwargs):
        return cls(cls.gen_db_url(*args, **kwargs))

    def get_connection(self):
        """Get a connection to this Database. Connections are retrieved from a
        pool.
        """
        if not self.open:
            raise exc.ResourceClosedError('Database closed.')

        return BaseConnection(self._engine.connect())

    def query(self, query: str, fetchall=False, **params):
        with self.get_connection() as conn:
            return conn.query(query, fetchall, **params)


class BaseConnection(Connection):

    def query(self, query, fetchall=False, **params):
        """Executes the given SQL query against the connected Database.
        Parameters can, optionally, be provided. Returns a RecordCollection,
        which can be iterated over to get result rows as dictionaries.
        """

        # Execute the given query.
        cursor = self._conn.execute(
            text(query), **params)  # TODO: PARAMS GO HERE
        auto_logger.info('affected num %d' % cursor.rowcount)

        # Row-by-row Record generator.
        row_gen = (Record(cursor.keys(), row) for row in cursor)

        # Convert psycopg2 results to RecordCollection.
        results = RecordCollection(row_gen)

        # Fetch all results if desired.
        if fetchall:
            results.all()

        return results


class MySQLDataBase(BaseDatabase):

    @classmethod
    def gen_db_url(self, host, username, pwd, port, dbname=None):
        if dbname:
            db_url = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(
                username, pwd, host, port, dbname)
        else:
            db_url = 'mysql+pymysql://{}:{}@{}:{}'.format(
                username, pwd, host, port)
        return db_url


class PostgreSQLDataBase(BaseDatabase):

    @classmethod
    def gen_db_url(cls, host, username, pwd, port, dbname):
        return 'postgresql+psycopg2://{}:{}@{}:{}/{}'.format(
            username, pwd, host, port, dbname)


class SQLiteDataBase(BaseDatabase):

    @classmethod
    def gen_db_url(self, filename):
        return "sqlite:///%s" % filename


@unique
class DB_TYPE(Enum):
    # 新增数据库链接需要在枚举新增
    mysql = MySQLDataBase
    pg = PostgreSQLDataBase
    sqlite = SQLiteDataBase
