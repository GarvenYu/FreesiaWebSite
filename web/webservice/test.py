# -*-coding:utf-8-*-


def func(name, job='engineer', *, city):
    print("name -> %s, city -> %s, job -> %s" % (name, city, job))


if __name__ == '__main__':
    d = {'name': 'ykb', 'city': 'yt', 'job': 'doctor'}
    d2 = dict(name='rtry', age=123)
    func(**d)
    func('qwe', city='yt')
    dict1 = {'name': 123}
    dict2 = dict1
    dict3 = dict(**dict1)
    print(str(dict2)+str(dict3))
    print('d2 -> %s' % d2)