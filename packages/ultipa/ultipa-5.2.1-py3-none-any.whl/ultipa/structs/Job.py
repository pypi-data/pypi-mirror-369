# -*- coding: utf-8 -*-
# @Time    : 2024/05/14 11:47
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : Index.py
from typing import Dict

from ultipa.structs.BaseModel import BaseModel


class Job(BaseModel):
    '''
        Data class for Index.
    '''

    def __init__(self, id: str = None,
                 graphName: str = None,
                 type: str = None,
                 query: str = None,
                 status: str = None,
                 errMsg: str = None,
                 result: Dict = {},
                 startTime: str = None,
                 endTime: str = None,
                 progress: str = None):
        self.id = id
        self.graphName = graphName
        self.query = query
        self.type = type
        self.status = status
        self.errMsg = errMsg
        self.result = result
        self.startTime = startTime
        self.endTime = endTime
        self.progress = progress
