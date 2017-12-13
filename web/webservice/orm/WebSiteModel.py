#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import time, uuid
from web.webservice.orm.Model import Model
from web.webservice.orm.Field import StringField, BooleanField, IntField, TextField, FloatField


def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)


class User(Model):
    __table__ = 'users'

    id = StringField(column_type='varchar(50)', primary_key=True, default=next_id())
    email = StringField(column_type='varchar(50)')
    passwd = StringField(column_type='varchar(50)')
    admin = BooleanField()
    name = StringField(column_type='varchar(50)')
    image = StringField(column_type='varchar(500)')
    created_at = FloatField(default=time.time())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Blog(Model):
    __table__ = 'blogs'

    id = StringField(column_type='varchar(50)', primary_key=True, default=next_id())
    user_id = StringField(column_type='varchar(50)')
    user_name = StringField(column_type='varchar(50)')
    user_image = StringField(column_type='varchar(500)')
    title = StringField(column_type='varchar(50)')
    summary = StringField(column_type='varchar(200)')
    content = TextField()
    created_at = FloatField(default=time.time())


class Comment(Model):
    __table__ = 'comments'

    id = StringField(column_type='varchar(50)', primary_key=True, default=next_id())
    blog_id = StringField(column_type='varchar(50)')
    user_id = StringField(column_type='varchar(50)')
    user_name = StringField(column_type='varchar(50)')
    user_image = StringField(column_type='varchar(500)')
    content = TextField()
    created_at = FloatField(default=time.time())


class Page(object):
    def __init__(self, item_count, page_index=1, page_size=5):
        self.item_count = item_count  # 总记录数
        self.page_size = page_size  # 一页显示记录数
        self.page_count = item_count // page_size + (1 if item_count % page_size > 0 else 0)  # 总页数
        if (item_count == 0) or (page_index > self.page_count):
            self.offset = 0
            self.limit = 0
            self.page_index = 1
        else:
            self.page_index = page_index
            self.offset = self.page_size * (page_index - 1)
            self.limit = self.page_size
        self.has_next = self.page_index < self.page_count
        self.has_previous = self.page_index > 1

    def __str__(self):
        return 'item_count: %s, page_count: %s, page_index: %s, page_size: %s, offset: %s, limit: %s' % \
               (self.item_count, self.page_count, self.page_index, self.page_size, self.offset, self.limit)

    __repr__ = __str__
