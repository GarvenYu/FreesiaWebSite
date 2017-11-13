#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from web.webservice.orm.WebSiteModel import User
from web.webservice.orm.Model import create_pool, destroy_pool
import asyncio
import logging


def test(loop):
    yield from create_pool(loop, user='root', password='123456', database='freesiawebsite')
    logging.info("connection ok")
    u = User(id=None, name='Test', email='qwe@example.com', passwd='1234567890',
             image='about:blank', admin=None, created_at=None)

    yield from u.save_one_user()
    yield from destroy_pool()


_loop = asyncio.get_event_loop()
_loop.run_until_complete(test(_loop))
_loop.close()