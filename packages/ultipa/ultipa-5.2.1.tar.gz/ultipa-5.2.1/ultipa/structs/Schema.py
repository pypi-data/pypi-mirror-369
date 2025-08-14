# -*- coding: utf-8 -*-
# @Time    : 2023/8/1 11:47
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : Schema.py
from typing import List

from ultipa.structs import DBType
from ultipa.structs.BaseModel import BaseModel
from ultipa.structs.Property import Property


class SchemaStat:
    def __init__(self, type: DBType, name: str, fromSchema: str, toSchema: str,
                 count: int):
        self.type = type
        self.name = name
        self.fromSchema = fromSchema
        self.toSchema = toSchema
        self.count = count


class SchemaStats:
    '''
        Data class for SchemaStats.
    '''

    def __init__(self, stats: List[SchemaStat] = None):
        self.stats = stats


class Schema(BaseModel):
    '''
        Data class for schema.
    '''

    def __init__(self,
                 name: str = None,
                 dbType: DBType = None,
                 description: str = None,
                 properties: List[Property] = None,
                 id: int = None,
                 total: int = 0,
                 stats: List[SchemaStat] = None):
        self.name = name
        self.description = description
        self.properties = properties
        self.dbType = dbType
        self.id = id
        self.total = total
        self.stats = stats

    def getProperty(self, name: str):
        find = list(filter(lambda x: x.get('name') == name, self.properties))
        if find:
            return find[0]
        return None
