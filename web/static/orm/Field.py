#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class Field(object):
    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.name)


class IntField(Field):
    def __init__(self, name=None, column_type='int', primary_key=False, default=0):
        super(IntField, self).__init__(name, column_type, primary_key, default)


class StringField(Field):
    def __init__(self, name=None, column_type='varchar(100)', primary_key=False, default=None):
        super(StringField, self).__init__(name, column_type, primary_key, default)


class BooleanField(Field):
    def __init__(self, name=None, default=False):
        super(BooleanField, self).__init__(name, 'boolean', False, default)


class TextField(Field):
    def __init__(self, name=None, default=None):
        super(TextField, self).__init__(name, 'text', False, default)


class FloatField(Field):
    def __init__(self, name=None, default=0.0):
        super(FloatField, self).__init__(name, 'real', False, default)