# -*- coding: utf-8 -*-
# @Time    : 2023/8/4 16:40
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : PropertyType.py
from enum import Enum

from ultipa.proto import ultipa_pb2


class PropertyTypeStr:
    '''
        Data class for property type mapping to string.
    '''
    UNSET = "unset"
    INT32 = 'int32'
    UINT32 = 'uint32'
    INT64 = 'int64'
    UINT64 = 'uint64'
    FLOAT = 'float'
    DOUBLE = 'double'
    STRING = 'string'
    DATETIME = 'datetime'
    TIMESTAMP = 'timestamp'
    TEXT = 'text'
    BLOB = "blob"
    POINT = "point"
    DECIMAL = "decimal"
    LIST = "list"
    SET = "set"
    MAP = "map"
    NULL_ = "null"
    BOOL = "bool"
    LOCAL_DATETIME = "local datetime"
    ZONED_DATETIME = "zoned datetime"
    DATE = "date"
    ZONED_TIME = "zoned time"
    LOCAL_TIME = "local time"
    YEAR_TO_MONTH = "duration(year to month)"
    DAY_TO_SECOND = "duration(day to second)"
    JSON = "json"


class UltipaPropertyType(Enum):
    '''
        Data class for property type mapping to gRPC.
    '''
    UNSET = ultipa_pb2.UNSET
    INT32 = ultipa_pb2.INT32
    UINT32 = ultipa_pb2.UINT32
    INT64 = ultipa_pb2.INT64
    UINT64 = ultipa_pb2.UINT64
    FLOAT = ultipa_pb2.FLOAT
    DOUBLE = ultipa_pb2.DOUBLE
    STRING = ultipa_pb2.STRING
    DATETIME = ultipa_pb2.DATETIME
    TIMESTAMP = ultipa_pb2.TIMESTAMP
    TEXT = ultipa_pb2.TEXT
    BLOB = ultipa_pb2.BLOB
    POINT = ultipa_pb2.POINT
    DECIMAL = ultipa_pb2.DECIMAL
    LIST = ultipa_pb2.LIST
    SET = ultipa_pb2.SET
    MAP = ultipa_pb2.MAP
    NULL = ultipa_pb2.NULL_
    BOOL = ultipa_pb2.BOOL
    LOCAL_DATETIME = ultipa_pb2.LOCAL_DATETIME
    ZONED_DATETIME = ultipa_pb2.ZONED_DATETIME
    DATE = ultipa_pb2.DATE
    ZONED_TIME = ultipa_pb2.ZONED_TIME
    LOCAL_TIME = ultipa_pb2.LOCAL_TIME
    YEAR_TO_MONTH = ultipa_pb2.YEAR_TO_MONTH
    DAY_TO_SECOND = ultipa_pb2.DAY_TO_SECOND
    JSON = ultipa_pb2.JSON
    ID = -1
    UUID = -2
    FROM = -3
    TO = -4
    FROM_UUID = -5
    TO_UUID = -6
    IGNORE = -7
