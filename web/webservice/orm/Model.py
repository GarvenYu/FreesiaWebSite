#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging; logging.basicConfig(level=logging.INFO)
import asyncio
import aiomysql
from web.webservice.orm.ModelMetaclass import ModelMetaclass


@asyncio.coroutine
def create_pool(loop, **kwargs):
    logging.info("connecting database pool...")
    global __pool
    __pool = yield from aiomysql.create_pool(
        host=kwargs.get('host', 'localhost'),
        port=kwargs.get('port', 3306),
        user=kwargs['user'],
        password=kwargs['password'],
        db=kwargs['database'],
        charset=kwargs.get('charset', 'utf8'),
        autocommit=kwargs.get('autocommit', True),
        maxsize=kwargs.get('maxsize', 10),
        minsize=kwargs.get('minsize', 1),
        loop=loop
    )


@asyncio.coroutine
def destroy_pool():
    if __pool is not None:
        __pool.close()
        yield from __pool.wait_closed()

# 提供给Model查询接口


@asyncio.coroutine
def select(sql, args, size=None):
    logging.info("select,sql->(%s),args->(%s)" % (sql, args))
    with (yield from __pool) as conn:
        cursor = yield from conn.cursor(aiomysql.DictCursor)
        yield from cursor.execute(sql.replace('?', '%s'), args or ())
        if size:
            rs = yield from cursor.fetchmany(size)
        else:
            rs = yield from cursor.fetchall()
        yield from cursor.close()
        logging.info('cursor closed, rows returned: %s, result -> %s' % (len(rs), str(rs)))
        return rs

# 提供Model增删改接口


@asyncio.coroutine
def execute(sql, args):
    logging.info("insert/delete/update,sql->(%s),args->(%s)" % (sql, args))
    with (yield from __pool) as conn:
        try:
            cur = yield from conn.cursor()
            yield from cur.execute(sql.replace('?', '%s'), args)
            rows = cur.rowcount
            yield from cur.close()
        except BaseException:
            raise
        return rows


class Model(dict, metaclass=ModelMetaclass):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError("Model has no attribute (%s)" % item)

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
                setattr(self, key, field_value.default)
            return field_value.default
        return value

    @asyncio.coroutine
    def save_one_user(self):
        """
        保存用户
        :return: None
        """
        logging.info("method -> save_one_user() ,fields[] -> %s , primaryKey -> %s  " % (self.__fields__, self.__primary_key__))
        args = list(map(self.get_value_or_default, self.__fields__))
        args.append(self.get_value_or_default(self.__primary_key__))
        rows = yield from execute(self.__insert__, args)
        if rows != 1:
            logging.warning('failed to insert record: affected rows: %s' % rows)

    @classmethod
    @asyncio.coroutine
    def find_one_user_by_pk(cls, args):
        """
        根据主键获取某一用户
        :param args: cls:传递当前类对象; args:where 条件参数tuple
        :return:
        """
        rs = yield from select("%s where %s = ?" % (cls.__select__, cls.__primary_key__), (args), 1)
        if len(rs) == 0:
            return None
        else:
            logging.info(str(rs))
            return cls(**rs[0])

    @classmethod
    @asyncio.coroutine
    def find_all_user(cls, **kwargs):
        """
        **kw传入限制条件，检索符合条件的用户
        :param kwargs:
        {
        'where':{'id':1, 'email':'qwe@qwe.com',...},
        'orderBy':('id','email',...),
        'limit': 5 / (5,10)
        }
        :return:[user]
        """
        logging.info('**kwargs -> %s' % str(kwargs))
        args = []
        subsql = []
        if 'where' in kwargs:
            subsql.append('where')
            mount = len(kwargs.get('where'))  # where 条件个数
            count = 0
            for attr, value in kwargs.get('where').items():
                subsql.append(attr + '= ?')
                args.append(value)
                count = count + 1
                if count == mount:
                    break
                subsql.append('and')
        if 'orderBy' in kwargs:
            subsql.append('order by ')  # where property1= .. and property2=... order by
            mount = len(kwargs.get('orderBy'))
            if mount == 1:
                subsql.append('?')
            else:
                subsql.append('?')
                for i in range(mount-1):
                    subsql.append(',?')
            args.extend(kwargs.get('orderBy'))
        if 'limit' in kwargs:
            subsql.append('limit')
            if isinstance(kwargs.get('limit'), int):
                subsql.append('?')
                args.append(kwargs.get('limit'))
            if isinstance(kwargs.get('limit'), tuple) and len(kwargs.get('limit')) == 2:
                subsql.append('?,?')
                args.extend(kwargs.get('limit'))
            else:
                raise ValueError('Invalid limit value: %s' % str(kwargs.get('limit')))
        if len(subsql) > 0:
            sql = cls.__select__ + ' ' + ' '.join(subsql)
        else:
            sql = cls.__select__
        rs = yield from select(sql, (args))  # 返回数据 list[dict1, dict2 ...]
        return [cls(**r) for r in rs]

    @asyncio.coroutine
    def save_one_blog(self):
        """
        保存博客
        :return: None
        """
        logging.info("method -> save_one_blog() ,fields[] -> %s , primaryKey -> %s  " % (self.__fields__, self.__primary_key__))
        args = list(map(self.get_value_or_default, self.__fields__))
        args.append(self.get_value_or_default(self.__primary_key__))
        rows = yield from execute(self.__insert__, args)
        if rows != 1:
            logging.warning('failed to insert record: affected rows: %s' % rows)







