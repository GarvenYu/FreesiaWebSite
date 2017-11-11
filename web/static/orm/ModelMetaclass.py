#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging; logging.basicConfig(level=logging.INFO)
from web.static.orm.Field import Field


class ModelMetaclass(type):
    # 元类必须实现__new__方法，当一个类指定通过某元类来创建，那么就会调用该元类的__new__方法
    # 该方法接收4个参数
    # cls为当前准备创建的类的对象
    # name为类的名字，创建User类，则name便是User
    # bases类继承的父类集合,创建User类，则base便是Model
    # attrs为类的属性/方法集合，创建User类，则attrs便是一个包含User类属性的dict
    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        # 取出表名
        table_name = attrs.get('__table__', None) or name
        logging.info('found model:%s (table:%s)' % (name, table_name))
        # 保存属性和列的映射关系
        mappings = dict()
        # 除主键外的属性名
        fields = []
        primary_key_temp = None
        # 注意这里attrs的key是字段名，value是字段实例，不是字段的具体值
        # 比如User类的id=StringField(...) 这个value就是这个StringField的一个实例，而不是实例化
        # 的时候传进去的具体id值
        for k,v in attrs.items():
            # attrs同时还会拿到一些其它系统提供的类属性，我们只处理自定义的类属性，所以判断一下
            # isinstance 方法用于判断v是否是一个Field
            if isinstance(v, Field):
                mappings[k] = v
                if v.primary_key:
                    if primary_key_temp:  # 如果此时变量不为空说明之前出现了主键
                        raise RuntimeError("Duplicate primary key for Field :%s" % k)
                    primary_key_temp = k  # 否则存储主键
                else:
                    fields.append(k)
        if not primary_key_temp:
            raise RuntimeError("Primary key not found")
        for key in mappings.keys():
            attrs.pop(key)
        escaped_fields = list(map(str, fields))
        logging.info("escaped_fields - > %s" % str(escaped_fields))
        attrs['__mappings__'] = mappings  # 保存属性和列的映射关系
        attrs['__table__'] = table_name
        attrs['__primary_key__'] = primary_key_temp  # 主键属性名
        attrs['__fields__'] = fields  # 除主键外的属性名
        # 构造默认的SELECT, INSERT, UPDATE和DELETE语句:
        attrs['__select__'] = 'select %s, %s from %s' % (primary_key_temp, ', '.join(escaped_fields), table_name)
        attrs['__insert__'] = 'insert into %s (%s, %s) values (%s)' % (
            table_name, ', '.join(escaped_fields), primary_key_temp,
            ModelMetaclass.create_args_string(len(escaped_fields) + 1))
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (
            table_name, ', '.join(map(lambda f: '%s=?' % (mappings.get(f).name or f), fields)), primary_key_temp)
        attrs['__delete__'] = 'delete from %s where %s=?' % (table_name, primary_key_temp)
        return type.__new__(cls, name, bases, attrs)

    @staticmethod
    def create_args_string(number):
        mist = []
        for n in range(number):
            mist.append('?')
        return ','.join(mist)