# -*-coding:utf-8-*-
import ast
import datetime
import json
from typing import List, Dict

from ultipa.structs import Index, Policy, User, Stats
from ultipa.structs.Algo import Algo
from ultipa.structs.BaseModel import BaseModel
from ultipa.structs.DBType import DBType
from ultipa.structs.Edge import Edge
from ultipa.structs.EntityRow import EntityRow
from ultipa.structs.Graph import Graph, GraphAlias
from ultipa.structs.GraphSet import GraphSet
from ultipa.structs.HDC import HDCGraph, HDCSyncType
from ultipa.structs.Node import Node, NodeAlias
from ultipa.structs.Path import Path, PathAlias
from ultipa.structs.Privilege import Privilege, PrivilegeLevel
from ultipa.structs.Process import Process
from ultipa.structs.Projection import Projection
from ultipa.structs.Property import Property
from ultipa.structs.PropertyPrivilege import PropertyPrivilege, PropertyPrivilegeElement
from ultipa.structs.PropertyType import *
from ultipa.structs.ResultType import ResultType
from ultipa.structs.Retry import Retry
from ultipa.structs.Schema import Schema
from ultipa.utils.ResposeFormat import ResponseKeyFormat
from ultipa.utils.convert import convertToListAnyObject, convertTableToDict, convertToTask, converToJob, \
    converToProjection
from ultipa.utils.errors import ParameterException


# class TruncateType:
# 	NODES = 'nodes'
# 	EDGES = 'edges'


class DirectionType:
    left = 'left'
    right = 'right'


class TaskStatus:
    TASK_WAITING = 0
    TASK_COMPUTING = 1
    TASK_WRITEBACKING = 2
    TASK_DONE = 3
    TASK_FAILED = 4
    TASK_STOP = 5


TaskStatusString = {
    TaskStatus.TASK_WAITING: "TASK_WAITING",
    TaskStatus.TASK_COMPUTING: "TASK_COMPUTING",
    TaskStatus.TASK_WRITEBACKING: "TASK_WRITEBACKING",
    TaskStatus.TASK_DONE: "TASK_DONE",
    TaskStatus.TASK_FAILED: "TASK_FAILED",
    TaskStatus.TASK_STOP: "TASK_STOP"
}


class ALGO_RETURN_TYPE:
    ALGO_RETURN_REALTIME = 1
    ALGO_RETURN_WRITE_BACK = 2
    ALGO_RETURN_VISUALIZATION = 4


class ErrorCode(Enum):
    SUCCESS = ultipa_pb2.SUCCESS
    FAILED = ultipa_pb2.FAILED
    PARAM_ERROR = ultipa_pb2.PARAM_ERROR
    BASE_DB_ERROR = ultipa_pb2.BASE_DB_ERROR
    ENGINE_ERROR = ultipa_pb2.ENGINE_ERROR
    SYSTEM_ERROR = ultipa_pb2.SYSTEM_ERROR
    SYNTAX_ERROR = ultipa_pb2.SYNTAX_ERROR
    RAFT_REDIRECT = ultipa_pb2.RAFT_REDIRECT
    RAFT_LEADER_NOT_YET_ELECTED = ultipa_pb2.RAFT_LEADER_NOT_YET_ELECTED
    RAFT_LOG_ERROR = ultipa_pb2.RAFT_LOG_ERROR
    # UQL_ERROR = ultipa_pb2.UQL_ERROR
    NOT_RAFT_MODE = ultipa_pb2.NOT_RAFT_MODE
    RAFT_NO_AVAILABLE_FOLLOWERS = ultipa_pb2.RAFT_NO_AVAILABLE_FOLLOWERS
    RAFT_NO_AVAILABLE_ALGO_SERVERS = ultipa_pb2.RAFT_NO_AVAILABLE_ALGO_SERVERS
    PERMISSION_DENIED = ultipa_pb2.PERMISSION_DENIED
    DUPLICATE_ID = ultipa_pb2.DUPLICATE_ID

    UNKNOW_ERROR = 1000


