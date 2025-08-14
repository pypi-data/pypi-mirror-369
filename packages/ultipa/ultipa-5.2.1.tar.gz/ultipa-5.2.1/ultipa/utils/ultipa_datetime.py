import datetime
import math
import re
import time

from dateutil.parser import parse

from ultipa.utils import errors
from ultipa.utils.errors import ParameterException, SerializeException

YEAR_OFFSET = 16384


class UTC(datetime.tzinfo):
    def __init__(self, offset_hours=0, offset_seconds=0):
        if offset_seconds is None:
            self.__offset = 0
        else:
            self.__offset = offset_seconds
        self.__offsetHour = offset_hours

    def utcoffset(self, dt):
        return datetime.timedelta(seconds=self.__offset, hours=self.__offsetHour)

    def tzname(self, dt):
        return 'UTC+%s dt: %s' % (self.__offsetHour, [dt, id(dt)])

    def dst(self, dt):
        return datetime.timedelta(seconds=self.__offset, hours=self.__offsetHour)


class UltipaDatetime:
    '''
    Processing class for date and time related operations.
    '''
    year = 0
    month = 0
    day = 0
    hour = 0
    minute = 0
    second = 0
    microsecond = 0
    nanosecond = 0

    @classmethod
    def datetimeStr2datetimeInt(self, str_datetime: datetime.datetime):
        '''
        Convert a datetime string into a customized datetime integer.

        Args:
            str_datetime:

        Returns:

        '''

        if isinstance(str_datetime, str):
            try:
                data = datetime.datetime.strptime(str_datetime, "%Y-%m-%d %H:%M:%S.%f%z")
            except:
                try:
                    data = datetime.datetime.strptime(str_datetime, "%Y-%m-%d %H:%M:%S.%f")
                except ValueError as e:
                    try:
                        data = datetime.datetime.strptime(str_datetime, "%Y-%m-%d %H:%M:%S")
                    except ValueError as e:
                        try:
                            data = datetime.datetime.strptime(str_datetime, "%Y-%m-%d")
                        except ValueError as e:
                            raise ParameterException(e)

        elif isinstance(str_datetime, datetime.datetime):
            data = str_datetime
        else:
            raise ParameterException('strDatetime must str %Y-%m-%d %H:%M:%S.%f or datetime type')
        self.year = data.year
        self.month = data.month
        self.day = data.day
        self.hour = data.hour
        self.minute = data.minute
        self.second = data.second
        self.microsecond = data.microsecond

        if self.year >= 70 and self.year < 100:
            self.year += 1900
        elif self.year < 70:
            self.year += 2000

        datetime_int = 0
        year_month = self.year * 13 + self.month
        datetime_int |= (year_month << 46)
        datetime_int |= (self.day << 41)
        datetime_int |= (self.hour << 36)
        datetime_int |= (self.minute << 30)
        datetime_int |= (self.second << 24)
        datetime_int |= self.microsecond
        return datetime_int

    @classmethod
    def timestampStr2timestampInt(self, str_datetime: str, timezone, timezone_offset=0):
        '''
        Convert strings of datetime, timezone and timezone-offset into the Unix timestamp integer in seconds.

        Args:
            str_datetime:
            timezone:
            timezone_offset:

        Returns:

        '''

        try:
            tzinfo = None
            dt = parse(str_datetime)
            if dt.utcoffset() is not None:
                offset_hours = int(dt.utcoffset().total_seconds() / 3600)
                tzinfo = UTC(offset_hours, timezone_offset)

            if timezone is not None:
                total_seconds = getTimeZoneSeconds(timezone)
                tzinfo = UTC(0, total_seconds)
            else:
                if timezone_offset is not None:
                    total_seconds = getTimeOffsetSeconds(timezone_offset)
                    tzinfo = UTC(0, total_seconds)

            timestamp = datetime.datetime(year=dt.year, month=dt.month, day=dt.day, hour=dt.hour, minute=dt.minute,
                                          second=dt.second, tzinfo=tzinfo)
            return int(timestamp.timestamp())
        except ValueError as e:
            raise ParameterException(e)

    @classmethod
    def dateStr2datetimeInt(self, str_date: str):
        '''
        Convert a date string into a customized datetime integer.

        Args:
            str_date:

        Returns:

        '''

        pattern = re.compile(r'^(-?\d{4})-?(\d{2})-?(\d{2})$')
        match = pattern.fullmatch(str_date)
        if not match:
            raise SerializeException(f"Invalid date format: {str_date}, str_date must be str %Y-%m-%d or date type")

        year, month, day = match.groups()

        self.year = int(year)
        self.month = int(month)
        self.day = int(day)

        datetime_int = (self.year + YEAR_OFFSET) << 9
        datetime_int |= ((self.month & 0x0F) << 5)
        datetime_int |= (self.day & 0x1F)
        return datetime_int

    @classmethod
    def timeStr2datetimeInt(self, str_time: str):
        '''
        Convert a time string into a customized datetime integer.

        Args:
            str_time:

        Returns:

        '''

        pattern = re.compile(
            r'^(?P<hour>\d{2}):?(?P<minute>\d{2}):?(?P<second>\d{2})'
            r'(?:\.(?P<nanosecond>\d{1,9}))?'
            r'(?P<tz>([+-]\d{2}:?\d{2})?)$'
        )

        match = pattern.fullmatch(str_time)
        if not match:
            raise SerializeException(f"Invalid time format: {str_time}")

        groups = match.groupdict()
        self.hour = int(groups['hour'])
        self.minute = int(groups['minute'])
        self.second = int(groups['second'])
        nanosecond_str = groups['nanosecond'] or '0'
        self.nanosecond = int(nanosecond_str.ljust(9, '0')[:9])

        tz_quarters = 0
        if groups['tz']:
            tz_str = groups['tz'].replace(':', '')
            tz_hours = int(tz_str[1:3])
            tz_minutes = int(tz_str[3:5]) if len(tz_str) > 3 else 0
            tz_sign = -1 if tz_str[0] == '-' else 1
            tz_offset = tz_sign * (tz_hours * 60 + tz_minutes)
            tz_quarters = tz_offset // 15

        datetime_int = (self.hour & 0x1F) << 59
        datetime_int |= (self.minute & 0x3F) << 53
        datetime_int |= (self.second & 0x3F) << 47
        datetime_int |= (tz_quarters & 0x7F) << 40
        datetime_int |= (self.nanosecond & 0x3FFFFFFF)
        return datetime_int

    @classmethod
    def datetimelzStr2datetimeInt(self, str_datetime: str):
        '''
        Convert a local_datetime or zoned_datetime string into a customized datetime integer.

        Args:
            str_datetime:

        Returns:

        '''

        parts = re.split(r'[ T]', str_datetime, maxsplit=1)
        if len(parts) != 2:
            raise SerializeException(f"Invalid datetime format: {str_datetime}")
        str_date = parts[0]
        str_time = parts[1]

        date_pattern = re.compile(r'^(-?\d{4})-?(\d{2})-?(\d{2})$')
        date_match = date_pattern.fullmatch(str_date)
        if not date_match:
            raise SerializeException(f"Invalid date part format for datetime: {str_datetime}")

        year, month, day = date_match.groups()
        self.year = int(year)
        self.month = int(month)
        self.day = int(day)
        date_int = (self.year + YEAR_OFFSET) << 9
        date_int |= ((self.month & 0x0F) << 5)
        date_int |= (self.day & 0x1F)

        times_pattern = re.compile(
            r'^(?P<hour>\d{2}):?(?P<minute>\d{2}):?(?P<second>\d{2})'
            r'(?:\.(?P<nanosecond>\d{1,9}))?'
            r'(?P<tz>([+-]\d{2}:?\d{2})?)$'
        )
        time_match = times_pattern.fullmatch(str_time)
        if not time_match:
            raise SerializeException(f"Invalid time part format for datetime: {str_datetime}")

        time_groups = time_match.groupdict()
        self.hour = int(time_groups['hour'])
        self.minute = int(time_groups['minute'])
        self.second = int(time_groups['second'])
        nanosecond_str = time_groups['nanosecond'] or '0'
        self.nanosecond = int(nanosecond_str.ljust(9, '0')[:9])

        tz_quarters = 0
        if time_groups['tz']:
            tz_str = time_groups['tz'].replace(':', '')
            tz_hours = int(tz_str[1:3])
            tz_minutes = int(tz_str[3:5]) if len(tz_str) > 3 else 0
            tz_sign = -1 if tz_str[0] == '-' else 1
            tz_offset = tz_sign * (tz_hours * 60 + tz_minutes)
            tz_quarters = tz_offset // 15

        time_int = (self.hour & 0x1F) << 59
        time_int |= (self.minute & 0x3F) << 53
        time_int |= (self.second & 0x3F) << 47
        time_int |= (tz_quarters & 0x7F) << 40
        time_int |= (self.nanosecond & 0x3FFFFFFF)
        return date_int, time_int

    @classmethod
    def durationymStr2datetimeInt(self, str_datetime: str):
        '''
        Convert a duration(year to month) string into a customized datetime integer.

        Args:
            str_datetime:

        Returns:

        '''

        pattern = r'^(-?)P(?:(\d{1,9})Y)?(?:(\d{1,2})M)?$'
        match = re.fullmatch(pattern, str_datetime)
        if not match:
            raise SerializeException(f"Invalid duration(year to month) format for datetime: {str_datetime}")

        sign, years, months = match.groups()

        return (int(years) * 12 + int(months)) if not sign else -(int(years) * 12 + int(months))

    @classmethod
    def durationdsStr2datetimeInt(self, str_datetime: str):
        '''
        Convert a duration(day to second) string into a customized datetime integer.

        Args:
            str_datetime:

        Returns:

        '''

        pattern = r'^(-?)P(?:(\d{1,9})D)?(?:T(?:(\d{1,2})H)?(?:(\d{1,2})M)?(?:(\d{1,2})(?:\.(\d{1,9}))?S)?)?$'
        match = re.fullmatch(pattern, str_datetime)
        if not match:
            raise SerializeException(f"Invalid duration(day to second) format for datetime: {str_datetime}")

        sign, days, hours, minutes, seconds, nanoseconds = match.groups()

        duration_int = int(days) * 86400 * 1000000000
        duration_int += int(hours) * 3600 * 1000000000
        duration_int += int(minutes) * 60 * 1000000000
        duration_int += int(seconds) * 60 * 1000000000
        duration_int += int(nanoseconds) * 1000000000

        return duration_int if not sign else -duration_int

    @staticmethod
    def datetimeInt2datetimeStr(datetime_int):
        '''
        Convert the customized datetime integer into a datetime string

        Args:
            datetime_int:

        Returns:

        '''
        if datetime_int < 0:
            return ""
        year_month = ((datetime_int >> 46) & 0x1FFFF)
        year = year_month // 13
        month = year_month % 13
        day = ((datetime_int >> 41) & 0x1F)
        hour = ((datetime_int >> 36) & 0x1F)
        minute = ((datetime_int >> 30) & 0x3F)
        second = ((datetime_int >> 24) & 0x3F)
        microsecond = (datetime_int & 0xFFFFFF)

        def pixString(s, length):
            s = "000000" + str(s)
            return s[len(s) - length:]

        if year == 0:
            return f"{pixString(year, 4)}-{pixString(month, 2)}-{pixString(day, 2)} {pixString(hour, 2)}:{pixString(minute, 2)}:{pixString(second, 2)}.{pixString(microsecond, 2)}"
        if microsecond == 000000:
            ret = datetime.datetime(year, month, day, hour, minute, second)
            ret = ret.strftime("%Y-%m-%d %H:%M:%S")
        else:
            ret = datetime.datetime(year, month, day, hour, minute, second, microsecond)
            ret = ret.strftime("%Y-%m-%d %H:%M:%S.%f")
        return ret

    @staticmethod
    def timestampInt2timestampStr(datetime_int, timezone: str = None, timezone_offset: int = 0):
        timeStamp = float(datetime_int)
        offset_hours = 0
        if timezone:
            total_seconds = getTimeZoneSeconds(timezone)
            offset_hours = int(total_seconds / 3600)
        if timezone_offset is None:
            timezone_offset = 0
        otherStyleTime = datetime.datetime.fromtimestamp(timeStamp, tz=UTC(offset_hours, timezone_offset))
        return str(otherStyleTime)

    @staticmethod
    def datetimeInt2dateStr(datetime_int):
        '''
        Convert the customized datetime integer into a date string

        Args:
            datetime_int:

        Returns:

        '''

        year = ((datetime_int >> 9) & 0x7FFF) - YEAR_OFFSET
        month = (datetime_int >> 5) & 0x0F
        day = datetime_int & 0x1F

        yearStr = f"{year:04d}" if year >= 0 else f"{year:05d}"
        monthStr = f"{month:02d}"
        dayStr = f"{day:02d}"

        ret = f"{yearStr}-{monthStr}-{dayStr}"
        return ret

    @staticmethod
    def datetimeInt2timeStr(datetime_int, is_zoned=False):
        '''
        Convert the customized datetime integer into a time string

        Args:
            datetime_int:
            is_zoned

        Returns:

        '''

        if datetime_int < 0:
            return ""
        hour = (datetime_int >> 59) & 0x1F
        minute = (datetime_int >> 53) & 0x3F
        second = (datetime_int >> 47) & 0x3F
        raw_tz = (datetime_int >> 40) & 0x7F
        tz_quarters = (raw_tz | -0x80) if (raw_tz & 0x40) else raw_tz
        nanosecond = datetime_int & 0x3FFFFFFF

        ret = formatTimeStr(hour, minute, second, nanosecond, tz_quarters, is_zoned)

        return ret

    @staticmethod
    def datetimeInt2datetimelzStr(datetime_date_int, datetime_time_int, is_zoned=False):
        '''
        Convert the customized datetime integer into a local_datetime or zoned_datetime string

        Args:
            datetime_date_int:
            datetime_time_int:
            is_zoned:

        Returns:

        '''

        if datetime_time_int < 0:
            return ""
        year = ((datetime_date_int >> 9) & 0x7FFF) - YEAR_OFFSET
        month = (datetime_date_int >> 5) & 0x0F
        day = datetime_date_int & 0x1F

        yearStr = f"{year:04d}" if year >= 0 else f"{year:05d}"
        monthStr = f"{month:02d}"
        dayStr = f"{day:02d}"

        dateStr = f"{yearStr}-{monthStr}-{dayStr}"

        hour = (datetime_time_int >> 59) & 0x1F
        minute = (datetime_time_int >> 53) & 0x3F
        second = (datetime_time_int >> 47) & 0x3F
        raw_tz = (datetime_time_int >> 40) & 0x7F
        tz_quarters = (raw_tz | -0x80) if (raw_tz & 0x40) else raw_tz
        nanosecond = datetime_time_int & 0x3FFFFFFF

        timeStr = formatTimeStr(hour, minute, second, nanosecond, tz_quarters, is_zoned)
        ret = f"{dateStr} {timeStr}"

        return ret

    @staticmethod
    def datetimeInt2durationymStr(datetime_int):
        '''
        Convert the customized datetime integer into a duration year_to_month string

        Args:
            datetime_int:

        Returns:

        '''

        sign = ""
        if datetime_int < 0:
            datetime_int = - datetime_int
            sign = "-"

        year = math.floor(datetime_int / 12)
        month = datetime_int % 12

        return f"{sign}P{year}Y{month}M" if month > 0 else f"{sign}P{year}Y"

    @staticmethod
    def datetimeInt2durationdsStr(datetime_int):
        '''
        Convert the customized datetime integer into a duration day_to_second string

        Args:
            datetime_int:

        Returns:

        '''

        ret = ""
        if datetime_int < 0:
            datetime_int = -datetime_int
            ret = "-"

        nanoseconds = datetime_int % 1000000000
        datetime_int = int((datetime_int - nanoseconds) / 1000000000)
        seconds = datetime_int % 60
        datetime_int = int((datetime_int - seconds) / 60)
        minutes = datetime_int % 60
        datetime_int = int((datetime_int - minutes) / 60)
        hours = datetime_int % 24
        days = int((datetime_int - hours) / 24)

        ret = f"{ret}P"
        if days > 0:
            ret = f"{ret}{days}D"
        if hours > 0 or minutes > 0 or seconds > 0 or nanoseconds > 0:
            ret = f"{ret}T"
        if hours > 0:
            ret = f"{ret}{hours}H"
        if minutes > 0:
            ret = f"{ret}{minutes}M"
        if seconds > 0 or nanoseconds > 0:
            ret = f"{ret}{seconds}"
            if nanoseconds > 0:
                nanoStr = f"{nanoseconds:09d}".rstrip("0")
                ret = f"{ret}.{nanoStr}"
            ret = f"{ret}S"

        if ret == "P":
            ret = "P0D"

        return ret


