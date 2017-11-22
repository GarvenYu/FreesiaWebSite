#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import functools
import inspect, asyncio
from aiohttp import web
from urllib import parse
from web.webservice.apierror import APIError
import os
from jinja2 import Environment, FileSystemLoader
import logging
logging.basicConfig(level=logging.INFO)

# 定义GET/POST方法的装饰器，分别添加__method__属性和__route__属性(因为aiohttp的add_route方法需要请求方式POST/GET和路径信息)
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
# POSITIONAL_ONLY		只能是位置参数
# POSITIONAL_OR_KEYWORD	可以是位置参数也可以是关键字参数
# VAR_POSITIONAL		可变参数相当于是 *args
# KEYWORD_ONLY			命名关键字参数且提供了key，相当于是 *,key
# VAR_KEYWORD			关键字参数相当于是 **kw

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


# 判断request是否为位置参数的最后一个。
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


# 根据request不同的请求方式，抽取请求参数key value put到kw=dict()中，根据URL处理函数所需要的参数与kw进行比较，如果出现
# 必要参数缺失则抛出异常。将封装好的参数集合**kw传入到URL处理函数中进行调用。
class RequestHandler(object):
    def __init__(self, app, fn):
        self.__app = app
        self.__fn = fn
        self.__named_kwargs_without_default = get_named_kwargs_without_default(fn)  # tuple
        self.__named_kwargs = get_named_kwargs(fn)  # tuple
        self.__has_named_kwargs = has_named_kwargs(fn)
        self.__has_kwargs = has_kwargs(fn)  # 有没有关键字参数
        self.__has_request_args_last = has_request_args_last(fn)

    @asyncio.coroutine
    def __call__(self, request):
        kw = None
        # 如果URL处理函数有关键字参数或者命名关键字参数或者带默认值的命名关键字参数
        if self.__has_kwargs or self.__has_named_kwargs or self.__named_kwargs_without_default:
            if request.method == 'POST':  # POST请求可以是json格式的数据，或者是表单字典格式的数据
                if not request.content_type:  # Returns str like 'text/html'
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
            if request.method == 'GET':  # GET请求直接从URL里取参数
                qs = request.query_string  # The query string in the URL, e.g., id=10.Read-only str property.
                if qs:
                    kw = dict()
                    for key, value in parse.parse_qs(qs, keep_blank_values=True).items():
                        # parse_qs 数据以字典形式返回. The dictionary keys are the unique query variable
                        # names and value值是每个key值的list，所以取value[0].
                        # keep_blank_values 为true则在parse时，遇到value为空格就保留空格串
                        kw[key] = value[0]
        if kw is None:  # kw为空说明是通过 /method/{key}访问
            kw = dict(**request.match_info)  # match_info{key:value}
        else:  # 如果从request中获取到了参数
            if not self.__has_kwargs and self.__has_named_kwargs:  # 如果处理函数没有关键字参数，有命名关键字参数
                copy = dict()
                for key, value in kw.items():
                    if key in self.__named_kwargs:
                        copy[key] = kw[key]
                    kw = copy
                # 检查命名关键字参数的参数名是否和match_info中的参数名重复
            for key, value in request.match_info.items():
                if key in kw:
                    logging.warning('Duplicate arg name in named arg and kw args: %s' % key)
                    kw[key] = value
        if self.__has_request_args_last:  # 如果有名为request的参数
            kw['request'] = request
        if self.__named_kwargs_without_default:  # 如果有不含默认值的命名关键字参数
            for key in self.__named_kwargs_without_default:
                if key not in kw:  # 如果构造的参数dict kw里没有必须要有的此参数
                    return web.HTTPBadRequest(reason='Missing argument: %s' % key)
        logging.info('call with args: %s' % str(kw))  # 打印参数dict（从request中获取）
        try:
            result = yield from self.__fn(**kw)
            return result
        except APIError as e:
            return dict(error=e.error, data=e.data, message=e.message)


# 注册URL处理函数
def add_route(app, fn):
    method = getattr(fn, '__method__', None)
    path = getattr(fn, '__route__', None)
    if path is None or method is None:
        raise ValueError('@get or @post not defined in %s.' % str(fn))
    if not asyncio.iscoroutinefunction(fn) or inspect.isgeneratorfunction(fn):  # 如果方法还不是协程
        fn = asyncio.coroutine(fn)
    logging.info(
        'add route method -> %s path -> %s => %s(%s)' %
        (method, path, fn.__name__, ', '.join(inspect.signature(fn).parameters.keys())))
    app.router.add_route(method, path, RequestHandler(app, fn))


# 批量注册URL处理函数
# 动态加载
def add_routes(app, module_name):
    n = module_name.rfind('.')
    if n == -1:  # 传入的模块名是xxx
        out_module = __import__(module_name, globals(), locals())  # 动态加载
        logging.info('globals = %s', globals()['__name__'])
    else:  # 传入的模块名是xxx.py
        out_module = __import__(module_name[:n], globals(), locals())
    for attr in dir(out_module):  # 以list形式返回module所有属性和方法,每个为str
        if attr.startswith('_'):  # 如果是_开头，代表是类变量，不是我们定义的方法
            continue
        fn = getattr(out_module, attr)
        if callable(fn):
            if getattr(fn, '__method__', None) and getattr(fn, '__route__', None):
                add_route(app, fn)  # 防止到add_route方法里检测报错


# 添加静态资源
def add_static(app):
    # os.path.abspath('.') = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(os.path.dirname(os.path.abspath('.')), 'static')  # G:\python_web_site\web\static
    app.router.add_static('/static/', path)
    logging.info('add static %s => %s' % ('/static/', path))


# 添加日志middleware
@web.middleware
async def logger_middleware(request, handler):
    resp = await handler(request)
    # 处理逻辑
    logging.info('request method is %s , path is %s' % (request.method, request.path))
    return resp


# 返回response的middleware
@web.middleware
async def response_middleware(request, handler):
    logging.info('Response Handler...')
    resp = await handler(request)
    if isinstance(resp, web.StreamResponse):
        return resp
    if isinstance(resp, bytes):
        resp_final = web.Response(body=resp, content_type='application/octet-stream')
        return resp_final
    if isinstance(resp, str):
        if resp.startswith('redirect:'):
            return web.HTTPFound(resp[9:])
        resp_final = web.Response(body=resp.encode('utf-8'), content_type='text/html', charset='UTF-8')
        return resp_final
    if isinstance(resp, dict):
        return web.json_response(resp)
    if isinstance(resp, int) and 600 > resp >= 100:
        return web.Response(resp)
    if isinstance(resp, tuple) and len(resp) == 2:
        t, m = resp
        if isinstance(t, int) and 600 > t >= 100:
            return web.Response(t, str(m))
    # default:
    resp_final = web.Response(body=str(resp).encode('utf-8'), content_type='text/plain', charset='utf-8')
    return resp_final


def init_jinja2(app, **kw):
    logging.info('init jinja2...')
    options = dict(
        autoescape=kw.get('autoescape', True),
        block_start_string=kw.get('block_start_string', '{%'),
        block_end_string=kw.get('block_end_string', '%}'),
        variable_start_string=kw.get('variable_start_string', '{{'),
        variable_end_string=kw.get('variable_end_string', '}}'),
        auto_reload=kw.get('auto_reload', True)
    )
    path = kw.get('path', None)
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath('.')), 'templates')
    logging.info('set jinja2 template path: %s' % path)
    env = Environment(loader=FileSystemLoader(path), **options)
    filters = kw.get('filters', None)
    if filters is not None:
        for name, f in filters.items():
            env.filters[name] = f
    app['__templating__'] = env