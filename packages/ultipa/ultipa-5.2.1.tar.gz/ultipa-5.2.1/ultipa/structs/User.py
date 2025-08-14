# -*- coding: utf-8 -*-
# @Time    : 2024/05/14 11:47
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : User.py
from datetime import datetime
from typing import List, Dict

from ultipa.structs.BaseModel import BaseModel
from ultipa.structs.PropertyPrivilege import PropertyPrivilege


class User(BaseModel):
    '''
        Data class for User.
    '''

    def __init__(self,
                 username: str = None,
                 password: str = None,
                 createdTime: datetime = None,
                 graphPrivileges: Dict[str, List[str]] = None,
                 systemPrivileges: List[str] = None,
                 propertyPrivileges: PropertyPrivilege = None,
                 policies: List[str] = None
                 ):
        self.username = username
        self.password = password
        self.createdTime = createdTime
        self.graphPrivileges = graphPrivileges
        self.systemPrivileges = systemPrivileges
        self.policies = policies
        self.propertyPrivileges = propertyPrivileges