class DateTimestamp:
    """
    A class that realizes the mutual conversion of datetime and timestamp.

    """

    def __init__(self, date=None):
        if date is None:
            self.timestamp = int(time.time())
            self.datetime = self._toDatetime(self.timestamp)
        else:
            ### Judge whether the input date is a timestamp ###
            if isinstance(date, int):
                self.timestamp = date
                self.datetime = self._toDatetime(date)
            else:
                self.timestamp = self._toTimestamp(date)
                self.datetime = date

        if self.timestamp == False:
            self.year = self.month = self.day = self.hour = self.minute = self.second = False
        else:
            self._localtime = time.localtime(self.timestamp)  # Parse the tuples from the timestamp
            self.year = self._localtime.tm_year  # Assign year tuple
            self.month = self._localtime.tm_mon  # Assign month tuple
            self.day = self._localtime.tm_mday  # Assign day tuple
            self.hour = self._localtime.tm_hour  # Assign hour tuple
            self.minute = self._localtime.tm_min  # Assign minute tuple
            self.second = self._localtime.tm_sec  # Assign second tuple

    def _toDatetime(self, timestamp):
        """
        Convert timestamp to datetime

        """
        try:
            timeStamp = float(timestamp)
            timeArray = time.localtime(timeStamp)
            return time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        except:
            return False

    def _toTimestamp(self, datetimeString):
        """
        Convert datetime to timestamp

        """
        try:
            return int(time.mktime(time.strptime(datetimeString, "%Y-%m-%d %H:%M:%S")))
        except:
            return False

    def __str__(self):
        return self.datetime


