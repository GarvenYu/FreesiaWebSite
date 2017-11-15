#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import functools
import inspect, asyncio
from aiohttp import web
from urllib import parse
import logging
logging.basicConfig(level=logging.INFO)

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

# 收集没有默认值的命名关键字参数,返回的是参数的名字
def get_named_kwargs_without_default(fn):
    args = []
    params = inspect.signature(fn).parameters
    for name, value in params.items():
        if str(value.kind) == 'KEYWORD_ONLY' and value.default == inspect.Parameter.empty:
            args.append(name)
    return tuple(args)


# 获取命名关键字参数
def get_named_kwargs(fn):
    args = []
    params = inspect.signature(fn).parameters
    logging.info(str(params))
    for name, value in params.items():
        if str(value.kind) == 'KEYWORD_ONLY':
            args.append(name)
    return tuple(args)


# 判断是否有命名关键字参数
def has_named_kwargs(fn):
    params = inspect.signature(fn).parameters
    for name, value in params.items():
        if str(value.kind) == 'KEYWORD_ONLY':
            return True
        else:
            return False


# 判断是否有关键字参数 **kwargs
def has_kwargs(fn):
    params = inspect.signature(fn).parameters
    for name, value in params.items():
        if str(value.kind) == 'VAR_KEYWORD':
            return True
        else:
            return False


# 判断是否有命名关键字参数，该命名关键字参数后面没有别的类型参数，且包含request
def has_request_args_last(fn):
    params = inspect.signature(fn).parameters
    sig = inspect.signature(fn)  # -> (*, request, name)
    flag = False
    for name, value in params.items():
        if name == 'request':
            flag = True
            continue
        if flag and (str(value.kind) != 'VAR_POSITIONAL'
                     and str(value.kind) != 'KEYWORD_ONLY' and str(value.kind != 'VAR_KEYWORD')):
                raise ValueError('request parameter must be the last named parameter in function: %s %s'
                                 % (fn.__name__, str(sig)))
    return flag


# 从request中获取参数给对应的URL处理函数
class RequestHandler(object):
    def __init__(self, app, fn):
        self.__app = app
        self.__fn = fn
        self.__named_kwargs_without_default = get_named_kwargs_without_default(fn)
        self.__named_kwargs = get_named_kwargs(fn)
        self.__has_named_kwargs = has_named_kwargs(fn)
        self.__has_kwargs = has_kwargs(fn)
        self.__has_request_args_last = has_request_args_last(fn)
