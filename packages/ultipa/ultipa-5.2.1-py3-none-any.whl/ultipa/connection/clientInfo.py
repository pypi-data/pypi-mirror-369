# -*- coding: utf-8 -*-
# @Time    : 2023/7/18 09:21
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : clientInfo.py
import copy

import grpc
import pytz
from tzlocal import get_localzone

from ultipa.proto import ultipa_pb2_grpc
from ultipa.utils.checkHostHttp import checkHost


class ClientInfo:
    '''
        This class defines basic settings for the client end that establishes an Ultipa connection.

        It stores information such as usage of RPCs, control features, host information, etc.
    '''

    def __init__(self, Rpcsclient: ultipa_pb2_grpc.UltipaRpcsStub, Controlsclient: ultipa_pb2_grpc.UltipaControlsStub,
                 metadata: any, graphSetName: str, host: str):
        self.Rpcsclient = Rpcsclient
        self.Controlsclient = Controlsclient
        self.host = host
        self.metadata = metadata
        self.graphSetName = graphSetName


class GrpcClientInfo:
    '''
        This class defines settings for the client's usage of gRPC when communicating with an Ultipa server.
    '''
    Rpcsclient: ultipa_pb2_grpc.UltipaRpcsStub
    Controlsclient: ultipa_pb2_grpc.UltipaControlsStub
    host: str
    username: str
    password: str

    def __init__(self, host: str, username: str, password: str, crt: str, maxRecvSize: int = 32 * 1024 * 1024):
        self.host = f'https://{host}' if checkHost(host) else host
        self._metadata = [('user', username), ('password', password)]
        if self.host.startswith("http"):
            channel = grpc.secure_channel(self.host.replace("https://", "").replace("http://", ""),
                                          grpc.ssl_channel_credentials(), options=(
                    ('grpc.max_send_message_length', maxRecvSize), ('grpc.max_receive_message_length', maxRecvSize),
                    ("grpc.keepalive_timeout_ms", 2 ** 31 - 1)  # 1500
                ))
            self.Rpcsclient = ultipa_pb2_grpc.UltipaRpcsStub(channel=channel, )
            self.Controlsclient = ultipa_pb2_grpc.UltipaControlsStub(channel=channel, )
            return
        if crt:
            credentials = grpc.ssl_channel_credentials(root_certificates=crt)
            channel = grpc.secure_channel(self.host, credentials, options=(
                ('grpc.ssl_target_name_override', 'ultipa'), ('grpc.default_authority', 'ultipa'),
                ('grpc.max_send_message_length', maxRecvSize), ('grpc.max_receive_message_length', maxRecvSize),
                ("grpc.keepalive_timeout_ms", 2 ** 31 - 1)
            ))
            self.Rpcsclient = ultipa_pb2_grpc.UltipaRpcsStub(channel=channel, )
            self.Controlsclient = ultipa_pb2_grpc.UltipaControlsStub(channel=channel, )
        else:
            channel = grpc.insecure_channel(self.host, options=(
                ('grpc.max_send_message_length', maxRecvSize), ('grpc.max_receive_message_length', maxRecvSize),
                ("grpc.keepalive_timeout_ms", 2 ** 31 - 1)))
            self.Rpcsclient = ultipa_pb2_grpc.UltipaRpcsStub(channel=channel, )
            self.Controlsclient = ultipa_pb2_grpc.UltipaControlsStub(channel=channel, )

    def getMetadata(self, graphSetName, timezone, timezoneOffset):
        metadata = copy.deepcopy(self._metadata)
        metadata.append(('graph_name', graphSetName))
        if timezone is not None and timezoneOffset is None:
            metadata.append(('tz', timezone))
        if timezone is None and timezoneOffset is not None:
            metadata.append(('tz_offset', str(timezoneOffset)))
        if timezone is not None and timezoneOffset is not None:
            metadata.append(('tz_offset', str(timezoneOffset)))
        if timezone is None and timezoneOffset is None:
            timezone = get_localzone().key
            tz = pytz.timezone(timezone)
            # timezoneOffset = tz.utcoffset(datetime.now()).total_seconds()
            # metadata.append(('tz_offset', str(timezoneOffset)))
            metadata.append(('tz', str(tz)))

        return metadata