def formatTimeStr(hour, minute, second, nanosecond, tz_quarters, isZoned=False):
    hour_str = f"{hour:02d}"
    minute_str = f"{minute:02d}"
    second_str = f"{second:02d}"
    nanosecond_str = f"{nanosecond:09d}".rstrip("0")

    time_str = f"{hour_str}:{minute_str}:{second_str}.{nanosecond_str}" if nanosecond > 0 else f"{hour_str}:{minute_str}:{second_str}"

    if isZoned:
        tz_total_minutes = tz_quarters * 15
        tz_minutes = abs(tz_total_minutes) % 60
        tz_hours = (abs(tz_total_minutes) - tz_minutes) // 60
        tz_sign = "+" if tz_quarters >= 0 else "-"
        tz_str = f"{tz_sign}{abs(tz_hours):02d}{tz_minutes:02d}"
        ret = f"{time_str}{tz_str}"
    else:
        ret = f"{time_str}"
    return ret


def getTimeZoneSeconds(timezone):
    import pytz
    try:
        tz = pytz.timezone(timezone)
        utc_offset = tz.utcoffset(datetime.datetime.utcnow())
        return utc_offset.total_seconds()
    except pytz.exceptions.UnknownTimeZoneError as e:
        raise errors.ParameterException("UnknownTimeZoneError:" + str(e))


