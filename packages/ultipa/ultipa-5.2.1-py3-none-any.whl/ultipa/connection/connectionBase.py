# -*- coding: utf-8 -*-
# @Time    : 2023/7/18 09:20
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : connectionBase.py
import schedule

from ultipa.configuration.UltipaConfig import UltipaConfig
from ultipa.connection.clientInfo import ClientInfo
from ultipa.connection.clientType import ClientType
from ultipa.connection.hostManagerControl import HostManagerControl, RAFT_GLOBAL
from ultipa.connection.uqlHelper import UQLHelper
from ultipa.proto import ultipa_pb2
from ultipa.utils import CommandList
from ultipa.utils.errors import ParameterException
from ultipa.utils.ultipaSchedule import run_continuously


class ConnectionBase:
    '''
        A base class that defines settings for an Ultipa connection.

    '''

    def __init__(self, host: str, defaultConfig: UltipaConfig, crt: str = None):
        self.host = host
        self.username = defaultConfig.username
        self.password = defaultConfig.password
        self.crt = crt
        self.defaultConfig = defaultConfig
        self.runSchedule: object = None
        self.crt = None
        if crt:
            try:
                with open(f'{crt}', 'rb') as f:
                    self.crt = f.read()
            except Exception as e:
                raise ParameterException(err=e)
        self.hostManagerControl = HostManagerControl(self.host, self.username, self.password,
                                                     self.defaultConfig.maxRecvSize, self.crt,
                                                     )

        self.defaultConfig.defaultGraph = defaultConfig.defaultGraph
        self.defaultConfig.timeout = defaultConfig.timeout
        self.graphSetName = self.defaultConfig.defaultGraph
        self.count = 0

    def getGraphSetName(self, currentGraphName: str, uql: str = "", isGlobal: bool = False):
        # if isGlobal:
        #     return RAFT_GLOBAL
        # if uql:
        parse = UQLHelper(uql)
        #     if parse.uqlIsGlobal():
        #         return RAFT_GLOBAL
        c1 = parse.parseRet.getFirstCommands()
        c2 = f"{c1}().{parse.parseRet.getSecondCommands()}"
        if c2 in [CommandList.mount, CommandList.unmount, CommandList.truncate]:
            graphName = parse.parseRet.getCommandsParam(1)
            if graphName:
                return graphName
        return currentGraphName or self.defaultConfig.defaultGraph

    def getTimeout(self, timeout: int):
        restimeout = timeout is None and self.defaultConfig.timeout or timeout
        return restimeout

    def getClientInfo(self, clientType: int = ClientType.Default, graphSetName: str = '', uql: str = '',
                      isGlobal: bool = False, ignoreRaft: bool = False, useHost: str = None,
                      timezone=None, timezoneOffset=None):
        goGraphName = self.getGraphSetName(currentGraphName=graphSetName, uql=uql, isGlobal=isGlobal)
        if not ignoreRaft and not self.hostManagerControl.getHostManger(goGraphName).raftReady:
            self.hostManagerControl.getHostManger(goGraphName).raftReady = False

        clientInfo = self.hostManagerControl.chooseClientInfo(type=clientType, uql=uql, graphSetName=goGraphName,
                                                              useHost=useHost)
        metadata = clientInfo.getMetadata(goGraphName, timezone, timezoneOffset)
        return ClientInfo(Rpcsclient=clientInfo.Rpcsclient, Controlsclient=clientInfo.Controlsclient, metadata=metadata,
                          graphSetName=goGraphName, host=clientInfo.host)

    def stopConnectionAlive(self):
        if self.runSchedule != None:
            self.runSchedule.set()

    def keepConnectionAlive(self, timeIntervalSeconds: int = None):
        timeIntervalSeconds = self.defaultConfig.heartbeat if timeIntervalSeconds == None else timeIntervalSeconds

        def test_allconn():
            goGraphName = self.defaultConfig.defaultGraph
            for host in self.hostManagerControl.getAllClientInfos(goGraphName):
                res = host.Controlsclient.SayHello(ultipa_pb2.HelloUltipaRequest(name="test"),
                                                   metadata=host.getMetadata(goGraphName, None, None))
            # print(host.host,res.message)

        schedule.every().second.do(test_allconn)
        self.runSchedule = run_continuously(timeIntervalSeconds)
