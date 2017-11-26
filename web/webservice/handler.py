#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from web.webservice.webframework import get, post
from web.webservice.orm.WebSiteModel import User


@get('/main')
async def index(request):
    users = await User.find_all_user()
    return {
        '__template__': 'blog_list.html',
        'users': users
    }