# -*- coding: utf-8 -*-
# @Time    : 2023/8/4 16:39
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : ResultType.py
from enum import Enum

from ultipa.proto import ultipa_pb2
from ultipa.structs.PropertyType import UltipaPropertyType


class ResultType(Enum):
    '''
        Data class for returned result type.
    '''
    RESULT_TYPE_UNSET = ultipa_pb2.RESULT_TYPE_UNSET
    RESULT_TYPE_PATH = ultipa_pb2.RESULT_TYPE_PATH
    RESULT_TYPE_NODE = ultipa_pb2.RESULT_TYPE_NODE
    RESULT_TYPE_EDGE = ultipa_pb2.RESULT_TYPE_EDGE
    RESULT_TYPE_ATTR = ultipa_pb2.RESULT_TYPE_ATTR
    # RESULT_TYPE_GRAPH = ultipa_pb2.RESULT_TYPE_GRAPH
    # RESULT_TYPE_ARRAY = ultipa_pb2.RESULT_TYPE_ARRAY
    RESULT_TYPE_TABLE = ultipa_pb2.RESULT_TYPE_TABLE
    RESULT_TYPE_GRAPH = 6
    RESULT_TYPE_ExplainPlan = "ExplainPlan"

    @staticmethod
    def getTypeStr(type):
        if type == ResultType.RESULT_TYPE_PATH or type == ResultType.RESULT_TYPE_PATH.value:
            return ResultType.RESULT_TYPE_PATH
        elif type == ResultType.RESULT_TYPE_NODE or type == ResultType.RESULT_TYPE_NODE.value:
            return ResultType.RESULT_TYPE_NODE
        elif type == ResultType.RESULT_TYPE_EDGE or type == ResultType.RESULT_TYPE_EDGE.value:
            return ResultType.RESULT_TYPE_EDGE
        elif type == ResultType.RESULT_TYPE_ATTR or type == ResultType.RESULT_TYPE_ATTR.value:
            return ResultType.RESULT_TYPE_ATTR
        elif type == UltipaPropertyType.LIST or type == UltipaPropertyType.LIST.value:
            return ResultType.RESULT_TYPE_ATTR
        elif type == ResultType.RESULT_TYPE_TABLE or type == ResultType.RESULT_TYPE_TABLE.value:
            return ResultType.RESULT_TYPE_TABLE
        elif type == ResultType.RESULT_TYPE_UNSET or type == ResultType.RESULT_TYPE_UNSET.value:
            return ResultType.RESULT_TYPE_UNSET
        elif type == ResultType.RESULT_TYPE_GRAPH or type == ResultType.RESULT_TYPE_GRAPH.value:
            return ResultType.RESULT_TYPE_GRAPH
        elif type == ResultType.RESULT_TYPE_ExplainPlan or type == ResultType.RESULT_TYPE_ExplainPlan.value:
            return ResultType.RESULT_TYPE_ExplainPlan
        else:
            return type
