# -*-coding:utf-8-*-

import time, uuid


class MyDict(dict):
    name = 'ykb'

    def __init__(self, name):
        super(MyDict, self).__init__(name=name)


L = []
for n in range(5):
    L.append('?')
print(','.join(L))

d = MyDict(name='ddd')
print(d['name'])
print(MyDict.name)
print("%012d" % 12)
print('%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex))

