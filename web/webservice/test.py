# -*-coding:utf-8-*-
import os
import logging
logging.basicConfig(level=logging.INFO)


def func(name, job='engineer', *, city):
    print("name -> %s, city -> %s, job -> %s" % (name, city, job))


def func2(**kw):
    print(kw.items())


def add_static():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    logging.info(os.path.abspath('.'))  # G:\python_web_site\web\webservice
    path2 = os.path.join(os.path.dirname(os.path.abspath('.')), 'static')
    logging.info(os.path.dirname(os.path.abspath(__file__)))  # G:\python_web_site\web\webservice
    # app.router.add_static('/static/', path)
    logging.info('add static %s => %s' % ('/static/', path2))  # => G:\python_web_site\web\webservice\static


if __name__ == '__main__':
    # d = {'name': 'ykb', 'city': 'yt', 'job': 'doctor'}
    # d2 = dict(name='rtry', age=123)
    # func(**d)
    # func('qwe', city='yt')
    # dict1 = {'name': 123}
    # dict2 = dict1
    # dict3 = dict(**dict1)
    # print(str(dict2)+str(dict3))
    # print('d2 -> %s' % d2)
    # add_static()
    func2(name='yyy', age=12)