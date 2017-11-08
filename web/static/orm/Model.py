# -*-coding:utf-8-*-
import logging; logging.basicConfig(level=logging.INFO)
import asyncio, aiomysql
from web.static.orm import ModelMetaclass


class Model(dict, metaclass=ModelMetaclass):
    def __init__(self, **kwargs):
        super(Model, self).__init__(**kwargs)

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(r"Model has no attribute (%s)" % item)

    def __setattr__(self, key, value):
        self[key] = value

    def get_value(self, key):
        return getattr(self, key, None)

    def get_value_or_default(self, key):
        value = getattr(self, key)
        if value is None:
            field_value = self.__mappings__[key]
            if field_value.default is not None:
                logging.info("find default value (key:%s) = (val:%s)" % (key, field_value))
                setattr(self, key, field_value)
        return field_value


@asyncio.coroutine
def create_pool(loop, **kwargs):
    logging.info("create database connection pool...")
    global __pool
    __pool = yield from aiomysql.create_pool(
        host=kwargs.get('host', 'localhost'),
        port=kwargs.get('port', 3306),
        user=kwargs['user'],
        password=kwargs['password'],
        db=kwargs['db'],
        charset=kwargs.get('charset', 'utf8'),
        autocommit=kwargs.get('autocommit', True),
        maxsize=kwargs.get('maxsize', 10),
        minsize=kwargs.get('minsize', 1),
        loop=loop
    )


@asyncio.coroutine
def select(sql, args, size=None):
    logging.info("sql->(%s),args->(%s)" % (sql, args))
    with (yield from __pool) as conn:
        cursor = yield from conn.cursor(aiomysql.DictCursor)
        yield from cursor.execute(sql.replace('?', '%s'), args or ())
        if size:
            rs = yield from cursor.fetchmany(size)
        else:
            rs = yield from cursor.fetchall()
        yield from cursor.close()
        logging.info('rows returned: %s' % len(rs))
        return rs