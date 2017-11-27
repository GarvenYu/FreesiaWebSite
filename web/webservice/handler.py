#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from web.webservice.webframework import get, post
from web.webservice.orm.WebSiteModel import User, Blog
import time


@get('/main')
async def index(request):
    users = await User.find_all_user()
    return {
        '__template__': 'blog_list.html',
        'users': users
    }


@get('/bloglist')
async def get_blog_list(request):
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