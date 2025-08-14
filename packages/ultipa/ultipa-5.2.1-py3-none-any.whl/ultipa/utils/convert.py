import datetime
import json
from typing import List

from ultipa.structs.Algo import Algo
from ultipa.structs.BaseModel import BaseModel
from ultipa.structs.DBType import DBType
from ultipa.structs.GraphSet import GraphSet
from ultipa.structs.HDC import HDCGraph
from ultipa.structs.Index import Index
from ultipa.structs.Job import Job
from ultipa.structs.License import License
from ultipa.structs.Policy import Policy
from ultipa.structs.Privilege import Privilege, PrivilegeLevel
from ultipa.structs.Process import Process
from ultipa.structs.Projection import Projection
from ultipa.structs.PropertyPrivilege import PropertyPrivilege, PropertyPrivilegeElement
from ultipa.structs.Schema import SchemaStat
from ultipa.structs.Stats import Stats
from ultipa.structs.User import User
from ultipa.utils.noneCheck import checkNone


class Any(BaseModel):
    '''
    Any model
    '''

    def __str__(self):
        return str(self.__dict__)

    pass


def convertToAnyObject(dict1: dict):
    '''
    Convert Dict to Object.

    Args:
        dict1:

    Returns:

    '''
    obj = Any()
    for k in dict1.keys():
        v = dict1[k]
        if isinstance(v, list):
            for i, n in enumerate(v):
                if isinstance(n, dict):
                    v[i] = convertToAnyObject(n)
        # if isinstance(v, dict):
        #     v = convertToAnyObject(v)
        obj.__setattr__(k, v)
    return obj


def convertToTask(dict1: dict):
    '''
    Convert Dict to Object.

    Args:
        dict1:

    Returns:

    '''

    from ultipa.types.types_response import Task_info
    taskInfo = Task_info()
    for k, value in dict1.items():
        # if isinstance(v, dict):
        #     v = convertToAnyObject(v)
        if hasattr(taskInfo, k):
            setattr(taskInfo, k, value)

    return taskInfo


def convertToListAnyObject(list1: List[dict]):
    '''
    Convert List[Dict] to Object.

    Args:
        list1:

    Returns:

    '''
    if not list1 and isinstance(list1, list):
        return list1
    if not list1:
        return
    newList = []
    for dict1 in list1:
        newList.append(convertToAnyObject(dict1))
    return newList


def convertTableToDict(table_rows, headers):
    '''
    Convert Table to Object.

    Args:
        table_rows:
        headers:

    Returns:

    '''
    newList = []
    for data in table_rows:
        dic = {}
        for index, header in enumerate(headers):
            dic.update({header.get("property_name"): data[index]})
        newList.append(dic)
    return newList


def convertToGraph(res):
    if isinstance(res.data, list) and len(res.data) > 1:
        graphdata = res.data
        graphdata.sort(key=lambda graph: int(graph.id))
        graphlist = []
        for graph in graphdata:
            graphlist.append(GraphSet(
                id=graph.id,
                name=graph.name,
                totalNodes=int(graph.total_nodes) if hasattr(graph, 'total_nodes') and graph.total_nodes.isdigit() else 0,
                totalEdges=int(graph.total_edges) if hasattr(graph, 'total_edges') and graph.total_edges.isdigit() else 0,
                description=graph.description,
                status=graph.status,
                shards=graph.shards.split(','),
                partitionBy=graph.partition_by,
                slotNum=int(graph.slot_num) if graph.slot_num.isdigit else 0
            ))

        return graphlist
    else:
        graph = res.data[0]
        return GraphSet(
            id=graph.id,
            name=graph.name,
            totalNodes=int(graph.total_nodes) if hasattr(graph, 'total_nodes') and graph.total_nodes.isdigit() else 0,
            totalEdges=int(graph.total_edges) if hasattr(graph, 'total_edges') and graph.total_edges.isdigit() else 0,
            description=graph.description,
            status=graph.status,
            shards=graph.shards.split(','),
            partitionBy=graph.partition_by,
            slotNum=int(graph.slot_num) if graph.slot_num.isdigit else 0
        )


