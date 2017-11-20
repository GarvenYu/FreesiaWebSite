import logging; logging.basicConfig(level=logging.INFO)
import asyncio, os, json, time
from datetime import datetime
from aiohttp import web


def index(request):
    return web.Response(body='<h1>于凯菠是脸红的Freesia</h1>'.encode('utf-8'), content_type='text/html', charset='UTF-8')


def hello(request):
    logging.info(request.match_info)  # MatchInfo {'name': 'ykb'}
    text = '<h1>hello, %s!</h1>' % request.match_info['name']
    return web.Response(body=text.encode('utf-8'), content_type='text/html', charset='UTF-8')


def hello_query_string(request):
    logging.info(request.query_string)  # name=qwer
    # text = '<h1>hello, %s!</h1>' % request.match_info['name']
    # return web.Response(body=text.encode('utf-8'), content_type='text/html', charset='UTF-8')


@asyncio.coroutine
def init(loop_param):
    app = web.Application(loop=loop_param)
    app.router.add_get('/', index, name='route')
    app.router.add_get('/hello/{name}', hello)
    app.router.add_get('/hello2', hello_query_string)
    srv = yield from loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('server started at http://127.0.0.1:9000...')
    return srv


loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
