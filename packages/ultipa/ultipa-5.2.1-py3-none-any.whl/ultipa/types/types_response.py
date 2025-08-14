from typing import Callable
from typing import List, Dict

from ultipa.printer.prettyPrint import PrettyPrint
from ultipa.structs.Algo import Algo
from ultipa.structs.GraphSet import GraphSet
from ultipa.structs.Index import Index
from ultipa.structs.InsertErrorCode import InsertErrorCode
from ultipa.structs.Policy import Policy
from ultipa.structs.Privilege import Privilege
from ultipa.structs.Property import Property
from ultipa.structs.Schema import Schema
from ultipa.structs.Stats import Stats
from ultipa.structs.Top import Top
from ultipa.structs.User import User
from ultipa.types.types import BaseModel, Node, Edge, DataItem, Status, \
    Statistics, ReturnReq, BaseUqlReply, ResultType, Alias, ExplainPlan, ErrorCode
from ultipa.utils.convert import Any


class PropertyTable(BaseModel):
    name: str
    data: List[Property]

    def __init__(self, name, data):
        self.name = name
        self.data = data


class UltipaResponse(BaseModel):
    def __init__(self, status: Status = None, data: BaseUqlReply = None,
                 req: ReturnReq = None, statistics: Statistics = None, aliases: List[Alias] = None):
        self.status = status
        self.data = data
        self.statistics = statistics
        self.req = req
        self.aliases = aliases

    def Print(self):
        pretty = PrettyPrint()
        pretty.prettyStatus(self.status)
        if self.status.code != ErrorCode.SUCCESS:
            return
        if self.statistics:
            pretty.prettyStatistics(self.statistics)

        if isinstance(self.data, list):
            dict_list = []
            for i in self.data:
                if isinstance(i, PropertyTable):
                    dict_list.append(i.toDict())
                else:
                    dict_list.append(i.__dict__)
            pretty.prettyDataList(dict_list)

        if isinstance(self.data, Any):
            dict_list = self.data.__dict__
            pretty.prettyData(dict_list)


class JobResponse(BaseModel):
    '''
        Data class for JobResponse
    '''

    def __init__(self, jobId: str = None, statistics: Statistics = None, status: Status = None
                 ):
        self.jobId = jobId
        self.statistics = statistics
        self.status = status


class Response(BaseModel):
    '''
        Data class for Response.
    '''

    def __init__(self, status: Status = None,
                 items: Dict[str, DataItem] = None,
                 statistics: Statistics = None,
                 aliases: List[Alias] = None,
                 explainPlan: ExplainPlan = None):
        self.status = status
        self.items = items
        self.aliases = aliases
        self.statistics = statistics
        self.explainPlan = explainPlan

    def alias(self, alias: str) -> DataItem:
        if self.items == None:
            return DataItem(alias, None, ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET))
        if self.items.get(alias):
            return self.items.get(alias)
        return DataItem(alias, None, ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET))

    def aliasItem(self, alias: str) -> DataItem:
        if self.items == None:
            return DataItem(alias, None, ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET))
        if self.items.get(alias):
            return DataItem(alias, self.items[f'{alias}'].entities, ResultType.getTypeStr(ResultType.RESULT_TYPE_TABLE))
        return DataItem(alias, None, ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET))

    def get(self, index: int) -> DataItem:
        if len(self.aliases) - 1 >= index:
            data = self.items.get(self.aliases[index].name)
            if data:
                return data
            if self.aliases[index].type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
                return DataItem(None, None, ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET))
        return DataItem(None, None, ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET))

    def getExplainPlan(self):
        return self.explainPlan

    def Print(self):
        pretty = PrettyPrint()
        pretty.prettyStatus(self.status)
        if self.status.code != ErrorCode.SUCCESS:
            return
        if self.statistics:
            pretty.prettyStatistics(self.statistics)
        explains = []
        if self.items:
            for key in self.items:
                dataItem = self.items.get(key)
                if dataItem.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_NODE):
                    pretty.prettyNode(dataItem)

                elif dataItem.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_EDGE):
                    pretty.prettyEdge(dataItem)

                elif dataItem.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_TABLE):
                    pretty.prettyTable(dataItem)

                elif dataItem.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_PATH):
                    pretty.prettyPath(dataItem)

                elif dataItem.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_ATTR):
                    pretty.prettyAttr(dataItem)

        if self.explainPlan:
            # for explan in self.explainPlan:
            #     explains.append(explan)
            # if explains:
            pretty.prettyTree(self.explainPlan)


