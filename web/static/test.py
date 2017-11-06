# -*-coding:utf-8-*-
class MyDict(dict):
    name = 'ykb'

    def __init__(self, name):
        super(MyDict, self).__init__(name=name)


d = MyDict(name='ddd')
print(d['name'])
print(MyDict.name)