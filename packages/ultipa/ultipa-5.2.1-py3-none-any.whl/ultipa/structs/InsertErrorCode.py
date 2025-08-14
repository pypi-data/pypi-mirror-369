from enum import Enum


class InsertErrorCode(Enum):
    ID_NOT_MATCH_UUID = 10001
    ID_UUID_NOT_MATCH_SCHEMA = 10002
    FROM_ID_NOT_EXISTED = 10003
    TO_ID_NOT_EXISTED = 10004
    ID_LEN = 10005
    NOT_NULL = 10006
    UNIQUCHECK = 10007
    ID_EMPTY = 10008
    FROM_ID_EMPTY = 10009
    TO_ID_EMPTY = 10010
    DUPLICATE_ID = 10011
    KEY_CONSTRAINT_VIOLATED = 10012
    INVALID_FORMAT = 10013
    OK_BUT_ID_EXISTED = 11001
    OTHERS = 19999


class InsertErrorCodeMap:
    codeMap = {
        10001: InsertErrorCode.ID_NOT_MATCH_UUID,
        10002: InsertErrorCode.ID_UUID_NOT_MATCH_SCHEMA,
        10003: InsertErrorCode.FROM_ID_NOT_EXISTED,
        10004: InsertErrorCode.TO_ID_NOT_EXISTED,
        10005: InsertErrorCode.ID_LEN,
        10006: InsertErrorCode.NOT_NULL,
        10007: InsertErrorCode.UNIQUCHECK,
        10008: InsertErrorCode.ID_EMPTY,
        10009: InsertErrorCode.FROM_ID_EMPTY,
        10010: InsertErrorCode.TO_ID_EMPTY,
        10011: InsertErrorCode.DUPLICATE_ID,
        10012: InsertErrorCode.KEY_CONSTRAINT_VIOLATED,
        10013: InsertErrorCode.INVALID_FORMAT,
        11001: InsertErrorCode.OK_BUT_ID_EXISTED,
        19999: InsertErrorCode.OTHERS
    }

    @staticmethod
    def getUnsertErrorCode(v):
        return InsertErrorCodeMap.codeMap.get(v)
