# -*- coding: utf-8 -*-
import datetime

from ultipa.types import ULTIPA
from ultipa.utils.checkStrTime import is_valid_date


class TypeCheck:
    '''
    Check the data type.
    '''

    @staticmethod
    def checkProperty(type, value):
        if type == ULTIPA.UltipaPropertyType.UINT32.value:
            if isinstance(value, int) or value is None:
                return True
            else:
                return "%s row [%s] error: failed to serialize value of property %s [uint32],value=%s"

        if type == ULTIPA.UltipaPropertyType.UINT64.value:
            if isinstance(value, int) or value is None:
                return True
            else:
                return "%s row [%s] error: failed to serialize value of property %s [uint64],value=%s"

        if type == ULTIPA.UltipaPropertyType.INT32.value:
            if isinstance(value, int) or value is None:
                return True
            else:
                return "%s row [%s] error: failed to serialize value of property %s [int32],value=%s"

        if type == ULTIPA.UltipaPropertyType.INT64.value:
            if isinstance(value, int) or value is None:
                return True
            else:
                return "%s row [%s] error: failed to serialize value of property %s [int64],value=%s"

        if type in [ULTIPA.UltipaPropertyType.STRING.value, ULTIPA.UltipaPropertyType.TO.value,
                    ULTIPA.UltipaPropertyType.FROM.value, ULTIPA.UltipaPropertyType.ID.value,
                    ULTIPA.UltipaPropertyType.TEXT.value, ULTIPA.UltipaPropertyType.BLOB.value,
                    ]:
            if isinstance(value, str) or value is None:
                return True
            else:
                return "%s row [%s] error: failed to serialize value of property %s [string],value=%s"

        if type in [ULTIPA.UltipaPropertyType.UUID.value, ULTIPA.UltipaPropertyType.FROM_UUID.value,
                    ULTIPA.UltipaPropertyType.TO_UUID.value]:
            if isinstance(value, int) or value is None:
                return True
            else:
                return "%s row [%s] error: failed to serialize value of property %s [int64],value=%s"

        if type in [ULTIPA.UltipaPropertyType.FLOAT.value]:
            if isinstance(value, float) or value is None:
                return True
            else:
                return "%s row [%s] error: failed to serialize value of property %s [float],value=%s"

        if type in [ULTIPA.UltipaPropertyType.DOUBLE.value]:
            if isinstance(value, float) or value is None:
                return True
            else:
                return "%s row [%s] error: failed to serialize value of property %s [double],value=%s"

        if type == ULTIPA.UltipaPropertyType.DATETIME.value:
            if is_valid_date(value) != False or isinstance(value, datetime.datetime) or value is None:
                return True
            else:
                return "%s row [%s] error: failed to serialize value of property %s [datetime],value=%s"

        if type == ULTIPA.UltipaPropertyType.TIMESTAMP.value:
            if (is_valid_date(value) != False
                    or isinstance(value, datetime.datetime) or isinstance(value,int) or value is None):
                return True
            else:
                return "%s row [%s] error: failed to serialize value of property %s [timestamp],value=%s"

        if type in [ULTIPA.UltipaPropertyType.DATE.value, ULTIPA.UltipaPropertyType.LOCAL_DATETIME.value,
                    ULTIPA.UltipaPropertyType.ZONED_DATETIME.value, ULTIPA.UltipaPropertyType.LOCAL_TIME.value,
                    ULTIPA.UltipaPropertyType.ZONED_TIME.value, ULTIPA.UltipaPropertyType.YEAR_TO_MONTH.value,
                    ULTIPA.UltipaPropertyType.DAY_TO_SECOND.value]:
            if isinstance(value, str) or value is None:
                return True
            else:
                return "%s row [%s] error: failed to serialize value of property %s [date],value=%s"

        return True


if __name__ == '__main__':
    ret = TypeCheck.checkProperty(1, "2019-12-12 15:59:59")
    print(ret)
