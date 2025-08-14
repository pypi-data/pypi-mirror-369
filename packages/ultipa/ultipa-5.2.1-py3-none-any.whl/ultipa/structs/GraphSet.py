# -*- coding: utf-8 -*-
# @Time    : 2023/8/1 10:47
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : Graph.py
from typing import List

from ultipa.structs.BaseModel import BaseModel


class GraphSet(BaseModel):
    '''
            Data class for graphSet.
    '''

    def __init__(self,
                 name: str = None,
                 id: str = None,
                 totalNodes: int = None,
                 totalEdges: int = None,
                 partitionBy: str = None,
                 status: str = None,
                 shards: List[str] = [],
                 description: str = None,
                 slotNum: int = 0,
                 ):
        self.id = id
        self.name = name
        self.totalNodes = totalNodes
        self.totalEdges = totalEdges
        self.shards = shards
        self.partitionBy = partitionBy
        self.status = status
        self.description = description
        self.slotNum = slotNum
