#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from web.webservice.webframework import get, post
from web.webservice.orm.WebSiteModel import User, Blog
from web.webservice.apierror import APIValueError,APIPermissionError,APIResourceNotFoundError
import time


@get('/main')
async def index():
    users = await User.find_all_user()
    return {
        '__template__': 'blog_list.html',
        'users': users
    }


@get('/blog/blogList')
async def get_blog_list():
    summary = 'catch me if you can'
    blogs = [
        Blog(id='1', name='Test Blog', summary=summary, created_at=time.time() - 120),
        Blog(id='2', name='Something New', summary=summary, created_at=time.time() - 3600),
        Blog(id='3', name='Learn Swift', summary=summary, created_at=time.time() - 7200),
        Blog(id='4', name='Learn Python', summary=summary, created_at=time.time() - 10000),
        Blog(id='5', name='Learn Java', summary=summary, created_at=time.time() - 20000)
    ]
    return {
        '__template__': 'blog_list.html',
        'blogs': blogs
    }


@get('/blog/writeBlog')
def write_blog():
    return dict(__template__='write_blog.html', id='', action='/api/saveBlog')


@get('/api/users')
async def get_users():
    users = await User.find_all_user(orderBy=('created_at',))
    return dict(users=users)  # [user1, user2, ...]


@post('/api/saveBlog')
def save_blog(request, *, title, summary, content):
    # 检查是否是管理员身份 后续更新
    if title is None or title.strip() is None:
        raise APIValueError('title field', 'blog title can`t be None.')
    if summary is None or summary.strip() is None:
        raise APIValueError('summary field', 'blog summary can`t be None.')
    if content is None or content.strip() is None:
        raise APIValueError('content field', 'blog content can`t be None.')
    pass
