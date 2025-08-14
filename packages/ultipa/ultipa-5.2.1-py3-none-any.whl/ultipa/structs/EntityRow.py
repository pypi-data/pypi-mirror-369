# -*- coding: utf-8 -*-
# @Time    : 2023/8/4 16:21
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : EntityRow.py
from typing import Dict


class EntityRow:
    '''
        Data class for data rows (nodes or edges) to be inserted.
    '''
    _index = None

    def __init__(self, values: Dict,
                 schema: str = None,
                 id: str = None,
                 fromId: str = None, toId: str = None,
                 uuid: int = None, fromUuid: int = None,
                 toUuid: int = None):
        self.uuid = uuid
        self.id = id
        self.fromUuid = fromUuid
        self.toUuid = toUuid
        self.fromId = fromId
        self.toId = toId
        self.schema = schema
        self.values = values

    def _getIndex(self):
        return self._index
