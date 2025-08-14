# -*- coding: utf-8 -*-
# @Time    : 2023/8/1 10:46
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : requestConfig.py
from ultipa.utils.noneCheck import checkTimeZoneOffset


class RequestConfig:
    '''
    Configuration class for the interface of any non-insert operation.

    This class provides settings for all the operations other than inserting metadata.
    
    Args:
        - graph (str):Name of the graph to use. If not specified, the graph defined in UltipaConfig.defaultGraph will be used.
        - timeout (int): Request timeout threshold (in second).
        - host (str): Specifies a host in a database cluster to execute the request.
        - thread (int): Number of threads for the request.
        - timezone (str): Name of the timezone, e.g., Europe/Paris. Defaults to the local timezone if not specified.
        - timezoneOffset (any): The offset from UTC (in hour), e.g., +2, -3.5. When both timezone and timezoneOffset are provided, timezoneOffset takes precedence.
    '''

    def __init__(self,
                 graph: str = '',
                 timeout: int = None,
                 host: str = None,
                 thread: int = None,
                 timezone: str = None,
                 timezoneOffset: str = None):
        self.graph = graph
        self.timeout = timeout
        self.host = host
        self.thread = thread
        self.timezone = timezone
        self.timezoneOffset = timezoneOffset
        if not checkTimeZoneOffset(timezoneOffset):
            raise ValueError('timezoneOffset: Not a valid ±(hh):(mm) format')
