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
from ultipa.types.types_response import PropertyTable, QueryResponseListener, UltipaResponse, Response
from ultipa.utils import UQLMAKER
from ultipa.utils.ResposeFormat import ResponseKeyFormat
from ultipa.utils.convert import convertTableToDict, convertToListAnyObject
from ultipa.utils.format import FormatType
from ultipa.utils.raftRetry import RetryHelp
from ultipa.utils.ultipa_datetime import getTimeZoneOffset, getTimeOffsetSeconds


class UqlExtra(BaseExtra):

    def uql(self, uql: str, config: RequestConfig = RequestConfig()) -> GeneratorType | Response:
        '''
        Execute UQL.

        Args:
            uql: A uql statement

            config: An object of RequestConfig class

        Returns:
            Response

        '''
        request = ultipa_pb2.QueryRequest()
        request.query_text = uql
        request.query_type = QLType.UQL
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
                clientInfo = self.getClientInfo(graphSetName=config.graph, uql=uql,
                                                useHost=config.host,
                                                timezone=timezone,
                                                timezoneOffset=timezoneOffset)
                uqlIsExtra = UQLHelper.uqlIsExtra(uql)
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

    def uqlStream(self, uql: str, cb: QueryResponseListener, config: RequestConfig = RequestConfig()):

        '''
        Execute UQL.

        Args:
            uql: A uql statement

            cb: Listener for the streaming process.

            config: An object of RequestConfig class

        '''
        cb.emit("start", config)
        request = ultipa_pb2.QueryRequest()
        request.query_text = uql
        request.query_type = QLType.UQL
        if self.getTimeout(config.timeout):
            request.timeout = self.getTimeout(config.timeout)
        if config.thread is not None:
            request.thread_num = config.thread

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
                clientInfo = self.getClientInfo(graphSetName=config.graph, uql=uql,
                                                useHost=config.host,
                                                timezone=timezone,
                                                timezoneOffset=timezoneOffset)
                uqlIsExtra = UQLHelper.uqlIsExtra(uql)
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

    def uqlSingle(self, uqlMaker: UQLMAKER) -> Response:
        res = self.uql(uqlMaker.toString(), uqlMaker.commonParams)
        return res

    def UqlListSimple(self, uqlMaker: UQLMAKER, responseKeyFormat: ResponseKeyFormat = None,
                      isSingleOne: bool = True) -> UltipaResponse | Response:
        res = self.uqlSingle(uqlMaker)
        if res.status.code != ULTIPA.ErrorCode.SUCCESS:
            # simplrRes = UltipaResponse(res.status, res.items)
            return res

        if not isSingleOne:
            retList = []
            for alias in res.aliases:
                item = res.items.get(alias.name)
                table = item.entities
                table_rows = table.rows
                table_rows_dict = convertTableToDict(table_rows, table.headers)
                if responseKeyFormat:
                    table_rows_dict = responseKeyFormat.changeKeyValue(table_rows_dict)
                data = convertToListAnyObject(table_rows_dict)
                retList.append(PropertyTable(name=table.name, data=data))
            simplrRes = UltipaResponse(res.status, retList)
            return simplrRes

        alisFirst = res.aliases[0].name if len(res.aliases) > 0 else None
        firstItem = res.items.get(alisFirst)
        if firstItem:
            table_rows = firstItem.entities.rows
            table_rows_dict = convertTableToDict(table_rows, firstItem.entities.headers)
            if responseKeyFormat:
                table_rows_dict = responseKeyFormat.changeKeyValue(table_rows_dict)
            data = convertToListAnyObject(table_rows_dict)
            simplrRes = UltipaResponse(res.status, data)
            simplrRes.statistics = res.statistics
            return simplrRes
        else:
            return res

    def UqlUpdateSimple(self, uqlMaker: UQLMAKER):
        res = self.uqlSingle(uqlMaker)
        return UltipaResponse(res.status, statistics=res.statistics)
