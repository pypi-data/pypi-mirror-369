# -*- coding: utf-8 -*-
# @Time    : 2023/1/17 9:45 AM
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : null.py
import sys

from ultipa.types import ULTIPA
from ultipa.utils.errors import SerializeException

Int32Null = bytes([0x7f, 0xff, 0xff, 0xff])
Uint32Null = bytes([0xff, 0xff, 0xff, 0xff])
Int64Null = bytes([0x7f, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff])
Uint64Null = bytes([0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff])
FloatNull = bytes([0xff, 0xff, 0xff, 0xff])
DoubleNull = bytes([0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff])
StringNull = bytes([0x00])
DatetimeNull = bytes([0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff])
TimestampNull = bytes([0xff, 0xff, 0xff, 0xff])
TextNull = bytes([0x00])
BlobNull = bytes([0x00])
PointNull = bytes([0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff])
DecimalNull = bytes([0x00])
BoolNull = bytes([0x2])
LocalDatetimeNull = bytes([0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff])
ZonedDatetimeNull = bytes([0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff])
DateNull = bytes([0xff, 0xff, 0xff, 0xff])
ZonedTimeNull = bytes([0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff])
LocalTimeNull = bytes([0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff])
YearToMonthNull = bytes([0x7f, 0xff, 0xff, 0xff])
DayToSecondNull = bytes([0x7f, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff])


def nullValue(type: ULTIPA.UltipaPropertyType):
    '''
    Returns the null value corresponding to different data types

    Args:
        type: The data type

    Returns:

    '''
    if type == ULTIPA.UltipaPropertyType.STRING.value:
        return StringNull
    elif type == ULTIPA.UltipaPropertyType.INT32.value:
        return Int32Null
    elif type == ULTIPA.UltipaPropertyType.UINT32.value:
        return Uint32Null
    elif type == ULTIPA.UltipaPropertyType.INT64.value:
        return Int64Null
    elif type == ULTIPA.UltipaPropertyType.UINT64.value:
        return Uint64Null
    elif type == ULTIPA.UltipaPropertyType.FLOAT.value:
        return FloatNull
    elif type == ULTIPA.UltipaPropertyType.DOUBLE.value:
        return DoubleNull
    elif type == ULTIPA.UltipaPropertyType.DATETIME.value:
        return Uint64Null
    elif type == ULTIPA.UltipaPropertyType.TIMESTAMP.value:
        return Uint32Null
    elif type == ULTIPA.UltipaPropertyType.TEXT.value:
        return TextNull
    elif type == ULTIPA.UltipaPropertyType.BLOB.value:
        return BlobNull
    elif type == ULTIPA.UltipaPropertyType.POINT.value:
        return PointNull
    elif type == ULTIPA.UltipaPropertyType.DECIMAL.value:
        return DecimalNull
    elif type == ULTIPA.UltipaPropertyType.BOOL.value:
        return BoolNull
    elif type == ULTIPA.UltipaPropertyType.LOCAL_DATETIME.value:
        return LocalDatetimeNull
    elif type == ULTIPA.UltipaPropertyType.ZONED_DATETIME.value:
        return ZonedDatetimeNull
    elif type == ULTIPA.UltipaPropertyType.DATE.value:
        return DateNull
    elif type == ULTIPA.UltipaPropertyType.ZONED_TIME.value:
        return ZonedTimeNull
    elif type == ULTIPA.UltipaPropertyType.LOCAL_TIME.value:
        return LocalTimeNull
    elif type == ULTIPA.UltipaPropertyType.YEAR_TO_MONTH.value:
        return YearToMonthNull
    elif type == ULTIPA.UltipaPropertyType.DAY_TO_SECOND.value:
        return DayToSecondNull
    elif type in [ULTIPA.UltipaPropertyType.LIST.value, ULTIPA.UltipaPropertyType.SET.value,
                  ULTIPA.UltipaPropertyType.MAP.value]:
        return None
    raise SerializeException(f"not support [{ULTIPA.Property._PropertyReverseMap.get(type)}]")


def isNullValue(v: any, type: ULTIPA.UltipaPropertyType):
    '''
    Judge whether a value is null

    Args:
        v: The value to be judged
        type: The property type of v

    Returns:
        bool

    '''
    try:
        nullV = nullValue(type)
        return nullV == v
    except Exception as e:
        raise SerializeException(e)


if __name__ == '__main__':
    print(sys.float_info.max)
    print(sys.int_info)
    print("Ret: ", 0X7FFFFFFF == Int32Null)
    print("Int32Null: ", Int32Null)
    print("Uint32Null: ", Uint32Null)
    print("Int64Null: ", Int64Null)
    print("Uint64Null: ", Uint64Null)
    print("FloatNull: ", FloatNull)
    print("DoubleNull: ", DoubleNull)
    print("StringNull: ", StringNull)
    print("DateTimeNull: ", DatetimeNull)
    print("TimestampNull: ", TimestampNull)
    print("TextNull: ", TextNull)
    print("BlobNull: ", BlobNull)
    print("PointNull: ", PointNull)
    print("DecimalNull: ", DecimalNull)
    print("BoolNull: ", BoolNull)
    print("LocalDatetimeNull: ", LocalDatetimeNull)
    print("ZonedDatetimeNull: ", ZonedDatetimeNull)
    print("DateNull: ", DateNull)
    print("ZonedTimeNull: ", ZonedTimeNull)
    print("LocalTimeNull: ", LocalTimeNull)
    print("YearToMonthNull: ", YearToMonthNull)
    print("DayToSecondNull: ", DayToSecondNull)
