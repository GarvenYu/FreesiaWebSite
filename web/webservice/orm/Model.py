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
    def find_one_user_by_email(cls, args):
        """
        根据邮箱获取某一用户
        :param args: cls:传递当前类对象; args:where 条件参数tuple
        :return:user
        """
        rs = yield from select("%s where %s = ?" % (cls.__select__, 'email'), (args), 1)
        if len(rs) == 0:
            return None
        else:
            logging.info(str(rs))
            return cls(**rs[0])

    @classmethod
    @asyncio.coroutine
    def find_all(cls, where=None, args=None, **kw):
        """
        根据查询条件得到某一实体或全体实体
        :param where: where子句,参数值用？代替,'where id = ?'
        :param args: 参数
        :param kw: {'orderBy':'', 'limit':''}
        :return: user or user_list
        """
        sql = [cls.__select__]
        if where:
            sql.append(where)
        if args is None:
            args = []
        orderBy = kw.get('orderBy', None)
        if orderBy:
            sql.append('order by')
            sql.append(orderBy)
        limit = kw.get('limit', None)
        if limit is not None:
            sql.append('limit')
            if isinstance(limit, int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:
                sql.append('?, ?')
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value: %s' % str(limit))
        rs = yield from select(' '.join(sql), args)
        if len(rs) > 1:
            return [cls(**r) for r in rs]
        elif len(rs) == 1:
            return cls(**rs[0])
        else:
            return []

    @classmethod
    @asyncio.coroutine
    def find_number(cls, select_field, where=None, args=None):
        """

        :param select_field: count(id) or else
        :param where: 查询条件
        :param args: 参数
        :return: count(id) or else
        """
        sql = ['select %s as _num_ from %s' % (select_field, cls.__table__)]
        if where:
            sql.append(where)
        rs = yield from select(' '.join(sql), args, 1)
        if len(rs) == 0:
            return None
        return rs[0]['_num_']  # [{'_num_': int }]

    @asyncio.coroutine
    def save_one_blog(self):
        """
        保存博客
        :param self
        :return: rows
        """
        logging.info(
            "method -> save_one_blog() ,fields[] -> %s , primaryKey -> %s  " % (self.__fields__, self.__primary_key__))
        args = list(map(self.get_value_or_default, self.__fields__))  # 获取传入值或者默认值
        args.append(self.get_value_or_default(self.__primary_key__))  # 生成主键值
        rows = yield from execute(self.__insert__, args)
        if rows != 1:
            logging.warning('failed to insert record: affected rows: %s' % rows)
        return rows

    @classmethod
    @asyncio.coroutine
    def find_blog(cls, args):
        """
        根据主键找到博客
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
    def delete_blog(cls, args):
        """
        根据主键删除博客
        :param args: cls:传递当前类对象; args:id
        :return:
        """
        rs = yield from execute(cls.__delete__, args)
        if rs != 1:
            logging.warning('failed to delete record: affected rows: %s' % rs)

    @asyncio.coroutine
    def update_blog(self):
        """
        根据主键更新博客
        :param self
        :return: rows
        """
        logging.info(
            "method -> update_blog() ,fields[] -> %s , primaryKey -> %s  " % (self.__fields__, self.__primary_key__))
        args = list(map(self.get_value_or_default, self.__fields__))
        args.append(self.get_value_or_default(self.__primary_key__))
        rows = yield from execute(self.__update__, args)
        if rows != 1:
            logging.warning('failed to insert record: affected rows: %s' % rows)
        return rows


