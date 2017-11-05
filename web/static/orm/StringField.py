# varchar类型

from web.static.orm import Field


class StringField(Field):
    def __init__(self, name=None, column_type='varchar(100)', primary_key=False, default=None):
        super(StringField, self).__init__(name, column_type, primary_key, default)
