#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from web.webservice.orm.WebSiteModel import User
from web.webservice.orm.Model import create_pool, destroy_pool
import asyncio
import logging


def test(loop):
    yield from create_pool(loop, user='root', password='123456', database='freesiawebsite')
    logging.info("connection ok")
    # u = User(id=None, name='Test', email='qwe@example.com', passwd='1234567890',
    #          image='about:blank', admin=None, created_at=None)
    # yield from u.save_one_user()
    # kw = {'where': {'id': '001510475160004d059c367f9bf4f9fb53042625e040ff7000', 'email': 'test@example.com'}}
    kw = {'orderBy': ('created_at',)}
    user = yield from User.find_one_user_by_email('123@qq.com')
    print(str(user))
    yield from destroy_pool()


_loop = asyncio.get_event_loop()
_loop.run_until_complete(test(_loop))
_loop.close()