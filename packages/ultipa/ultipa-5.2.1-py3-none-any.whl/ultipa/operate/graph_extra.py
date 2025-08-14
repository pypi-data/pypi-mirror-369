from ultipa.configuration.RequestConfig import RequestConfig
from ultipa.operate.base_extra import BaseExtra
from ultipa.structs import DBType
from ultipa.types import ULTIPA_REQUEST, ULTIPA
from ultipa.types.types_response import *
from ultipa.utils import UQLMAKER, CommandList
from ultipa.utils.ResposeFormat import ResponseKeyFormat
from ultipa.utils.convert import convertTableToDict
from ultipa.utils.convert import convertToGraph
from ultipa.utils.noneCheck import checkNone

JSONSTRING_KEYS = ["graph_privileges", "system_privileges", "policies", "policy", "privilege"]
formatdata = ['graph_privileges']
REPLACE_KEYS = {
    "graph": "name",
}


class GraphExtra(BaseExtra):
    '''
    Processing class that defines settings for GraphSet related operations.
    '''

    def showGraph(self, config: RequestConfig = RequestConfig()) -> List[GraphSet]:
        '''
        Args:
            config: An object of RequestConfig class

        Returns:
            List[GraphSet]
        '''

        uqlMaker = UQLMAKER(command=CommandList.showGraphMore, commonParams=config)
        uqlMaker.setCommandParams("")
        res = self.UqlListSimple(uqlMaker=uqlMaker, responseKeyFormat=ResponseKeyFormat(keyReplace=REPLACE_KEYS))
        if res.status.code == ULTIPA.ErrorCode.SUCCESS and len(res.data) > 0:
            res = convertToGraph(res)
        return res

    def getGraph(self, graphName: str, config: RequestConfig = RequestConfig()) -> GraphSet | None:
        '''
        Args:
            graphName: The name of GraphSet

            config: An object of RequestConfig class

        Returns:
            GraphSet
        '''

        uqlMaker = UQLMAKER(command=CommandList.showGraph, commonParams=config)
        uqlMaker.setCommandParams(graphName)
        uqlMaker.addParam(key='more', value=graphName)
        res = self.UqlListSimple(uqlMaker=uqlMaker, responseKeyFormat=ResponseKeyFormat(keyReplace=REPLACE_KEYS))
        if res.status.code == ULTIPA.ErrorCode.FAILED:
            return None
        elif res.status.code == ULTIPA.ErrorCode.SUCCESS and len(res.data) > 0:
            res = convertToGraph(res)
        return res

    def createGraph(self, graphSet: GraphSet,
                    config: RequestConfig = RequestConfig()) -> Response:
        '''
        Create a GraphSet.

        Args:
            graphSet: The graph to be created; the attribute name is mandatory, shards, partitionBy and description are optional.

            config: An object of RequestConfig class

        Returns:
            Response
        '''
        if checkNone(graphSet.name):
            return Response(status=Status(code=ErrorCode.PARAM_ERROR, message='The name of graphSet cannot be None'))
        shardslist = f" shards {[int(shard) if shard.isdigit() else 0 for shard in graphSet.shards]}" if isinstance(
            graphSet.shards, list) and len(graphSet.shards) > 0 else ''
        partitionby = f" PARTITION BY HASH({graphSet.partitionBy})" if graphSet.partitionBy is not None else ''
        comment = f" COMMENT '{graphSet.description}'" if graphSet.description else ''
        gqlMaker = CommandList.createGraphGql + f"{graphSet.name} {{ }} {partitionby} {shardslist} {comment}"
        res = self.gql(gqlMaker, config=config)
        return res

    def createGraphIfNotExist(self, graphSet: GraphSet,
                              config: RequestConfig = RequestConfig()) -> ResponseWithExistCheck:
        '''
        Checks if graph exists or not, if graph does not exist then creates new.

        Args:
            graphSet: The object of graphSet

            config: An object of RequestConfig class

        Returns:
            ResponseWithExistCheck
        '''

        if (self.hasGraph(graphSet.name, config)) == True:
            return ResponseWithExistCheck(exist=True, response=Response())

        else:
            res = self.createGraph(graphSet, config=config)
            return ResponseWithExistCheck(exist=False, response=res)

    def dropGraph(self, graphName: str,
                  config: RequestConfig = RequestConfig()) -> Response:
        '''
        Drop a GraphSet.

        Args:
            graphName: The name of GraphSet

            config: An object of RequestConfig class

        Returns:
            Response
        '''

        uqlMaker = UQLMAKER(command=CommandList.dropGraph, commonParams=config)
        uqlMaker.setCommandParams(graphName)
        res = self.uqlSingle(uqlMaker)
        return res

    def alterGraph(self, graphName: str, alterGraphSet: GraphSet,
                   config: RequestConfig = RequestConfig()) -> Response:
        '''
        Args:
            graphName: The orignal name of GraphSet

            alterGraphSet: A GraphSet object used to set the new name and/or description for the graph. the attribute name is mandatory

            config: An object of RequestConfig class

        Returns:
            Response
        '''
        if checkNone(alterGraphSet.name):
            return Response(
                status=Status(code=ErrorCode.PARAM_ERROR, message='The name of alterGraphSet cannot be None'))
        config.graph = graphName
        uqlMaker = UQLMAKER(command=CommandList.alterGraph, commonParams=config)
        uqlMaker.setCommandParams(graphName)
        data = {"name": alterGraphSet.name}
        if alterGraphSet.description is not None:
            data.update({'description': alterGraphSet.description})
        uqlMaker.addParam("set", data)
        res = self.uqlSingle(uqlMaker)
        return res

    def hasGraph(self, graphName: str, config: RequestConfig = RequestConfig()) -> bool:
        '''
        Check if graph exists or not.

        Args:
            graphName: The name of GraphSet

            config: An object of RequestConfig class

        Returns:
            bool
        '''

        graphsdata = self.showGraph(config)
        if isinstance(graphsdata, Response):
            return graphsdata
        for graphs in graphsdata:
            if (graphs.name == graphName):
                return True

        return False

    def compact(self, graphName: str, config: RequestConfig = RequestConfig()) -> JobResponse:
        '''
        Compact graphshet.

        Args:
            graphName: The name of graphset

            config: An object of RequestConfig class

        Returns:
            JobResponse

        '''
        command = CommandList.compact
        uqlMaker = UQLMAKER(command, commonParams=config)
        uqlMaker.addParam("graph", graphName)
        result = self.uqlSingle(uqlMaker)
        jobResponse = JobResponse()
        jobResponse.statistics = result.statistics
        jobResponse.status = result.status
        if result.items:
            res = convertTableToDict(result.alias(result.aliases[0].name).entities.rows,
                                     result.alias(result.aliases[0].name).entities.headers)

            jobResponse.jobId = res[0]['new_job_id']
            return jobResponse
        else:
            return jobResponse

    def truncate(self,
                 params: ULTIPA_REQUEST.TruncateParams,
                 config: RequestConfig = RequestConfig()) -> Response:
        '''
        Truncate graphset.

        Args:
            params: The truncate parameters; the attribute graphName is mandatory, schemaName and dbType are optional while they must be set together.

            config: An object of RequestConfig class.

        Returns:
            Response

        '''

        if checkNone(params.graphName):
            return Response(Status(code=ULTIPA.ErrorCode.PARAM_ERROR, message='The graphName of params cannot be None'))
        else:
            if checkNone(params.dbType) and (not checkNone(params.schemaName) or params.schemaName == '*'):
                return Response(status=ULTIPA.Status(code=ULTIPA.ErrorCode.PARAM_ERROR,
                                                     message="The schemaName and dbType of params must be set together"))
        command = CommandList.truncate
        config.graph = params.graphName
        uqlMaker = UQLMAKER(command, commonParams=config)
        uqlMaker.addParam("graph", params.graphName)

        if params.dbType is not None:
            if params.dbType == DBType.DBNODE:
                if params.schemaName == "*" or params.schemaName is None:
                    uqlMaker.addParam("nodes", "*")
                else:
                    uqlMaker.addParam("nodes", "@" + f'`{params.schemaName}`', notQuotes=True)
            if params.dbType == DBType.DBEDGE:
                if params.schemaName == "*" or params.schemaName is None:
                    uqlMaker.addParam("edges", "*")
                else:
                    uqlMaker.addParam("edges", "@" + f'`{params.schemaName}`', notQuotes=True)

        return self.uqlSingle(uqlMaker)
