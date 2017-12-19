from web.webservice.orm.Model import create_pool, destroy_pool
from web.webservice.webframework import init_jinja2, datetime_filter, add_static, add_routes
from web.webservice.handler import COOKIE_NAME, cookie2user
from aiohttp import web
import asyncio
import logging, json


# 添加日志middleware
@web.middleware
async def logger_middleware(request, handler):
    resp = await handler(request)
    logging.info('logger_middleware info is '+str(resp))
    logging.info('Request: %s %s' % (request.method, request.path))
    # await asyncio.sleep(0.3)
    return resp


# 返回response的middleware

async def response_middleware(app, handler):
    async def response(request):
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
            logging.info('response_middleware() resp -> '+str(resp))
            template_page = resp.get('__template__')
            if template_page is None:
                resp_final = web.Response(
                    body=json.dumps(resp, ensure_ascii=False, default=lambda obj: obj.__dict__).encode('utf-8'))
                resp_final.content_type = 'application/json'
                resp_final.charset = 'utf-8'
                return resp_final
            else:
                resp_final = web.Response(
                    body=app['__template__'].get_template(template_page).render(**resp).encode('utf-8'))
                resp_final.content_type = 'text/html'
                resp_final.charset = 'utf-8'
                return resp_final
        if isinstance(resp, int) and 600 > resp >= 100:
            return web.Response(resp)
        if isinstance(resp, tuple) and len(resp) == 2:
            t, m = resp
            if isinstance(t, int) and 600 > t >= 100:
                return web.Response(t, str(m))
        # default:
        resp_final = web.Response(body=str(resp).encode('utf-8'), content_type='text/plain', charset='utf-8')
        return resp_final
    return response


# 解析客户端发送的cookie
@web.middleware
async def cookie_middleware(request, handler):
    logging.info('check cookie: request method is %s, request path is %s' % (request.method, request.path))
    cookie_str = request.cookies.get(COOKIE_NAME)
    if cookie_str:
        user = await cookie2user(cookie_str)
        if user:
            request.__user__ = user
            logging.info('find valid user %s' % user.email)
            if request.path.startswith('/manage') and (request.__user__ is None or not request.__user__.get('admin')):
                return web.HTTPFound('/login')
    return await handler(request)


async def init(loop_param):
    await create_pool(loop, user='root', password='123456', database='freesiawebsite')
    app = web.Application(loop=loop_param, middlewares=[response_middleware, logger_middleware, cookie_middleware])
    init_jinja2(app, filters=dict(datetime=datetime_filter))
    add_routes(app, 'handler')
    # app.router.add_get('/', index)
    add_static(app)
    srv = await loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('server started at http://127.0.0.1:9000...')
    logging.info("connection ok")
    # await destroy_pool()
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
