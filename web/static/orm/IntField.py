# int类型

from web.static.orm import Field


class IntField(Field):
    def __init__(self, name=None, column_type='int', primary_key=False, default=None):
        super(IntField, self).__init__(name, column_type, primary_key, default)