def convertToIndex(res, all: bool = True, dbtype: DBType = None):
    nodeindex = []
    edgeindex = []
    indexdata = []
    if all:
        nodeindex = res.data[0].data
        edgeindex = res.data[1].data
    elif dbtype == DBType.DBNODE:
        nodeindex = res.data[0].data
    elif dbtype == DBType.DBEDGE:
        edgeindex = res.data[0].data

    if nodeindex:
        for index in nodeindex:
            indexdata.append(Index(
                id=index.id,
                name=index.name,
                properties=index.properties,
                schema=index.schema,
                # size=index.size,
                status=index.status,
                dbType=DBType.DBNODE
            ))
    if edgeindex:
        for index in edgeindex:
            indexdata.append(Index(
                id=index.id,
                name=index.name,
                properties=index.properties,
                schema=index.schema,
                # size=index.size,
                status=index.status,
                dbType=DBType.DBEDGE
            ))
    return indexdata


def convertToFullText(res, all: bool = True, dbtype: DBType = None):
    nodeindex = []
    edgeindex = []
    indexdata = []
    if all:
        nodeindex = res.data[0].data
        edgeindex = res.data[1].data
    elif dbtype == DBType.DBNODE:
        nodeindex = res.data[0].data
    elif dbtype == DBType.DBEDGE:
        edgeindex = res.data[0].data

    if nodeindex:
        for index in nodeindex:
            indexdata.append(Index(
                name=index.name,
                properties=index.properties,
                schema=index.schema,
                status=index.status,
                dbType=DBType.DBNODE
            ))
    if edgeindex:
        for index in edgeindex:
            indexdata.append(Index(
                name=index.name,
                properties=index.properties,
                schema=index.schema,
                status=index.status,
                dbType=DBType.DBEDGE
            ))
    return indexdata


def convertToUser(res):
    if isinstance(res.data, list) and len(res.data) > 1:
        userdata = res.data
        datalist = []
        for data in userdata:
            proPrivilegesData = json.loads(data.propertyPrivileges)
            datalist.append(User(
                username=data.username,
                systemPrivileges=data.systemPrivileges,
                graphPrivileges=data.graphPrivileges,
                createdTime=datetime.datetime.fromtimestamp(data.create),
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
                policies=data.policies
            ))

        return datalist
    else:
        data = res.data[0]
        proPrivilegesData = json.loads(data.propertyPrivileges)
        return User(
            username=data.username,
            systemPrivileges=data.systemPrivileges,
            graphPrivileges=data.graphPrivileges,
            createdTime=datetime.datetime.fromtimestamp(data.create),
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
            policies=data.policies
        )


def convertToPolicy(res):
    if isinstance(res.data, list) and len(res.data) > 1:
        policydata = res.data
        policylist = []
        for data in policydata:
            proPrivilegesData = json.loads(data.propertyPrivileges)
            policylist.append(Policy(
                name=data.name,
                systemPrivileges=data.systemPrivileges,
                graphPrivileges=data.graphPrivileges,
                policies=data.policies,
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
                )
            ))

        return policylist
    else:
        data = res.data[0]
        proPrivilegesData = json.loads(data.propertyPrivileges)
        return Policy(
            name=data.name,
            systemPrivileges=data.systemPrivileges,
            graphPrivileges=data.graphPrivileges,
            policies=data.policies,
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
            )
        )


def convertToPrivilege(res):
    if isinstance(res.data, list) and len(res.data) > 1:
        privilegedata = res.data
        privilegelist = []
        for data in privilegedata:
            sysPrivileges = [Privilege(name=sysdata, level=PrivilegeLevel.SYSTEM) for sysdata in data.systemPrivileges]
            privilegelist.extend(sysPrivileges)
            graPrivileges = [Privilege(name=gradata, level=PrivilegeLevel.GRAPH) for gradata in data.graphPrivileges]
            privilegelist.extend(graPrivileges)

        return privilegelist
    else:
        data = res.data[0]
        sysPrivileges = [Privilege(name=sysdata, level=PrivilegeLevel.SYSTEM) for sysdata in data.systemPrivileges]
        graPrivileges = [Privilege(name=gradata, level=PrivilegeLevel.GRAPH) for gradata in data.graphPrivileges]
        sysPrivileges.extend(graPrivileges)
        return sysPrivileges


