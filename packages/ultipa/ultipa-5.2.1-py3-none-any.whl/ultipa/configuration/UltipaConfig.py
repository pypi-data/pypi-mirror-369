# -*- coding: utf-8 -*-
# @Time    : 2023/8/10 18:25
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : UltipaConfig.py
from typing import List

from ultipa.utils.password2md5 import passwrod2md5

MAXINT = 2 ** 31 - 1


class UltipaConfig:
    '''
    Configuration class used to instantiate Ultipa connection.

    This class stores settings for establishing a connection to an Ultipa server. The change of an UltipaConfig object will update the connection it established.
    
    Args:
        - hosts (List[str]): Required. A comma-separated list of database server IPs or URLs. If a URL does not start with https:// or http://, http:// is prefixed by default.
        - username (str): Required. Username of the host authentication.
        - password (str): Required. Password of the host authentication.
        - passwordEncrypt(str): Password encryption method of the driver. Supports MD5, LDAP and NOTHING.
        - crt (str): The file path of the SSL certificate used for secure connections.
        - defaultGraph (str): Name of the graph to use by default in the database.
        - timeout (int): Connection timeout threshold (in second).
        - heartbeat (int): The heartbeat interval (in millisecond), used to keep the connection alive. Set to 0 to disable.
        - maxRecvSize (int): The maximum size (in MB) of the received data.
        
    '''

    def __init__(self, hosts: List[str] = None,
                 username: str = None,
                 password: str = None,
                 passwordEncrypt: str = 'MD5',
                 crt: str = None,
                 defaultGraph: str = None,
                 timeout: int = MAXINT,
                 heartbeat: int = 0,
                 maxRecvSize: int = 32):
        if hosts is None:
            hosts = []
        self.hosts = hosts
        self.username = username
        self.defaultGraph = defaultGraph
        self.crt = crt
        self._password = None
        self.passwordEncrypt = passwordEncrypt
        self.timeout = timeout
        self.heartbeat = heartbeat
        self.maxRecvSize = maxRecvSize * 1024 * 1024
        self.password = password

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        if self.passwordEncrypt == 'MD5' and value is not None:
            self._password = passwrod2md5(value)
        else:
            self._password = value

    def setDefaultGraphName(self, graph: str):
        self.defaultGraph = graph