def getTimeOffsetSeconds(timezoneOffset):
    if timezoneOffset is None:
        return timezoneOffset
    if isinstance(timezoneOffset, int):
        return timezoneOffset
    elif isinstance(timezoneOffset, float):
        return timezoneOffset
    elif isinstance(timezoneOffset, str):
        # pattern = re.compile(r"([+-])(\d{2})(\d{2})")
        pattern = re.compile(r'^([+-])(\d{1,2})(?::?(\d{2}))?$')
        match = pattern.match(timezoneOffset)

        if not match:
            raise ValueError(f"Invalid time zone offset format: {timezoneOffset}")

        sign = match.group(1)  # 符号 (+/-)
        hours = int(match.group(2))  # 小时部分
        minutes = int(match.group(3)) if match.group(3) else 0  # 分钟部分（可选）

        # 验证小时和分钟范围
        if hours < 0 or hours > 23:
            raise ValueError(f"Hour part exceeds the range: {hours}")
        if minutes < 0 or minutes > 59:
            raise ValueError(f"The minute part is out of range: {minutes}")

        # 计算总偏移分钟数
        total_offset_minutes = (hours * 60 + minutes) * (-1 if sign == '-' else 1)
        offset = datetime.timedelta(minutes=total_offset_minutes)
        return int(offset.total_seconds())

    else:
        raise errors.ParameterException("UnknownTimeZoneOffsetError:" + str(timezoneOffset))


def getTimeZoneOffset(requestConfig, defaultConfig):
    '''
    Get timezone offset

    Args:
        requestConfig:

        defaultConfig:

    Returns:

    '''

    timezone = requestConfig.timezone
    if timezone is not None:
        return getTimeZoneSeconds(timezone)
    timezoneOffset = requestConfig.timezoneOffset
    return getTimeOffsetSeconds(timezoneOffset)


def wrapper(func):
    '''
    Measures the execution time of a method.

    Args:
        func:

    Returns:

    '''

    def inner(*args, **kwargs):
        start_time = time.time()
        res = func(*args, **kwargs)
        end_time = time.time()
        result = end_time - start_time
        print('func %s time is: %.3fs' % (func.__name__, result))
        return res

    return inner