class CodeMap:
    _codeMap = {
        ultipa_pb2.SUCCESS: ErrorCode.SUCCESS,
        ultipa_pb2.FAILED: ErrorCode.FAILED,
        ultipa_pb2.PARAM_ERROR: ErrorCode.PARAM_ERROR,
        ultipa_pb2.BASE_DB_ERROR: ErrorCode.BASE_DB_ERROR,
        ultipa_pb2.ENGINE_ERROR: ErrorCode.ENGINE_ERROR,
        ultipa_pb2.SYSTEM_ERROR: ErrorCode.SYSTEM_ERROR,
        ultipa_pb2.SYNTAX_ERROR: ErrorCode.SYNTAX_ERROR,
        ultipa_pb2.RAFT_REDIRECT: ErrorCode.RAFT_REDIRECT,
        ultipa_pb2.RAFT_LEADER_NOT_YET_ELECTED: ErrorCode.RAFT_LEADER_NOT_YET_ELECTED,
        ultipa_pb2.RAFT_LOG_ERROR: ErrorCode.RAFT_LOG_ERROR,
        # ultipa_pb2.UQL_ERROR : UQL_ERROR.name,
        ultipa_pb2.NOT_RAFT_MODE: ErrorCode.NOT_RAFT_MODE,
        ultipa_pb2.RAFT_NO_AVAILABLE_FOLLOWERS: ErrorCode.RAFT_NO_AVAILABLE_FOLLOWERS,
        ultipa_pb2.RAFT_NO_AVAILABLE_ALGO_SERVERS: ErrorCode.RAFT_NO_AVAILABLE_ALGO_SERVERS,
        ultipa_pb2.PERMISSION_DENIED: ErrorCode.PERMISSION_DENIED,
        ultipa_pb2.DUPLICATE_ID: ErrorCode.DUPLICATE_ID,
        1000: ErrorCode.UNKNOW_ERROR

    }

    def getCode(codeKey: str):
        return CodeMap._codeMap[codeKey]


class FollowerRole:
    ROLE_UNSET = ultipa_pb2.ROLE_UNSET
    ROLE_READABLE = ultipa_pb2.ROLE_READABLE
    ROLE_ALGO_EXECUTABLE = ultipa_pb2.ROLE_ALGO_EXECUTABLE


class RaftPeerInfo:
    def __init__(self, host, status=None, isLeader=False, isAlgoExecutable=False, isFollowerReadable=False,
                 isUnset=False):
        self.host = host
        self.status = status
        self.isLeader = isLeader
        self.isAlgoExecutable = isAlgoExecutable
        self.isFollowerReadable = isFollowerReadable
        self.isUnset = isUnset


class ClusterInfo:
    def __init__(self, redirect: str, raftPeers: List[RaftPeerInfo], leader: RaftPeerInfo = None):
        self.redirect = redirect
        self.leader = leader
        self.raftPeers = raftPeers


class Status:
    '''
        Data class for Status
    '''

    def __init__(self, message: str = None, code: ErrorCode = None):
        self.code = code
        self.message = message.strip('\n')


class Schemas:
    def __init__(self, schema: List[Schema] = None, totalNodes: int = None, totalEdges: int = None):
        self.schema = schema
        self.totalNodes = totalNodes
        self.totalEdges = totalEdges


class NodeEntityTable:
    def __init__(self, schemas: List[object], nodeRows: List[EntityRow] = None):
        self.schemas = schemas
        if nodeRows is None:
            nodeRows = []
        self.nodeRows = nodeRows

    def __del__(self):
        pass


class EdgeEntityTable:
    def __init__(self, schemas: List[object], edgeRows: List[EntityRow] = None):
        self.schemas = schemas
        if edgeRows is None:
            edgeRows = []
        self.edgeRows = edgeRows

    def __del__(self):
        pass


class EdgeAlias:
    def __init__(self, alias: str, edges: List[Edge]):
        self.alias = alias
        self.edges = edges


class Attr(BaseModel):
    '''
            Data class for attr
    '''

    def __init__(self, name: str = None,
                 values: List[any] = None,
                 resultType: ResultType = None,
                 propertyType: UltipaPropertyType = None):
        self.name = name
        self.values = values
        self.resultType = resultType
        self.propertyType = propertyType


class AttrNode:
    def __init__(self, alias: str, values: List[List[Node]], type: ResultType = None, type_desc: str = None):
        self.name = alias
        self.values = values
        self.type = type
        self.type_desc = type_desc


