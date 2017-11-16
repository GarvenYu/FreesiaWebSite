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


# 判断是否有命名关键字参数，它包含了request，该命名关键字参数后面没有别的类型参数。
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


# 提取URL处理函数的特征，与request中获取的参数进行比较，分发处理。
class RequestHandler(object):
    def __init__(self, app, fn):
        self.__app = app
        self.__fn = fn
        self.__named_kwargs_without_default = get_named_kwargs_without_default(fn) # tuple
        self.__named_kwargs = get_named_kwargs(fn) # tuple
        self.__has_named_kwargs = has_named_kwargs(fn)
        self.__has_kwargs = has_kwargs(fn) # 有没有关键字参数
        self.__has_request_args_last = has_request_args_last(fn)

    @asyncio.coroutine
    def __call__(self, request):
        kw = None
        # 如果URL处理函数有关键字参数或者命名关键字参数或者带默认值的命名关键字参数
        if self.__has_kwargs or self.__has_named_kwargs or self.__named_kwargs_without_default:
            if request.method == 'POST':
                if not request.content_type:
                    return web.HTTPBadRequest(reason='Missing Content Type')
                con_typ = request.content_type.lower()
                if con_typ.startswith('application/json'):
                    params = request.json()  # json数据转为dict格式
                    if not isinstance(dict, params):
                        return web.HTTPBadRequest(reason='JSON body must be object.')
                    kw = params
                elif con_typ.startswith('application/x-www-form-urlencoded') or con_typ.startswith('multipart/form-data'):
                    params = request.post()  # Returns MultiDictProxy instance filled with parsed data.
                    kw = dict(**params)
                else:
                    return web.HTTPBadRequest(reason='Unsupported Content-Type: %s' % request.content_type)
            if request.method == 'GET':
                pass

