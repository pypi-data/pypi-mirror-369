import copy
import types
from types import GeneratorType

from ultipa.configuration.RequestConfig import RequestConfig
from ultipa.connection.uqlHelper import UQLHelper
from ultipa.operate.base_extra import BaseExtra
from ultipa.proto import ultipa_pb2
from ultipa.structs.QLType import QLType
from ultipa.structs.Retry import Retry
from ultipa.types import ULTIPA
from ultipa.types.types_response import QueryResponseListener, UltipaResponse, Response
from ultipa.utils.format import FormatType
from ultipa.utils.raftRetry import RetryHelp
from ultipa.utils.ultipa_datetime import getTimeZoneOffset, getTimeOffsetSeconds


class GqlExtra(BaseExtra):
    def gql(self, gql: str, config: RequestConfig = RequestConfig()) -> GeneratorType | Response:
        '''
        Execute GQL.

        Args:
            gql: A gql statement

            config: An object of RequestConfig class

        Returns:
            Response

        '''
        request = ultipa_pb2.QueryRequest()
        request.query_text = gql
        request.query_type = QLType.GQL
        if self.getTimeout(config.timeout):
            request.timeout = self.getTimeout(config.timeout)
        if config.thread is not None:
            request.thread_num = config.thread
        ultipaRes = Response()
        if config.graph == '' and self.defaultConfig.defaultGraph != '':
            config.graph = self.defaultConfig.defaultGraph

        if self.defaultConfig.maxRecvSize != self.hostManagerControl.maxRecvSize:
            self.hostManagerControl.maxRecvSize = self.defaultConfig.maxRecvSize
        onRetry = copy.deepcopy(Retry())
        canRetry = True
        while onRetry.current < onRetry.max and canRetry:
            try:
                import pytz
                getTimeZoneOffset(config, self.defaultConfig)
                timezone = config.timezone
                timezoneOffset = config.timezoneOffset
                timezoneOffset = getTimeOffsetSeconds(timezoneOffset)
                clientInfo = self.getClientInfo(graphSetName=config.graph, uql=gql,
                                                useHost=config.host,
                                                timezone=timezone,
                                                timezoneOffset=timezoneOffset)
                uqlIsExtra = UQLHelper.uqlIsExtra(gql)
                if uqlIsExtra:
                    res = clientInfo.Controlsclient.QueryEx(request, metadata=clientInfo.metadata)
                else:
                    res = clientInfo.Rpcsclient.Query(request, metadata=clientInfo.metadata)

                ultipaRes = FormatType.uqlMergeResponse(res, timezone, timezoneOffset)

                if not isinstance(ultipaRes, types.GeneratorType) and RetryHelp.checkRes(ultipaRes):
                    onRetry.current += 1
                    continue
                else:
                    return ultipaRes

            except Exception as e:
                try:
                    message = str(e._state.code) + ' : ' + str(e._state.details)
                except:
                    message = str(e)
                ultipaRes.status = ULTIPA.Status(code=ULTIPA.ErrorCode.UNKNOW_ERROR, message=message)

                if ultipaRes.status.code not in {ULTIPA.ErrorCode.RAFT_REDIRECT,
                                                 ULTIPA.ErrorCode.RAFT_LEADER_NOT_YET_ELECTED,
                                                 ULTIPA.ErrorCode.RAFT_NO_AVAILABLE_FOLLOWERS,
                                                 ULTIPA.ErrorCode.RAFT_NO_AVAILABLE_ALGO_SERVERS}:
                    canRetry = False
                else:
                    onRetry.current += 1
                    self.hostManagerControl.getHostManger(config.graph).raftReady = False

        return ultipaRes

    def gqlStream(self, gql: str, cb: QueryResponseListener, config: RequestConfig = RequestConfig()):

        '''
        Execute UQL.

        Args:
            gql: A gql statement

            cb: Listener for the streaming process.

            config: An object of RequestConfig class

        '''
        cb.emit("start", config)
        request = ultipa_pb2.QueryRequest()
        request.query_text = gql
        request.query_type = QLType.GQL
        if self.getTimeout(config.timeout):
            request.timeout = self.getTimeout(config.timeout)
        if config.thread is not None:
            request.thread_num = config.thread
        if config.graph == '' and self.defaultConfig.defaultGraph != '':
            config.graph = self.defaultConfig.defaultGraph

        if self.defaultConfig.maxRecvSize != self.hostManagerControl.maxRecvSize:
            self.hostManagerControl.maxRecvSize = self.defaultConfig.maxRecvSize
        onRetry = copy.deepcopy(Retry())
        while onRetry.current < onRetry.max:
            try:
                import pytz
                getTimeZoneOffset(config, self.defaultConfig)
                timezone = config.timezone
                timezoneOffset = config.timezoneOffset
                timezoneOffset = getTimeOffsetSeconds(timezoneOffset)
                clientInfo = self.getClientInfo(graphSetName=config.graph, uql=gql,
                                                useHost=config.host,
                                                timezone=timezone,
                                                timezoneOffset=timezoneOffset)
                uqlIsExtra = UQLHelper.uqlIsExtra(gql)
                if uqlIsExtra:
                    res = clientInfo.Controlsclient.QueryEx(request, metadata=clientInfo.metadata)
                else:
                    res = clientInfo.Rpcsclient.Query(request, metadata=clientInfo.metadata)

                uql_response = UltipaResponse()
                ultipa_response = Response()
                for uqlReply in res:
                    status = FormatType.status(uqlReply.status)
                    uql_response = FormatType.response(uql_response, uqlReply, timezone, timezoneOffset)
                    ret = ULTIPA.UqlReply(dataBase=uql_response.data)

                    if status.code != ULTIPA.ErrorCode.SUCCESS:
                        ultipa_response.status = uql_response.status
                        cb.emit("end", config)
                        return

                    ultipa_response.items = ret._aliasMap
                    ultipa_response.status = uql_response.status
                    ultipa_response.statistics = uql_response.statistics
                    should_continue = cb.emit("data", ultipa_response, config)
                    if should_continue == False:
                        cb.emit("end", config)
                        return

                if not isinstance(ultipa_response, types.GeneratorType) and RetryHelp.checkRes(ultipa_response):
                    onRetry.current += 1
                    continue
                else:
                    cb.emit("end", config)
                    return

            except Exception as e:
                ultipaRes = Response()
                onRetry.current += 1
                self.hostManagerControl.getHostManger(config.graph).raftReady = False
                try:
                    message = str(e._state.code) + ' : ' + str(e._state.details)
                except:
                    message = str(e)
                ultipaRes.status = ULTIPA.Status(code=ULTIPA.ErrorCode.UNKNOW_ERROR, message=message)
                print(ultipaRes.status.message)
        cb.emit("end", config)
        return
