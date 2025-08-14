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


class EdgeExtra(BaseExtra):
    '''
    Processing class that defines settings for edge related operations.

    '''

    def insertEdges(self, edges: List[Edge], schemaName: str, config: InsertRequestConfig) -> Response:
        '''
        Insert edges.

        Args:
            edges: The list of edges to be inserted; the attributes fromId and toId of each Edge are mandatory, uuid, fromUuid, and toUuid cannot be set.

            schemaName: Name of the schema

            config: An object of InsertRequestConfig class

        Returns:
            Response
        '''
        combined_values = []  # to combine values and id for insertion
        for edge in edges:
            if checkNone(edge.fromId) or checkNone(edge.toId):
                return Response(
                    status=Status(code=ErrorCode.PARAM_ERROR, message='The fromId and toId of edge cannot be None'))
            edge_dict = {}
            if edge.fromId:
                edge_dict["_from"] = edge.fromId
            if edge.toId:
                edge_dict["_to"] = edge.toId

            if edge.fromUuid:
                edge_dict["_from_uuid"] = edge.fromUuid
            if edge.toUuid:
                edge_dict["_to_uuid"] = edge.toUuid

            if edge.uuid:
                edge_dict["_uuid"] = edge.uuid
            edge_dict.update(edge.values)
            combined_values.append(edge_dict)
        edges = combined_values
        schemaName = '@' + schemaName

        uqlMaker = UQLMAKER(command=CommandList.insert, commonParams=config)
        if config.insertType == InsertType.UPSERT:
            uqlMaker = UQLMAKER(command=CommandList.upsert, commonParams=config)
        if config.insertType == InsertType.OVERWRITE:
            uqlMaker.addParam('overwrite', "", required=False)
        if schemaName:
            uqlMaker.addParam('into', schemaName, required=False)
        uqlMaker.addParam('edges', edges)

        if config.silent == False:
            uqlMaker.addParam('as', "edges")
            uqlMaker.addParam('return', "edges{*}")
        res = self.uqlSingle(uqlMaker)
        return res

    def insertEdgesBatchBySchema(self, schema: Schema, edges: List[Edge],
                                 config: InsertRequestConfig) -> InsertResponse | Response:
        '''
        Batch insert edges of a same schema (that already exists in the graph)

        Args:
            schema: The target schema; the attributes name and dbType are mandatory, properties should include some or all properties.

            edges: The list of edges to be inserted; the attributes fromId and toId of each Edge are mandatory, uuid, fromUuid, and toUuid cannot be set, values must have the same structure with Schema.properties.

            config: An object of InsertConfig class

        Returns:
            InsertResponse

        '''
        if checkNone(schema.name) or not isinstance(schema.properties, list):
            messege = 'The name of schema cannot be None' if checkNone(
                schema.name) else 'The properties type of schema must be list'
            return Response(status=Status(code=ErrorCode.PARAM_ERROR, message=messege))
        if config.graph == '' and self.defaultConfig.defaultGraph != '':
            config.graph = self.defaultConfig.defaultGraph

        clientInfo = self.getClientInfo(clientType=ClientType.Update, graphSetName=config.graph)

        edgetable = FormatType.makeEntityEdgeTable(schema, edges,getTimeZoneOffset(requestConfig=config,
                                                                                    defaultConfig=self.defaultConfig))

        _edgeTable = ultipa_pb2.EntityTable(schemas=edgetable.schemas, entity_rows=edgetable.edgeRows)
        request = ultipa_pb2.InsertEdgesRequest()
        request.silent = config.silent
        request.insert_type = config.insertType.value
        request.graph_name = config.graph
        request.edge_table.MergeFrom(_edgeTable)
        res = clientInfo.Rpcsclient.InsertEdges(request, metadata=clientInfo.metadata)

        status = FormatType.status(res.status)
        uqlres = InsertResponse(status=status)
        reTry = RetryHelp.check(self, config, uqlres)
        if reTry.canRetry:
            return self.insertEdgesBatchBySchema(schema, edges, config)

        uqlres.uuids = [i for i in res.uuids]
        errorDict = {}
        for i, data in enumerate(res.ignore_error_code):
            try:
                index = edges[res.ignore_indexes[i]]._getIndex()
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

    def insertEdgesBatchAuto(self, edges: List[Edge],
                             config: InsertRequestConfig) -> Dict[str, InsertResponse]:
        '''
        Batch insert edges of different schemas (that will be created if not existent)

        Args:
            edges: The data to be inserted, List[Edge]

            config: An object of InsertConfig class

        Returns:
            Dict[str,InsertResponse]

        '''
        Result = {}
        schemaDict = {}
        batches = {}
        schemaRet = self.uql(GetPropertyBySchema.edge, config)
        if schemaRet.status.code == ULTIPA.ErrorCode.SUCCESS:
            for aliase in schemaRet.aliases:
                if aliase.name == '_edgeSchema':
                    schemaDict = convertTableToDict(schemaRet.alias(aliase.name).entities.rows,
                                                    schemaRet.alias(aliase.name).entities.headers)
            if not schemaDict:
                raise ParameterException(err='Please create Edge Schema.')
        else:
            raise ParameterException(err=schemaRet.status.message)
        for index, edge in enumerate(edges):
            edge._index = index
            if batches.get(edge.schema) == None:
                batches[edge.schema] = ULTIPA_REQUEST.Batch()
                propertyList = []
                find = list(filter(lambda x: x.get('name') == edge.schema, schemaDict))
                if find:
                    findSchema = find[0]
                    # propertyList = FormatType.checkProperty(edge, json.loads(findSchema.get("properties")))
                    propertyDics = json.loads(findSchema.get("properties"))
                    for schemaProperty in propertyDics:
                        reqProperty = Property(schemaProperty.get("name"), type=None)
                        reqProperty.setTypeInt(schemaProperty.get("type"))
                        propertyList.append(reqProperty)
                    reqSchema = ULTIPA_REQUEST.Schema(name=edge.schema, properties=propertyList, dbType=DBType.DBEDGE)
                    batches[edge.schema].Schema = reqSchema
                else:
                    if edge.schema is None:
                        raise ParameterException(err=f"Row [{index}]:Please set schema name for edge.")
                    else:
                        raise ParameterException(err=f"Row [{index}]:Edge Schema not found {edge.schema}.")
            batches.get(edge.schema).Edges.append(edge)
        for key in batches:
            batch = batches.get(key)
            ret = self.insertEdgesBatchBySchema(schema=batch.Schema, edges=batch.Edges, config=config)
            Result.update({key: ret})
        return Result
