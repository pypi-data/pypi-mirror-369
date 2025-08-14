# -*- coding: utf-8 -*-
# @Time    : 2023/8/4 16:19
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : Edge.py
from typing import Dict

from ultipa.structs.BaseModel import BaseModel


class Edge(BaseModel):
    '''
        Data class for edge.
    '''
    _index = None

    def __init__(self,
                 uuid: int = None,
                 fromId: str = None,
                 toId: str = None,
                 fromUuid: int = None,
                 toUuid: int = None,
                 schema: str = None,
                 values: Dict[str, any] = None):
        self.schema = schema
        self.uuid = uuid
        self.fromId = fromId
        self.toId = toId
        self.fromUuid = fromUuid
        self.toUuid = toUuid
        self.values = values

    def getFrom(self):
        return self.fromId

    def getTo(self):
        return self.toId

    def getFromUUID(self):
        return self.fromUuid

    def getUUID(self):
        return self.uuid

    def getToUUID(self):
        return self.toUuid

    def getValues(self):
        return self.values

    def getSchema(self):
        return self.schema

    def get(self, propName: str):
        return self.values.get(propName)

    def set(self, propName: str, value):
        self.values.update({propName: value})

    def _getIndex(self):
        return self._index
