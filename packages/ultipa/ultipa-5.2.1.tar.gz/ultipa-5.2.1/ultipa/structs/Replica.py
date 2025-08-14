# -*- coding: utf-8 -*-
# @Time    : 2023/8/1 10:47
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : Graph.py
from ultipa.structs.BaseModel import BaseModel


class Replica(BaseModel):
    addr: str
    status: str
    streamAddr: str
    lastHeartBeat: str

    def __init__(self, addr: str = '', status: str = '', streamAddr: str = '',
                 lastHeartBeat: str = ''):
        self.addr = addr
        self.status = status
        self.streamAddr = streamAddr
        self.lastHeartBeat = lastHeartBeat