class AttrEdge:
    def __init__(self, alias: str, values: List[List[Edge]], type: ResultType = None, type_desc: str = None):
        self.name = alias
        self.values = values
        self.type = type
        self.type_desc = type_desc


class AttrPath:
    def __init__(self, alias: str, values: List[List[Path]], type: ResultType = None, type_desc: str = None):
        self.name = alias
        self.values = values
        self.type = type
        self.type_desc = type_desc


class UltipaAttr:

    def __init__(self, type: UltipaPropertyType, values: any, has_attr_data: bool = False,
                 has_ultipa_data: bool = False, type_desc: any = None):
        self.values = values
        self.type = type
        self.type_desc = type_desc
        self.has_attr_data = has_attr_data
        self.has_ultipa_data = has_ultipa_data


class AttrNewAlias:
    def __init__(self, alias: str, attr: UltipaAttr):
        self.alias = alias
        self.attr = attr


class Alias:
    '''
        Data class for Alias
    '''

    def __init__(self, name: str = None, type: ResultType = None):
        self.name = name
        self.type = type


class Table(BaseModel):
    '''
        Data class for table.
    '''

    def __init__(self, name: str = None, headers: List[dict] = None, rows: List[List[any]] = None):
        self.name = name
        self.rows = rows
        self.headers = headers

    def getHeaders(self):
        return self.headers

    def getRows(self):
        return self.rows

    def getName(self):
        return self.name

    def toKV(self) -> List[Dict]:
        return convertTableToDict(self.rows, self.headers)

    def headerToDicts(self) -> List[Dict]:
        return convertTableToDict(self.rows, self.headers)


class ArrayAlias:
    def __init__(self, alias: str, elements):
        self.alias = alias
        self.elements = elements


class Exta(BaseModel):
    '''
            Data class for exta
    '''

    def __init__(self, author: str = None, detail: str = None, name: str = None, version: str = None):
        self.author = author
        self.detail = detail
        self.name = name
        self.version = version


class PlanNode:
    '''

        Data class for PlanNode

    '''

    def __init__(self, alias: str = None, childrenNum: int = None, uql: str = None, infos: str = None):
        self.alias = alias
        self.children_num = childrenNum
        self.uql = uql
        self.infos = infos


class ExplainPlan:
    '''
        Data class for ExplainPlan

    '''

    def __init__(self, planNodes: List[PlanNode] = None):
        self.planNodes = planNodes


