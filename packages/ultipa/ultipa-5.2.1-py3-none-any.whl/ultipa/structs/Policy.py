# -*- coding: utf-8 -*-
# @Time    : 2024/05/14 11:47
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : Policy.py
from typing import List, Dict

from ultipa.structs.BaseModel import BaseModel
from ultipa.structs.PropertyPrivilege import PropertyPrivilege


class Policy(BaseModel):
    '''
        Data class for Policy.
    '''

    def __init__(self, name: str = None,
                 graphPrivileges: Dict[str, List[str]] = None,
                 systemPrivileges: List[str] = None,
                 propertyPrivileges: PropertyPrivilege = None,
                 policies: List[str] = None):
        self.name = name
        self.systemPrivileges = systemPrivileges
        self.graphPrivileges = graphPrivileges
        self.propertyPrivileges = propertyPrivileges
        self.policies = policies
