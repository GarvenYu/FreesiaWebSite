#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import functools
import inspect, asyncio
from aiohttp import web
from urllib import parse

# 定义GET/POST方法的装饰器，分别添加__method__属性和__route__属性，来标记某个URL处理函数的性质以及路径
# @get('/path') @post('/path')
# 被装饰器修饰的函数func，调用为 get(path)(func)


def get(path):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        # 添加装饰属性
        wrapper.__method__ = 'GET'
        wrapper.__route__ = path
        return wrapper
    return decorator


def post(path):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        # 添加装饰属性
        wrapper.__method__ = 'POST'
        wrapper.__route__ = path
        return wrapper
    return decorator


# 使用inspect模块，来处理映射不同URL的函数的所需参数和request参数的关系

# 收集没有默认值的命名关键字参数
def get_required_kw_args(fn):
    args = []
    params = inspect.signature(fn).parameters
    for name, value in params.items():
        if str(value.kind) == 'KEYWORD_ONLY' and value.default == inspect.Parameter.empty:
            args.append(name)
    return tuple(args)


def test_func(*,name = 'ykb'):
    pass


a = get_required_kw_args(test_func())
print(str(a))