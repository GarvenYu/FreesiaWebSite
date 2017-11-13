#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import functools

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