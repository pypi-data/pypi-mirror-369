# -*- coding: utf-8 -*-
# @Time    : 2023/8/10 14:54
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : Retry.py
class Retry:
    '''
        Processing class that defines settings for retry.
    '''

    def __init__(self, current: int = 0, max: int = 3):
        self.current = current
        self.max = max


class RetryResponse:
    '''
        Processing class that defines settings for retry response.
    '''

    def __init__(self, canRetry, currentRetry, nextRetry):
        self.canRetry = canRetry
        self.currentRetry = currentRetry
        self.nextRetry = nextRetry
