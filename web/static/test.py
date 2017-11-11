# -*-coding:utf-8-*-
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
print("%s -> `%s`" % ('wer', 'qw'))