class DataItem(BaseModel):
    '''
        Data class for DataItem

    '''

    def __init__(self, alias: str, entities: any, type: ResultType):
        self.alias = alias
        self.entities = entities
        self.type = type

    def asNodes(self) -> List[Node]:
        if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
            if self.entities is None:
                return []
            return self.entities
        if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_NODE):
            error = f"DataItem {self.alias} is not Type Node"
            raise ParameterException(error)
        return self.entities

    def asFirstNode(self) -> Node:
        if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
            return self.entities
        if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_NODE):
            error = f"DataItem {self.alias} is not Type Node"
            raise ParameterException(error)
        return self.entities[0] if len(self.entities) > 0 else None

    def asEdges(self) -> List[Edge]:
        if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
            if self.entities is None:
                return []
            return self.entities
        if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_EDGE):
            error = f"DataItem {self.alias} is not Type Edge"
            raise ParameterException(error)
        return self.entities

    def asFirstEdge(self) -> Edge:
        if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
            return self.entities
        if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_EDGE):
            error = f"DataItem {self.alias} is not Type Edge"
            raise ParameterException(error)
        return self.entities[0] if len(self.entities) > 0 else None

    def asAttr(self) -> Attr:
        if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
            return self.entities
        if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_ATTR):
            error = f"DataItem {self.alias} is not Type Attribute list"
            raise ParameterException(error)

        return self.entities

    def asAttrNodes(self) -> AttrNode:
        return self.asAttr()

    def asAttrEdges(self) -> AttrEdge:
        return self.asAttr()

    def asAttrPaths(self) -> AttrPath:
        return self.asAttr()

    def asPaths(self) -> List[Path]:
        graphdata = self.entities
        for data in graphdata.paths:
            data.nodes = {nodeuuidsdata: graphdata.nodes[nodeuuidsdata] for nodeuuidsdata in data.nodeUuids}
            data.edges = {edgeuuidsdata: graphdata.edges[edgeuuidsdata] for edgeuuidsdata in data.edgeUuids}
        return graphdata.paths

    def asTable(self) -> Table:
        if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
            return self.entities
        if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_TABLE):
            error = f"DataItem {self.alias} is not Type Table"
            raise ParameterException(error)
        return self.entities

    def asSchemas(self) -> List[Schema]:
        if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
            if self.entities is None:
                return []
            return self.entities
        if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_TABLE):
            error = f"DataItem {self.alias} is not Type Table"
            raise ParameterException(error)
        alias = self.entities.getName()
        if alias.startswith("_node"):
            type = "node"
            dbType = DBType.DBNODE
        elif alias.startswith("_edge"):
            type = "edge"
            dbType = DBType.DBEDGE

        else:
            type = None
            dbType = None

        headers = self.entities.getHeaders()
        rows = self.entities.getRows()
        tableListDict = convertTableToDict(rows, headers)
        REPLACE_KEYS = {
            "totalNodes": "total",
            "totalEdges": "total",
        }
        BOOL_KEYS = ["index", "lte"]
        JSON_KEYS = ["properties"]
        convert2Int = ["totalNodes", "totalEdges"]
        responseKeyFormat = ResponseKeyFormat(keyReplace=REPLACE_KEYS, boolKeys=BOOL_KEYS, jsonKeys=JSON_KEYS,
                                              convert2Int=convert2Int)
        dataList = responseKeyFormat.changeKeyValue(tableListDict)
        schemaList = []

        def none_k(data_none: str):
            return '' if data_none is None else data_none

        for data in dataList:
            responseKeyFormat = ResponseKeyFormat(boolKeys=BOOL_KEYS)
            properList = responseKeyFormat.changeKeyValue(data.get("properties"))
            propertyList = []
            for propo in properList:
                prop = Property(name=none_k(propo.get("name")),
                                description=none_k(propo.get("description")),
                                type=none_k(propo.get("type")),
                                lte=propo.get("lte"),
                                schema=data.get("name"),
                                read=propo.get("read"),
                                write=propo.get("write"),
                                encrypt=none_k(propo.get("encrypt")
                                               ))

                prop.type = prop.getPropertyTypeByString(prop.type)
                propertyList.append(prop)

            schemaList.append(
                Schema(name=data.get("name"), description=data.get("description"),
                       properties=propertyList,
                       dbType=dbType,
                       id=int(data.get('id')) if data.get('id').isdigit() else None,
                       total=int(data.get("total")) if data.get("total") and data.get("total") != '' else data.get(
                           "total")))

        return schemaList

    def asProperties(self) -> List[Property]:
        if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
            if self.entities is None:
                return []
            return self.entities
        if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_TABLE):
            error = f"DataItem {self.alias} is not Type Table"
            raise ParameterException(error)
        headers = self.entities.getHeaders()
        rows = self.entities.getRows()
        table_rows_dict = convertTableToDict(rows, headers)
        BOOL_KEYS = ["lte", "read", "write"]
        responseKeyFormat = ResponseKeyFormat(boolKeys=BOOL_KEYS)
        dataList = responseKeyFormat.changeKeyValue(table_rows_dict)

        def none_k(data_none: str):
            return '' if data_none is None else data_none

        propertyList = []
        for propo in dataList:
            prop = Property(name=none_k(propo.get("name")),
                            description=none_k(propo.get("description")),
                            type=none_k(propo.get("type")),
                            lte=propo.get("lte"),
                            schema=propo.get("schema"),
                            read=propo.get("read"),
                            write=propo.get("write"),
                            encrypt=none_k(propo.get("encrypt")
                                           ))

            prop.type = prop.getPropertyTypeByString(prop.type)
            propertyList.append(prop)

        return propertyList

    def asGraphSets(self) -> List[GraphSet]:
        REPLACE_KEYS = {
            "graph": "name",
        }
        if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
            if self.entities is None:
                return []
            return self.entities
        if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_TABLE):
            error = f"DataItem {self.alias} is not Type Table"
            raise ParameterException(error)
        headers = self.entities.getHeaders()
        rows = self.entities.getRows()
        table_rows_dict = convertTableToDict(rows, headers)
        responseKeyFormat = ResponseKeyFormat(keyReplace=REPLACE_KEYS)
        data = responseKeyFormat.changeKeyValue(table_rows_dict)
        data = [GraphSet(id=res.id, description=res.description, name=res.name,
                         totalNodes=int(res.total_nodes) if hasattr(res,
                                                                    'total_nodes') and res.total_nodes.isdigit() else 0,
                         totalEdges=int(res.total_edges) if hasattr(res,
                                                                    'total_edges') and res.total_edges.isdigit() else 0,
                         slotNum=int(res.slot_num) if res.slot_num.isdigit() else 0,
                         shards=res.shards.split(','),
                         partitionBy=res.partition_by,
                         status=res.status
                         ) for res in convertToListAnyObject(data)]
        return data

    def asGraph(self) -> Graph:
        if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
            if self.entities is None:
                return []
            return self.entities
        if self.type != ResultType.RESULT_TYPE_GRAPH:
            error = f"DataItem {self.alias} is not Type Graph"
            raise ParameterException(error)
        return Graph(paths=self.entities.paths, nodes=self.entities.nodes, edges=self.entities.edges)

    def asAlgos(self) -> List[Algo]:
        if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
            if self.entities is None:
                return []
            return self.entities
        if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_TABLE):
            error = f"DataItem {self.alias} is not Type Table"
            raise ParameterException(error)
        headers = self.entities.getHeaders()
        rows = self.entities.getRows()
        table_rows_dict = convertTableToDict(rows, headers)
        algo_list = []
        for paramDict in table_rows_dict:
            desc = json.loads(paramDict.get("description"))
            algoObj = Algo(name=paramDict.get("name"),
                           version=desc.get('version'),
                           type=paramDict.get("type"),
                           params=paramDict.get("params"),
                           description=paramDict.get("description"),
                           canRollback=paramDict.get("can_rollback"),
                           configContext=paramDict.get("config_context"),
                           writeSupportType=paramDict.get('write_support_type')
                           )

            algo_list.append(algoObj)
        return algo_list

    def asHDCGraphs(self) -> List[HDCGraph]:
        if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
            if self.entities is None:
                return []
            return self.entities
        if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_TABLE):
            error = f"DataItem {self.alias} is not Type Table"
            raise ParameterException(error)
        headers = self.entities.getHeaders()
        rows = self.entities.getRows()
        table_rows_dict = convertTableToDict(rows, headers)
        algo_list = []
        for paramDict in table_rows_dict:
            algoObj = HDCGraph(name=paramDict.get("name"),
                               graphName=paramDict.get("graph_name"),
                               status=paramDict.get("status"),
                               stats=paramDict.get('stats'),
                               isDefault=paramDict.get("is_default"),
                               hdcServerName=paramDict.get('hdc_server_name'),
                               hdcServerStatus=paramDict.get('hdc_server_status'),
                               config=paramDict.get('config')
                               )

            algo_list.append(algoObj)
        return algo_list

    def asExtas(self) -> List[Exta]:
        if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
            if self.entities is None:
                return []
            return self.entities
        if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_TABLE):
            error = f"DataItem {self.alias} is not Type Table"
            raise ParameterException(error)

        headers = self.entities.getHeaders()
        rows = self.entities.getRows()
        table_rows_dict = convertTableToDict(rows, headers)
        exta_list = []
        for data in table_rows_dict:
            exta = Exta(author=data.get('author'),
                        detail=data.get('detail'),
                        name=data.get('name'),
                        version=data.get('version'))

            exta_list.append(exta)

        return exta_list

    def asIndexes(self) -> List[Index]:
        if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
            if self.entities is None:
                return []
            return self.entities
        if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_TABLE):
            error = f"DataItem {self.alias} is not Type Table"
            raise ParameterException(error)
        headers = self.entities.getHeaders()
        rows = self.entities.getRows()
        table_rows_dict = convertTableToDict(rows, headers)
        index_list = []
        for data in table_rows_dict:
            index = Index(
                id=data.get('id'),
                dbType=data.get('db_type'),
                name=data.get('name'),
                properties=data.get('properties'),
                schema=data.get('schema'),
                size=data.get('size'),
                status=data.get('status'))

            index_list.append(index)

        return index_list

    def asPrivileges(self) -> List[Privilege]:
        if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
            if self.entities is None:
                return None
            return self.entities
        if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_TABLE):
            error = f"DataItem {self.alias} is not Type Table"
            raise ParameterException(error)
        headers = self.entities.getHeaders()
        rows = self.entities.getRows()
        table_rows_dict = convertTableToDict(rows, headers)
        privilege_list = []
        for data in table_rows_dict:
            sysPrivileges = [Privilege(name=sysdata, level=PrivilegeLevel.SYSTEM) for sysdata in
                             ast.literal_eval(data.get('systemPrivileges'))]
            privilege_list.extend(sysPrivileges)
            graPrivileges = [Privilege(name=gradata, level=PrivilegeLevel.GRAPH) for gradata in
                             ast.literal_eval(data.get('graphPrivileges'))]
            privilege_list.extend(graPrivileges)
        return privilege_list

    def asPolicies(self) -> List[Policy]:
        if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
            if self.entities is None:
                return []
            return self.entities
        if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_TABLE):
            error = f"DataItem {self.alias} is not Type Table"
            raise ParameterException(error)
        headers = self.entities.getHeaders()
        rows = self.entities.getRows()
        table_rows_dict = convertTableToDict(rows, headers)
        policy_list = []
        for data in table_rows_dict:
            proPrivilegesData = json.loads(data.get('propertyPrivileges'))
            policy = Policy(
                name=data.get('name'),
                graphPrivileges=json.loads(data.get('graphPrivileges')),
                systemPrivileges=json.loads(data.get('systemPrivileges')),
                propertyPrivileges=PropertyPrivilege(
                    PropertyPrivilegeElement(
                        proPrivilegesData['node'].get('read'),
                        proPrivilegesData['node'].get('write'),
                        proPrivilegesData['node'].get('deny'),
                    ),
                    PropertyPrivilegeElement(
                        proPrivilegesData['edge'].get('read'),
                        proPrivilegesData['edge'].get('write'),
                        proPrivilegesData['edge'].get('deny'),
                    )
                ),
                policies=ast.literal_eval(data.get('policies')))

            policy_list.append(policy)
        if len(policy_list) == 1:
            return policy_list[0]
        return policy_list

    def asUsers(self) -> List[User]:
        if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
            if self.entities is None:
                return []
            return self.entities
        if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_TABLE):
            error = f"DataItem {self.alias} is not Type Table"
            raise ParameterException(error)
        headers = self.entities.getHeaders()
        rows = self.entities.getRows()
        table_rows_dict = convertTableToDict(rows, headers)
        user_list = []
        for data in table_rows_dict:
            proPrivilegesData = json.loads(data.get('propertyPrivileges'))
            user = User(createdTime=datetime.datetime.fromtimestamp(data.get('create')),
                        username=data.get('username'),
                        graphPrivileges=json.loads(data.get('graphPrivileges')),
                        systemPrivileges=json.loads(data.get('systemPrivileges')),
                        propertyPrivileges=PropertyPrivilege(
                            PropertyPrivilegeElement(
                                proPrivilegesData['node'].get('read'),
                                proPrivilegesData['node'].get('write'),
                                proPrivilegesData['node'].get('deny'),
                            ),
                            PropertyPrivilegeElement(
                                proPrivilegesData['edge'].get('read'),
                                proPrivilegesData['edge'].get('write'),
                                proPrivilegesData['edge'].get('deny'),
                            )
                        ),
                        policies=ast.literal_eval(data.get('policies')))

            user_list.append(user)

        if len(user_list) == 1:
            return user_list[0]
        return user_list

    def asStats(self) -> Stats:
        if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
            if self.entities is None:
                return []
            return self.entities
        if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_TABLE):
            error = f"DataItem {self.alias} is not Type Table"
            raise ParameterException(error)
        headers = self.entities.getHeaders()
        rows = self.entities.getRows()
        table_rows_dict = convertTableToDict(rows, headers)
        stats_list = []
        for data in table_rows_dict:
            stats = Stats(limitedHdc=data.get('limited_hdc'),
                          limitedShard=data.get('limited_shard'),
                          expiredDate=data.get('expired_date')
                          )

            stats_list.append(stats)

        return stats_list[0]

    def asProcesses(self) -> List[Process]:
        if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
            if self.entities is None:
                return []
            return self.entities
        if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_TABLE):
            error = f"DataItem {self.alias} is not Type Table"
            raise ParameterException(error)
        headers = self.entities.getHeaders()
        rows = self.entities.getRows()
        table_rows_dict = convertTableToDict(rows, headers)
        process_list = []
        for data in table_rows_dict:
            process = Process(processId=data.get('process_id'),
                              processQuery=data.get('process_uql'),
                              duration=data.get('duration'),
                              status=data.get('status')
                              )

            process_list.append(process)

        return process_list

    def asTasks(self):
        from ultipa.types import types_response
        _jsonKeys = ['taskJson']
        headers = self.entities.getHeaders()
        rows = self.entities.getRows()
        table_rows_dict = convertTableToDict(rows, headers)
        responseKeyFormat = ResponseKeyFormat(jsonKeys=_jsonKeys)
        if responseKeyFormat:
            table_rows_dict = responseKeyFormat.changeKeyValue(table_rows_dict)
        task_list = []
        for data in table_rows_dict:
            task_info = data.get('taskJson').get('task_info')
            if task_info.get('status_code'):
                task_info["status_code"] = TaskStatusString[task_info.get("TASK_STATUS")]
            if task_info.get('engine_cost'):
                task_info["engine_cost"] = task_info.get("writing_start_time", 0) - task_info.get("start_time", 0)

            data['taskJson']['task_info'] = convertToTask(task_info)
            return_type_get = int(task_info.get('return_type', 0))
            return_type = types_response.Return_Type()
            return_type.is_realtime = True if return_type_get & ALGO_RETURN_TYPE.ALGO_RETURN_REALTIME else False
            return_type.is_visualization = True if return_type_get & ALGO_RETURN_TYPE.ALGO_RETURN_VISUALIZATION else False
            return_type.is_wirte_back = True if return_type_get & ALGO_RETURN_TYPE.ALGO_RETURN_WRITE_BACK else False
            data['taskJson']['task_info'].__setattr__('return_type', return_type)
            task = types_response.Task()
            task.param = data.get('taskJson').get('param')
            task.task_info = data.get('taskJson').get('task_info')
            task.result = data.get('taskJson').get('result')

            task_list.append(task)

        return task_list

    def asProjections(self) -> List[Projection]:
        if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
            if self.entities is None:
                return []
            return self.entities
        if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_TABLE):
            error = f"DataItem {self.alias} is not Type Table"
            raise ParameterException(error)
        return converToProjection(convertTableToDict(self.entities.rows, self.entities.headers))

    def asAny(self) -> any:
        return self.entities

    def asKV(self):
        return self.toDict()

    def asJobs(self):
        if self.type == ResultType.getTypeStr(ResultType.RESULT_TYPE_UNSET):
            if self.entities is None:
                return []
            return self.entities
        if self.type != ResultType.getTypeStr(ResultType.RESULT_TYPE_TABLE):
            error = f"DataItem {self.alias} is not Type Table"
            raise ParameterException(error)
        return [converToJob(data) for data in convertTableToDict(self.entities.rows, self.entities.headers)]


