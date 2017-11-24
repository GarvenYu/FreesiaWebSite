#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from web.webservice.webframework import get, post
import asyncio


@get('/')
async def index(request):
    pass