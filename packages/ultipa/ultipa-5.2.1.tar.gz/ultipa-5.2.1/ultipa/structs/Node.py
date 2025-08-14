# -*- coding: utf-8 -*-
# @Time    : 2023/8/4 16:18
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : Node.py
from typing import Dict, List

from ultipa.structs.BaseModel import BaseModel


class Node(BaseModel):
    '''
        Data calss for node.
    '''
    _index = None

    # **kwargs
    def __init__(self,
                 uuid: int = None,
                 id: str = None,
                 schema: str = None,
                 values: Dict[str, any] = None
                 ):
        self.uuid = uuid
        self.id = id
        self.schema = schema
        self.values = values

    def getID(self):
        return self.id

    def getUUID(self):
        return self.uuid

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


class NodeAlias:
    def __init__(self, alias: str, nodes: List[Node] = None):
        self.alias = alias
        if nodes is None:
            nodes = []
        self.nodes = nodes