class BaseUqlReply:
    def __init__(self, nodes: List[NodeAlias], edges: List[EdgeAlias], tables: List[Table],
                 graphs: List[GraphAlias], attrs: List = None,
                 resultAlias: List = None,
                 explainPlan: ExplainPlan = None,
                 paths: List[PathAlias] = []):
        self.paths = paths
        self.nodes = nodes
        self.edges = edges
        self.tables = tables
        self.attrs = attrs
        self.graphs = graphs
        # self.arrays = arrays
        self.resultAlias = resultAlias
        self.explainPlan = explainPlan


class Statistics(BaseModel):
    '''
        Data class for Statistics
    '''

    def __init__(self, edgeAffected: int = None, nodeAffected: int = None, engineCost: int = None,
                 totalCost: int = None):
        self.edgeAffected = edgeAffected
        self.nodeAffected = nodeAffected
        self.engineCost = engineCost
        self.totalCost = totalCost


class UqlReply(BaseModel):
    datas: List[DataItem]

    def __init__(self, dataBase: BaseUqlReply, aliasMap: dict = None, datas: List = None):
        if aliasMap == None:
            aliasMap = {}
        self._aliasMap = aliasMap
        if datas is None:
            datas = []
        self.datas: List[DataItem] = datas
        self.explainPlan: ExplainPlan = []
        self._dataBase = dataBase

        for data in self._dataBase.paths:
            if self._aliasMap.get(data.alias):
                self._aliasMap[data.alias].data.extend(data.paths)
                continue
            self._aliasMap[data.alias] = DataItem(data.alias, data.paths,
                                                  ResultType.getTypeStr(ResultType.RESULT_TYPE_PATH))

        for data in self._dataBase.graphs:
            if self._aliasMap.get(data.alias):
                self._aliasMap[data.alias].data.extend(data.graph)
                continue
            self._aliasMap[data.alias] = DataItem(data.alias, data.graph,
                                                  ResultType.getTypeStr(ResultType.RESULT_TYPE_GRAPH))

        # for data in self._dataBase.graphs:
        # 	if self._aliasMap.get(data.alias):
        # 		self._aliasMap[data.alias].data.extend(data.graph)
        # 		continue
        # 	self._aliasMap[data.alias] = DataItem(data.alias, data.graph,
        # 										  ResultType.getTypeStr(ResultType.RESULT_TYPE_GRAPH))

        for data in self._dataBase.nodes:
            if self._aliasMap.get(data.alias):
                self._aliasMap[data.alias].data.extend(data.nodes)
                continue
            self._aliasMap[data.alias] = DataItem(data.alias, data.nodes,
                                                  ResultType.getTypeStr(ResultType.RESULT_TYPE_NODE))

        for data in self._dataBase.edges:
            if self._aliasMap.get(data.alias):
                self._aliasMap[data.alias].data.extend(data.edges)
                continue
            self._aliasMap[data.alias] = DataItem(data.alias, data.edges,
                                                  ResultType.getTypeStr(ResultType.RESULT_TYPE_EDGE))

        for data in self._dataBase.attrs:
            if self._aliasMap.get(data.name):
                self._aliasMap[data.name].data.append(data)
                continue
            self._aliasMap[data.name] = DataItem(data.name, data, ResultType.getTypeStr(ResultType.RESULT_TYPE_ATTR))

        for data in self._dataBase.tables:
            if self._aliasMap.get(data.name):
                self._aliasMap[data.name].data.extend(data)
                continue
            self._aliasMap[data.name] = DataItem(data.name, data, ResultType.getTypeStr(ResultType.RESULT_TYPE_TABLE))

        for data in self._dataBase.explainPlan.planNodes:
            self.explainPlan.planNodes.append(data)

        for data in self._dataBase.resultAlias:
            if self._aliasMap.get(data.name):
                self.datas.append(self._aliasMap[data.name])
        if not self.datas:
            for key in self._aliasMap:
                self.datas.append(self._aliasMap[key])


