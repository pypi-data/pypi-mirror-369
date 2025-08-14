# -*- coding: utf-8 -*-
# @Time    : 2023/8/4 18:15
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : InsertType.py
from enum import Enum

from ultipa.proto import ultipa_pb2


class InsertType(Enum):
    '''
        Data class for insert type.
    '''
    NORMAL = ultipa_pb2.NORMAL
    OVERWRITE = ultipa_pb2.OVERWRITE
    UPSERT = ultipa_pb2.UPSERT