def convertToStats(res):
    statsdata = res.data[0]
    return Stats(
        limitedHdc=statsdata.limited_hdc,
        limitedShard=statsdata.limited_shard,
        expiredDate=statsdata.expired_date
    )


def convertToSchemas(res):
    from ultipa.types.types import Schemas
    graphcount = convertTableToDict(res.alias("_graphCount").entities.rows, res.alias("_graphCount").entities.headers)
    schemasresult = Schemas()
    count = {}
    for data in graphcount:
        if not checkNone(data.get('schema')):
            edgepair = count.get(data.get('schema')) if count.get(data.get('schema')) is not None else []
            data['count'] = int(data.get('count')) if data.get('count') and data.get(
                'count').isdigit() else 0
            edgepair.append(data)
            count[data.get('schema')] = edgepair
    schemas = []
    for aliases in res.aliases:
        nodeschemas = res.alias("_nodeSchema").asSchemas() if aliases.name == '_nodeSchema' else []
        schemas.extend(nodeschemas)
        edgeschemas = res.alias("_edgeSchema").asSchemas() if aliases.name == '_edgeSchema' else []
        schemas.extend(edgeschemas)

    for data in schemas:
        if data.name in count:
            countsum = 0
            for countiter in count.get(data.name):
                countsum += countiter.get('count')
            data.total = countsum
            data.stats = [SchemaStat(fromSchema=pairiter.get('from_schema'),
                                     toSchema=pairiter.get('to_schema'),
                                     count=pairiter.get('count'),
                                     type=DBType.DBNODE if pairiter.get(
                                         'type') in 'node' else DBType.DBEDGE if pairiter.get(
                                         'type') in 'edge' else None,
                                     name=pairiter.get('schema')
                                     )
                          for pairiter in count.get(data.name)]

    schemasresult.schema = schemas
    return schemasresult


def convertToTop(res) -> List[Process]:
    if isinstance(res.data, list) and len(res.data) > 0:
        topdata = res.data
        toplist = []
        for data in topdata:
            toplist.append(Process(
                processId=data.process_id,
                processQuery=data.process_query,
                duration=data.duration,
                status=data.status
            ))

    return toplist


def convertToAlgo(res):
    algodata = res.data
    algolist = []
    for data in algodata:
        desc = json.loads(data.get("description"))
        algolist.append(Algo(
            name=data.name,
            version=desc.param['version'],
            params=data.param['parameters'],
            description=data.get("description"),
            type=data.param['type'],
            writeSupportType=data.param['write_support_type'],
            canRollback=data.param['can_rollback'],
            configContext=data.param['config_context']
        ))

    if len(algolist) == 1:
        return algolist[0]
    else:
        return algolist


def convertToExta(res):
    from ultipa.types.types import Exta
    extadata = res.data
    extalist = []
    for data in extadata:
        extalist.append(Exta(author=data.author,
                             detail=data.detail,
                             name=data.name,
                             version=data.version))

    return extalist


def convertToLicense(res):
    return License(limitedHdc=res.get('limited_hdc'),
                   limitedShard=res.get('limited_shard'),
                   expiredDate=res.get('expired_date'))


def converToJob(obj):
    return Job(id=obj.get('job_id'), graphName=obj.get('graph_name'), type=obj.get('type'),
               query=obj.get('query'), status=obj.get('status'), errMsg=obj.get('err_msg'),
               result=json.loads(obj.get('result')) if obj.get('result') != '' else {}, startTime=obj.get('start_time'),
               endTime=obj.get('end_time'), progress=obj.get('progress'))


def converToProjection(res):
    if isinstance(res, list) and len(res) > 0:
        return [Projection(name=data.get('name'), graphName=data.get('graph_name'), status=data.get('status'),
                           stats=data.get('stats'), config=data.get('config')) for data in res]
    return res


def converToHDCGraph(res):
    if isinstance(res, list) and len(res) > 0:
        return [HDCGraph(name=data.get('name'),
                         graphName=data.get('graph_name'),
                         status=data.get('status'),
                         stats=data.get('stats'),
                         isDefault=data.get('is_default'),
                         hdcServerName=data.get('hdc_server_name'),
                         hdcServerStatus=data.get('hdc_server_status'),
                         config=data.get('config')) for data in res]
    return res
