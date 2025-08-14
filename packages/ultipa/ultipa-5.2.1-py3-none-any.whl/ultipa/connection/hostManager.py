# -*- coding: utf-8 -*-
# @Time    : 2023/7/18 09:21
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : hostManager.py
import random
from typing import List

from ultipa.connection.clientInfo import GrpcClientInfo
from ultipa.connection.clientType import ClientType
from ultipa.connection.uqlHelper import UQLHelper
from ultipa.types import ULTIPA


class HostManager:
    '''
        Client manager class for managing Ultipa connection on behalf of client end.

    '''
    username: str
    password: str
    crt: str
    graphSetName: str
    leaderHost: str
    followersPeerInfos: List[ULTIPA.RaftPeerInfo] = None
    leaderInfos: ULTIPA.RaftPeerInfo = None
    leaderClientInfo: GrpcClientInfo = None
    algoClientInfos: List[GrpcClientInfo] = []
    defaultClientInfo: GrpcClientInfo = None
    otherFollowerClientInfos: List[GrpcClientInfo] = []
    otherUnsetFollowerClientInfos: List[GrpcClientInfo] = []
    nullClientInfos: GrpcClientInfo = None
    raftReady: bool = False

    def __init__(self, graphSetName: str, host: str, username: str, password: str, crt: str, maxRecvSize: int):
        self.graphSetName = graphSetName
        self.username = username
        self.password = password
        self.maxRecvSize = maxRecvSize
        self.leaderHost = host
        self.crt = crt
        self.defaultClientInfo = self.__createClientInfo(host)
        self.nullClientInfos = self.__createClientInfo('0.0.0.0')

    def __createClientInfo(self, host: str):

        if self.defaultClientInfo and self.defaultClientInfo.host == host:
            return self.defaultClientInfo

        clientInfo = GrpcClientInfo(host=str(random.choices(host.split(','))[0]), username=self.username,
                                    password=self.password, crt=self.crt,
                                    maxRecvSize=self.maxRecvSize)
        return clientInfo

    def chooseClientInfo(self, clientType: int, uql: str, useHost: str):
        '''
        Three rules: Send to a random node for load balancing.
        Select the connection object.
        :param clientType: the type of connection
        :return:
        '''
        if useHost:
            for clientInfo in self.getAllClientInfos():
                if useHost == clientInfo.host:
                    return clientInfo
            return self.__createClientInfo(useHost)

        clientType = clientType or ClientType.Default
        if uql:
            if UQLHelper.uqlIsExecTask(uql):
                clientType = ClientType.Algo
            elif UQLHelper.uqlIsWrite(uql):
                clientType = ClientType.Update
            elif UQLHelper.uqlIsForceUseMaster(uql):
                clientType = ClientType.Leader
        if clientType == ClientType.Algo:
            if not self.algoClientInfos:
                return self.nullClientInfos
            return random.choice(self.algoClientInfos)
        if clientType == ClientType.Update or clientType == ClientType.Leader:
            return self.leaderClientInfo or self.defaultClientInfo

        return random.choice(list(self.getAllClientInfos(ignoreAlgo=True, needUnset=False)))

    def getAllHosts(self):
        hosts = [self.leaderHost]
        if self.followersPeerInfos:
            for PeerHost in self.followersPeerInfos:
                hosts.append(PeerHost.host)
        return hosts

    def getAllClientInfos(self, ignoreAlgo: bool = False, needUnset: bool = True):
        all = [self.defaultClientInfo]
        if self.leaderClientInfo and self.leaderClientInfo.host != self.defaultClientInfo.host:
            all.append(self.leaderClientInfo)
        if self.algoClientInfos and not ignoreAlgo:
            all.extend(self.algoClientInfos)
        if self.otherFollowerClientInfos:
            all.extend(self.otherFollowerClientInfos)
        if self.otherUnsetFollowerClientInfos and needUnset:
            all.extend(self.otherUnsetFollowerClientInfos)
        return all

    def setClients(self, leaderHost: str, followersPeerInfos: List[ULTIPA.RaftPeerInfo],
                   leaderInfos: ULTIPA.RaftPeerInfo):

        self.leaderHost = leaderHost
        self.leaderClientInfo = self.__createClientInfo(leaderHost)
        self.followersPeerInfos = followersPeerInfos
        self.leaderInfos = leaderInfos
        self.otherFollowerClientInfos = []
        self.otherUnsetFollowerClientInfos = []
        self.algoClientInfos = []

        if followersPeerInfos and len(followersPeerInfos) > 0:
            for peerInfo in followersPeerInfos:

                if peerInfo.isAlgoExecutable:
                    self.algoClientInfos.append(self.__createClientInfo(peerInfo.host))

                if peerInfo.isFollowerReadable:
                    self.otherFollowerClientInfos.append(self.__createClientInfo(peerInfo.host))

                if peerInfo.isUnset:
                    self.otherUnsetFollowerClientInfos.append(self.__createClientInfo(peerInfo.host))
        else:
            self.algoClientInfos = [self.leaderClientInfo]
