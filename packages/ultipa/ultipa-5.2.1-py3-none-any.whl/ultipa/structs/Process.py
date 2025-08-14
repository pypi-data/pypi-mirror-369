# -*- coding: utf-8 -*-
# @Time    : 2024/05/14 11:47
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : Process.py
from ultipa.structs.BaseModel import BaseModel


class Process(BaseModel):
    '''
        Data class for Index.
    '''

    def __init__(self,
                 processId: str = None,
                 processQuery: str = None,
                 duration: str = None,
                 status: str = None):
        self.processId = processId
        self.processQuery = processQuery
        self.duration = duration
        self.status = status
