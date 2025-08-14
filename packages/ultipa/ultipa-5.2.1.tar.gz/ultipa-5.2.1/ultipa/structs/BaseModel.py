# -*- coding: utf-8 -*-
# @Time    : 2023/8/4 10:29
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : BaseModel.py
import json
from datetime import datetime
from enum import Enum


class BaseModel:
    '''
        Processing class that defines settings for returned data related operations.
    '''

    def toJSON(self, pretty=False):
        def custom_default(o):
            if isinstance(o, Enum):
                return o.name
            elif isinstance(o, datetime):
                return o.strftime("%Y-%m-%d %H:%M:%S")
            else:
                return o.__dict__

        try:
            if pretty:
                return json.dumps(self, default=lambda o: o.__dict__,
                                  sort_keys=True, indent=4, ensure_ascii=False)
            else:

                return json.dumps(self, default=lambda o: custom_default(o), sort_keys=False, ensure_ascii=False)

        except Exception as e:
            return self

    def toDict(self):
        return json.loads(self.toJSON())

    def __str__(self):
        return str(self.__dict__)
