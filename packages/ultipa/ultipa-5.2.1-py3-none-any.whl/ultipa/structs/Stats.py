# -*- coding: utf-8 -*-
# @Time    : 2024/05/17 10:56
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : Stats.py
from ultipa.structs.BaseModel import BaseModel


class Stats(BaseModel):
    '''
        Data class for Statistics.
    '''

    def __init__(self, limitedShard: str = '', limitedHdc: str = '', expiredDate: str = '',
                 licenseUUId: str = '', company: str = '', department: str = '', limitedUser: str = '',
                 limitedGraph: str = '', limitedNode: str = '',
                 limitedEdge: str = ''):
        # self.licenseUUId = licenseUUId
        # self.company = company
        # self.department = department
        # self.limitedUser = limitedUser
        # self.limitedGraph = limitedGraph
        # self.limitedNode = limitedNode
        # self.limitedEdge = limitedEdge
        self.limitedShard = limitedShard
        self.limitedHdc = limitedHdc
        self.expiredDate = expiredDate