class ReturnReq:
    def __init__(self, graphSetName: str, uql: str, host: str, retry: Retry, uqlIsExtra: bool):
        self.graph_name = graphSetName
        self.uql = uql
        self.host = host
        self.Retry = retry
        self.uqlIsExtra = uqlIsExtra


class ExportReply:
    def __init__(self, data: List[NodeAlias]):
        self.data = data


class PaserAttrListData:
    def __init__(self, type, nodes: List[Node] = None, edges: List[Edge] = None, paths: List[Path] = None,
                 attrs: UltipaAttr = None):
        self.type = type
        self.nodes = nodes
        self.edges = edges
        self.paths = paths
        self.attrs = attrs


class HDCDirection(Enum):
    OUT = 'out'
    IN = 'in'
    UNDIRECTED = 'undirected'


class HDCBuilder:
    def __init__(self, hdcGraphName: str,
                 nodeSchema: [Dict[str, List[str]]],
                 edgeSchema: [Dict[str, List[str]]],
                 hdcServerName: str,
                 direction: HDCDirection = HDCDirection.UNDIRECTED,
                 loadId: bool = True,
                 isDefault: bool = False,
                 syncType: HDCSyncType = HDCSyncType.STATIC,
                 ):
        self.hdcGraphName = hdcGraphName
        self.nodeSchema = nodeSchema
        self.edgeSchema = edgeSchema
        self.hdcServerName = hdcServerName
        self.syncType = syncType
        self.direction = direction
        self.loadId = loadId
        self.isDefault = isDefault
