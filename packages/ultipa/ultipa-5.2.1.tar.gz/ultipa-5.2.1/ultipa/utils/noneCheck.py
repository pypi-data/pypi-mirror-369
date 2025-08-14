import re


def checkNone(data):
    if isinstance(data, list) or isinstance(data, dict):
        if len(data) < 1:
            return True
    value = True if data is None or data == '' else False
    return value


def checkTimeZoneOffset(timezoneOffset):
    if timezoneOffset is None:
        return True
    pattern = r'[+-](0[0-9]|1[0-4])(?::?[0-5]\d)?'
    if re.fullmatch(pattern, timezoneOffset):
        return True
    return False
