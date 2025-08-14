# -*- coding: utf-8 -*-
from dateutil.parser import parse


def is_valid_date(strdate):
    '''
        Judge whether a string is a valid data or time.
    '''
    try:
        dt = parse(strdate)
    except Exception as e:
        return False
