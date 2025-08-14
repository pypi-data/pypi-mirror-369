# -*- coding: utf-8 -*-
# @Time    : 2023/8/4 10:34
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : DBType.py
from enum import Enum

from ultipa.proto import ultipa_pb2


class DBType(Enum):
    '''
        Data class for data type
    '''
    DBNODE = ultipa_pb2.DBNODE
    DBEDGE = ultipa_pb2.DBEDGE
    DBGLOBAL = ultipa_pb2.DBGLOBAL
