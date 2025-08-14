# -*- coding: utf-8 -*-
# @Time    : 2024/05/14 11:47
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : Privilege.py
from enum import Enum, auto

from ultipa.structs.BaseModel import BaseModel


class PrivilegeLevel(Enum):
    SYSTEM = auto()
    GRAPH = auto()


class Privilege(BaseModel):
    '''
        Data class for Privilege.
    '''

    def __init__(self, name: str = None, level: PrivilegeLevel = None):
        self.name = name
        self.level = level
