# -*- coding: utf-8 -*-
# @Time    : 2023/8/4 16:36
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : Algo.py
from typing import List

from ultipa.structs.BaseModel import BaseModel


class AlgoParam:
    name: str
    desc: str


class Algo(BaseModel):
    '''
        Data class for algorithm.
    '''

    def __init__(self,
                 name: str = None,
                 type: str = None,
                 writeSupportType: str = None,
                 canRollback: str = None,
                 configContext: str = None,
                 version: str = None,
                 params: List[AlgoParam] = None,
                 description: str = None
                 ):
        self.name = name
        self.type = type
        self.writeSupportType = writeSupportType
        self.canRollback = canRollback
        self.configContext = configContext
        self.version = version
        self.params = params
        self.description = description


class AlgoResultOpt(BaseModel):
    can_realtime: bool
    can_visualization: bool
    can_write_back: bool
