import json

from ultipa.configuration import InsertRequestConfig
from ultipa.connection.clientType import ClientType
from ultipa.connection.commonUql import GetPropertyBySchema
from ultipa.operate.base_extra import BaseExtra
from ultipa.proto import ultipa_pb2
from ultipa.structs import DBType
from ultipa.structs.InsertErrorCode import InsertErrorCodeMap
from ultipa.structs.InsertType import InsertType
from ultipa.types import ULTIPA, ULTIPA_REQUEST
from ultipa.types.types_response import *
from ultipa.types.types_response import InsertResponse, Response
from ultipa.utils import CommandList
from ultipa.utils import UQLMAKER
from ultipa.utils.convert import convertTableToDict
from ultipa.utils.errors import ParameterException
from ultipa.utils.format import FormatType
from ultipa.utils.noneCheck import checkNone
from ultipa.utils.raftRetry import RetryHelp
from ultipa.utils.ultipa_datetime import getTimeZoneOffset


class NodeExtra(BaseExtra):
    '''
    Processing class that defines settings for node related operations.

    '''

    def insertNodes(self, nodes: List[Node], schemaName: str, config: InsertRequestConfig) -> Response:
        '''
        Insert nodes.

        Args:
            nodes: List of nodes to be inserted

            schemaName: The name of the Schema

            config: An object of InsertConfig class

        Returns:
            Response
        '''

        combined_values = []
        for node in nodes:
            node_dict = {}
            if node.id:
                node_dict['_id'] = node.id
            node_dict.update(node.values)
            combined_values.append(node_dict)

        nodes = combined_values
        schemaName = '@' + schemaName

        uqlMaker = UQLMAKER(command=CommandList.insert, commonParams=config)
        if config.insertType == InsertType.UPSERT:
            uqlMaker = UQLMAKER(command=CommandList.upsert, commonParams=config)
        if config.insertType == InsertType.OVERWRITE:
            uqlMaker.addParam('overwrite', "", required=False)
        if schemaName:
            uqlMaker.addParam('into', schemaName, required=False)

        uqlMaker.addParam('nodes', nodes)

        if config.silent == False:
            uqlMaker.addParam('as', "nodes")
            uqlMaker.addParam('return', "nodes{*}")

        res = self.uqlSingle(uqlMaker)
        return res

    def insertNodesBatchBySchema(self, schema: Schema, nodes: List[Node],
                                 config: InsertRequestConfig) -> InsertResponse | Response:
        '''
        Batch insert nodes of a same schema (that already exists in the graph).

        Args:
            schema:  The target schema; the attributes name and dbType are mandatory, properties should include some or all properties.

            nodes: The data to be inserted, List[Node]

            config: An object of InsertConfig class

        Returns:
            InsertResponse

        '''

        if checkNone(schema.name) or not isinstance(schema.properties, list):
            message = 'The name of schema cannot be None' if checkNone(
                schema.name) else 'The properties type of schema must be list'
            return Response(status=Status(code=ErrorCode.PARAM_ERROR, message=message))

        if config.graph == '' and self.defaultConfig.defaultGraph != '':
            config.graph = self.defaultConfig.defaultGraph

        clientInfo = self.getClientInfo(clientType=ClientType.Update, graphSetName=config.graph)

        nodetable = FormatType.makeEntityNodeTable(schema, nodes, getTimeZoneOffset(requestConfig=config,
                                                                                    defaultConfig=self.defaultConfig))

        _nodeTable = ultipa_pb2.EntityTable(schemas=nodetable.schemas, entity_rows=nodetable.nodeRows)
        request = ultipa_pb2.InsertNodesRequest()
        request.silent = config.silent
        request.insert_type = config.insertType.value
        request.graph_name = config.graph
        request.node_table.MergeFrom(_nodeTable)
        res = clientInfo.Rpcsclient.InsertNodes(request, metadata=clientInfo.metadata)

        status = FormatType.status(res.status)
        uqlres = InsertResponse(status=status)
        reTry = RetryHelp.check(self, config, uqlres)
        if reTry.canRetry:
            return self.insertNodesBatchBySchema(schema, nodes, config)

        uqlres.uuids = [i for i in res.uuids]
        uqlres.ids = [i for i in res.ids]
        errorDict = {}
        for i, data in enumerate(res.ignore_error_code):
            try:
                index = nodes[res.ignore_indexes[i]]._getIndex()
            except Exception as e:
                try:
                    index = res.ignore_indexes[i]
                except Exception as e:
                    index = i
            if index is None:
                try:
                    index = res.ignore_indexes[i]
                except Exception as e:
                    index = i
            errorDict.update({index: InsertErrorCodeMap.getUnsertErrorCode(data)})
        uqlres.errorItems = {key: errorDict[key] for key in sorted(errorDict.keys())}
        return uqlres

    def insertNodesBatchAuto(self, nodes: List[Node],
                             config: InsertRequestConfig) -> Dict[str, InsertResponse]:
        '''
        Batch insert nodes of different schemas (that will be created if not existent)

        Args:
            nodes: The data to be inserted, List[Node]

            config: An object of InsertConfig class

        Returns:
            Dict[str,InsertResponse]

        '''
        Result = {}
        schemaDict = {}
        batches = {}
        schemaRet = self.uql(GetPropertyBySchema.node, config)
        if schemaRet.status.code == ULTIPA.ErrorCode.SUCCESS:
            for aliase in schemaRet.aliases:
                if aliase.name == '_nodeSchema':
                    schemaDict = convertTableToDict(schemaRet.alias(aliase.name).entities.rows,
                                                    schemaRet.alias(aliase.name).entities.headers)
            if not schemaDict:
                raise ParameterException(err='Please create Node Schema.')
        else:
            raise ParameterException(err=schemaRet.status.message)
        for index, node in enumerate(nodes):
            node._index = index
            if batches.get(node.schema) is None:
                batches[node.schema] = ULTIPA_REQUEST.Batch()
                propertyList = []
                find = list(filter(lambda x: x.get('name') == node.schema, schemaDict))
                if find:
                    findSchema = find[0]
                    # propertyList = FormatType.checkProperty(node, json.loads(findSchema.get("properties")))
                    propertyDics = json.loads(findSchema.get("properties"))
                    for schemaProperty in propertyDics:
                        reqProperty = Property(schemaProperty.get("name"), type=None)
                        reqProperty.setTypeInt(schemaProperty.get("type"))
                        propertyList.append(reqProperty)
                    reqSchema = ULTIPA_REQUEST.Schema(name=node.schema, properties=propertyList, dbType=DBType.DBNODE)
                    batches[node.schema].Schema = reqSchema
                else:
                    if node.schema is None:
                        raise ParameterException(err=f"Row [{index}]:Please set schema name for node.")
                    else:
                        raise ParameterException(err=f"Row [{index}]:Node Schema not found {node.schema}.")

            batches.get(node.schema).Nodes.append(node)
        for key in batches:
            batch = batches.get(key)
            ret = self.insertNodesBatchBySchema(schema=batch.Schema, nodes=batch.Nodes, config=config)
            Result.update({key: ret})
        return Result