class QueryResponseListener:
    def __init__(self):
        self._listeners = {}
        self._default_handlers = {
            "start": self._default_start_handler,
            "end": self._default_end_handler
        }

    def on(self, event: str, handler: Callable):
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(handler)

    def emit(self, event: str, *args, **kwargs):
        if event in self._listeners:
            for handler in self._listeners[event]:
                handler(*args, **kwargs)
        elif event in self._default_handlers:
            self._default_handlers[event](*args, **kwargs)

    def _default_start_handler(self, request_config):
        print("Stream started with request:", request_config)

    def _default_end_handler(self, request_config):
        print("Stream ended with request:", request_config)


class ResponseCommon(UltipaResponse):
    data: None


# class User(BaseModel):
# 	username: str
# 	create: str
# 	last_login_time: str
# 	graphPrivileges: dict
# 	systemPrivileges: List[str]
# 	policies: List[str]


# class Index(BaseModel):
# 	name: str
# 	properties: str
# 	schema: str
# 	status: str
# 	size:str
# 	dbType:DBType


# class IndexTable:
# 	name: str
# 	data: List[Index]


class Stat(BaseModel):
    cpuUsage: str
    memUsage: str
    company: str
    cpuCores: str
    expiredDate: str
    serverType: str
    version: str


class Return_Type(BaseModel):
    is_realtime: bool
    is_visualization: bool
    is_wirte_back: bool


class Task_info(BaseModel):
    task_id: int = None
    server_id: int = None
    algo_name: str = None
    start_time: int = None
    writing_start_time: int = None
    end_time: int = None
    time_cost: int = None
    TASK_STATUS: int = None
    status_code: str = None
    engine_cost: int = None
    return_type: Return_Type = None


class Task(BaseModel):
    param: dict
    task_info: Task_info
    result: dict


class SearchKhop(BaseModel):
    values: dict
    nodes: List[Node]


class Path(BaseModel):
    nodes: List[Node]
    edges: List[Edge]


class SearchPath(BaseModel):
    paths: List[Path]


class NodeSpread(SearchPath):
    pass


class AutoNet(SearchPath):
    pass


class AlgoResultOpt(BaseModel):
    can_realtime: bool
    can_visualization: bool
    can_write_back: bool


# class Algo(BaseModel):
# 	param: dict
# 	name: str
# 	result_opt: AlgoResultOpt

class ResponseGraph(UltipaResponse):
    data: GraphSet


class ResponseListGraph(UltipaResponse):
    data: List[GraphSet]


# class ResponeListExta(UltipaResponse):
#     data: List[Exta]

class ResponseSchema(UltipaResponse):
    items: Schema


class ResponseListSchema(Response):
    items: List[Schema]


class ResponseListIndex(Response):
    data: List[Index]


# class ResponseListFulltextIndex(ResponseListIndex):
# 	pass


class ResponseSearchEdge(Response):
    items: List[DataItem]


class ResponseSearchNode(Response):
    items: List[DataItem]


class ResponseBulk:
    uuids: List[int]
    errorItem: Dict


class InsertResponse(BaseModel):
    '''
        Data class for InsertResponse

    '''

    def __init__(self, ids: List[str] = None,
                 uuids: List[int] = None,
                 errorItems: Dict[int, InsertErrorCode] = None,
                 statistics: Statistics = None,
                 status: Status = None
                 ):
        self.ids = ids
        self.uuids = uuids
        self.errorItems = errorItems
        self.statistics = statistics
        self.status = status


class ResponseInsertNode(Response):
    data: List[Node]


class ResponseInsertEdge(Response):
    data: List[Edge]


class ResponseDeleteNode(Response):
    data: List[Node]


class ResponseDeleteEdge(Response):
    data: List[Edge]


class ResponseBatchAutoInsert(UltipaResponse):
    data: Dict[str, ResponseBulk]


class ResponseListPolicy(UltipaResponse):
    data: List[Policy]


class ResponsePolicy(UltipaResponse):
    data: Policy


class ResponsePrivilege(UltipaResponse):
    data: List[Privilege]


class ResponseListProperty(Response):
    items: List[Property]


class ResponseProperty(UltipaResponse):
    data: List[Property]


class ResponseListTop(UltipaResponse):
    data: List[Top]


class ResponseListTask(UltipaResponse):
    data: List[Task]


class ResponseUser(UltipaResponse):
    data: User


class ResponseListUser(UltipaResponse):
    data: List[User]


class ResponseListAlgo(UltipaResponse):
    data: List[Algo]


class Cluster:
    host: str
    status: bool
    cpuUsage: str
    memUsage: str
    isLeader: bool
    isFollowerReadable: bool
    isAlgoExecutable: bool
    isUnset: bool


class ClusterInfo(UltipaResponse):
    data: List[Cluster]


class ResponseStat(UltipaResponse):
    data: Stats


class ResponseExport(UltipaResponse):
    data: List[Node]


class ResponseWithExistCheck:
    '''
        Data class for ResponseWithExistCheck

    '''

    def __init__(self,
                 exist: bool = None,
                 response: Response = None
                 ):
        self.exist = exist
        self.response = response
