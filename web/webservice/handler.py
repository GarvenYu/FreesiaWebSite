#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from web.webservice.config_default import configs
from aiohttp import web
from web.webservice.webframework import get, post
from web.webservice.orm.WebSiteModel import User, Blog
from web.webservice.apierror import APIValueError,APIPermissionError,APIResourceNotFoundError
import time, re, hashlib, json
import logging
logging.basicConfig(level=logging.INFO)


@get('/main')
async def index():
    # users = await User.find_all_user()
    return {
        '__template__': 'blog_list.html'
        # 'users': users
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
async def get_users(**kwargs):
    users = await User.find_all_user(kwargs)
    return dict(users=users)  # [user1, user2, ...]


@post('/api/saveBlog')
def save_blog(*, title, summary, content):
    # 检查是否是管理员身份 后续更新
    if title is None or title.strip() == '':
        raise APIValueError('title field', '标题不能为空.')
    if summary is None or summary.strip() == '':
        raise APIValueError('summary field', '摘要不能为空.')
    if content is None or content.strip() == '':
        raise APIValueError('content field', '内容不能为空.')
    blog = Blog(id=None, user_id='001510478227665db0b9bb1767b4aacb66239ff8e2ad1c6000', user_name='Test',
                user_image='about:blank', title=title, summary=summary, content=content, created_at=None)
    yield from blog.save_one_blog()
    return blog


@get('/api/blogs/{id}')
def find_blog(**kw):
    blog = yield from Blog.find_blog(kw.get('id'))
    return blog


_REGEX_EMAIL = re.compile(r'^[0-9a-zA-Z.]+@[0-9a-zA-Z.]+\w+$')
_REGEX_PASSWORD = re.compile(r'^[0-9a-zA-Z]{8,15}$')
_COOKIE_KEY = configs.session.secret
COOKIE_NAME = 'Freesia'


@post('/user/register')
def register_user(*, email, name, passwd):
    if _REGEX_EMAIL.match(email) is None or email.strip() == '':
        raise APIValueError('email field', '邮箱格式不正确.')
    if name is None or name.strip() == '':
        raise APIValueError('name field', '用户名不能为空.')
    if _REGEX_PASSWORD.match(passwd) is None or passwd.strip() == '':
        raise APIValueError('passwd field', '密码格式不正确.')
    # 检查是否已注册
    user = yield from get_users(where={'email': email})
    if len(user) > 0:
        raise APIValueError('email', '邮箱已被注册。')
    # sha1加密密码
    sha1_passwd = '%s:%s' % (email, passwd)
    user = User(id=None, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),
                image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest()
                , admin=None)
    yield from user.save_one_user()
    # 生成cookie:
    r = web.Response()
    # function ——> set_cookie(name, value, *, path='/', expires=None, domain=None,
    #  max_age=None, secure=None, httponly=None, version=None)
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


def user2cookie(user, max_age):
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    # "用户id" + "过期时间" + SHA1("用户id" + "用户口令" + "过期时间" + "SecretKey")
    ls = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(ls)