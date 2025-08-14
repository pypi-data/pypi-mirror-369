# -*- coding: utf-8 -*-
# @Time    : 2024/05/14 11:47
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : Index.py
from ultipa.structs import DBType
from ultipa.structs.BaseModel import BaseModel


class Index(BaseModel):
    '''
        Data class for Index.
    '''

    def __init__(self,
                 name: str = None,
                 properties: str = None,
                 schema: str = None,
                 status: str = None,
                 size: str = None,
                 id: str = None,
                 dbType: DBType = None
                 ):
        self.id = id
        self.name = name
        self.properties = properties
        self.schema = schema
        self.status = status
        self.size = size
        self.dbType = dbType
