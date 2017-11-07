# -*-coding:utf-8-*-
import logging; logging.basicConfig(level=logging.INFO)
from web.static.orm import ModelMetaclass


class Model(dict, metaclass=ModelMetaclass):
    def __init__(self, **kwargs):
        super(Model, self).__init__(**kwargs)

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(r"Model has no attribute (%s)" % item)

    def __setattr__(self, key, value):
        self[key] = value

    def get_value(self, key):
        return getattr(self, key, None)

    def get_value_or_default(self, key):
        value = getattr(self, key)
        if value is None:
            field_value = self.__mappings__[key]
            if field_value.default is not None:
                logging.info("find default value (key:%s) = (val:%s)" % (key, field_value))
                setattr(self, key, field_value)
        return field_value
