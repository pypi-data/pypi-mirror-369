# -*- coding: utf-8 -*-
# @Time    : 2023/7/18 17:17
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : base_extra.py
from ultipa.configuration.RequestConfig import RequestConfig
from ultipa.connection.connectionBase import ConnectionBase
from ultipa.proto import ultipa_pb2
from ultipa.types import ULTIPA, ULTIPA_REQUEST
from ultipa.types.types_response import *
from ultipa.types.types_response import UltipaResponse
from ultipa.utils.format import FormatType
from ultipa.utils.noneCheck import checkNone


class BaseExtra(ConnectionBase):
    '''
        Processing class that defines settings for basic operations.

    '''

    def test(self, config: RequestConfig = RequestConfig()) -> bool:
        '''
        Test connection.

        Args:
            config: An object of RequestConfig class

        Returns:
            Response
        '''
        returnReq = ULTIPA.ReturnReq(config.graph, "test", None, None, False)
        try:

            clientInfo = self.getClientInfo(useHost=config.host)
            name = 'Test'
            res = clientInfo.Controlsclient.SayHello(ultipa_pb2.HelloUltipaRequest(name=name),
                                                     metadata=clientInfo.metadata)
            returnReq.host = clientInfo.host
            if (res.status.error_code == ErrorCode.SUCCESS.value):
                return True
        except Exception as e:
            raise e
        return False

    def exportData(self, request: ULTIPA_REQUEST.ExportRequest, cb: Callable[[List[Node], List[Edge]], None],
                   config: RequestConfig = RequestConfig()):
        try:
            req = ultipa_pb2.ExportRequest(db_type=request.dbType.value, limit=request.limit,
                                           select_properties=request.selectProperties, schema=request.schema)

            graphName = request.graph if not checkNone(request.graph) else config.graph
            clientInfo = self.getClientInfo(graphSetName=graphName)
            res = clientInfo.Controlsclient.Export(req, metadata=clientInfo.metadata)
            nodedata = []
            edgedata = []
            response = UltipaResponse()
            for exportReply in res:
                response.status = FormatType.status(exportReply.status)
                if exportReply.node_table:
                    nodedata = FormatType.export_nodes(exportReply, config.timezone, config.timezoneOffset)
                if exportReply.edge_table:
                    edgedata = FormatType.export_edges(exportReply, config.timezone, config.timezoneOffset)
                if nodedata:
                    uql = ULTIPA.ExportReply(data=nodedata)
                    response.data = uql.data
                    cb(uql.data, None)
                if edgedata:
                    uql = ULTIPA.ExportReply(data=edgedata)
                    response.data = uql.data
                    cb(None, uql.data)

        except Exception as e:
            errorRes = UltipaResponse()
            try:
                message = str(e._state.code) + ' : ' + str(e._state.details)
                print(message)
            except:
                message = 'UNKNOW ERROR'
                print(message)
            errorRes.status = ULTIPA.Status(code=ULTIPA.ErrorCode.UNKNOW_ERROR, message=message)
            return errorRes
