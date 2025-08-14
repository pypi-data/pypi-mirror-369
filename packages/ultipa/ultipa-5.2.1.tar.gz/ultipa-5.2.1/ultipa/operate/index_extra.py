from ultipa.configuration.RequestConfig import RequestConfig
from ultipa.operate.base_extra import BaseExtra
from ultipa.structs.DBType import DBType
from ultipa.types.types_response import *
from ultipa.types.types_response import JobResponse
from ultipa.utils import UQLMAKER, CommandList
from ultipa.utils.convert import convertTableToDict, convertToIndex, convertToFullText
from ultipa.utils.format import FormatType
from ultipa.utils.noneCheck import checkNone


class IndexExtra(BaseExtra):
    '''
	Processing class that defines settings for index related operations.
	'''

    def showIndex(self,
                  config: RequestConfig = RequestConfig()) -> List[Index]:
        '''
        Show all Index.

        Args:

            config: An object of RequestConfig class

        Returns:
            List[Index]
        '''
        command = CommandList.showIndex
        uqlMaker = UQLMAKER(command=command, commonParams=config)
        res = self.UqlListSimple(uqlMaker=uqlMaker, isSingleOne=False)
        if isinstance(res, Response):
            return res
        indexdata = convertToIndex(res=res, all=True)
        if len(indexdata) > 0:
            res.data = indexdata
        else:
            res.data = []
        return res.data

    def showNodeIndex(self, config: RequestConfig = RequestConfig()) -> List[Index]:
        '''
        Show all Node index.

        Args:
            config: An object of RequestConfig class

        Returns:
            List[Index]
        '''
        command = CommandList.showNodeIndex
        uqlMaker = UQLMAKER(command=command, commonParams=config)
        res = self.UqlListSimple(uqlMaker=uqlMaker, isSingleOne=False)
        if isinstance(res, Response):
            return res
        indexdata = convertToIndex(res=res, all=False, dbtype=DBType.DBNODE)
        if len(indexdata) > 0:
            res.data = indexdata
        else:
            res.data = []
        return res.data

    def showEdgeIndex(self, config: RequestConfig = RequestConfig()) -> List[Index]:
        '''
        Show all Edge index.

        Args:
            config: An object of RequestConfig class

        Returns:
            List[Index]
        '''

        command = CommandList.showEdgeIndex
        uqlMaker = UQLMAKER(command=command, commonParams=config)
        res = self.UqlListSimple(uqlMaker=uqlMaker, isSingleOne=False)
        if isinstance(res, Response):
            return res
        indexdata = convertToIndex(res=res, all=False, dbtype=DBType.DBEDGE)
        if len(indexdata) > 0:
            res.data = indexdata
        else:
            res.data = []
        return res.data

    def showFulltext(self,
                     config: RequestConfig = RequestConfig()) -> List[Index]:
        '''
        Show all full-text index.

        Args:
            config: An object of RequestConfig class
        Returns:

            List[Index]
        '''
        command = CommandList.showFulltext
        uqlMaker = UQLMAKER(command=command, commonParams=config)
        res = self.UqlListSimple(uqlMaker=uqlMaker, isSingleOne=False)
        if isinstance(res, Response):
            return res
        fulltextdata = convertToFullText(res=res)
        if len(fulltextdata) > 0:
            res.data = fulltextdata
        else:
            res.data = []
        return res.data

    def createIndex(self, dbType: DBType, source: str, indexName: str,
                    config: RequestConfig = RequestConfig()) -> JobResponse:
        '''
        Create an index.

        Args:
            dbType: The DBType of data (DBNODE or DBEDGE)

            indexName: The name of index

            source: Property Related Information

            config: An object of RequestConfig class

        Returns:
            JobResponse
        '''
        response = Response()
        if FormatType.checkNone(dbType) or FormatType.checkNone(source) or FormatType.checkNone(
                indexName) or dbType == DBType.DBGLOBAL:
            message = 'The dbType cannot be None' if FormatType.checkNone(dbType) \
                else 'The source cannot be None' if FormatType.checkNone(
                source) else 'The indexName cannot be None' if FormatType.checkNone(
                source) else 'The dbType cannot be DBTYPE.DBGLOBAL'

            response.status = Status(code=ErrorCode.FAILED, message=message)

            return response
        command = dbType == DBType.DBNODE and CommandList.createNodeIndex or CommandList.createEdgeIndex
        uqlMaker = UQLMAKER(command=command, commonParams=config)
        source = f'{source}'
        uqlMaker.setCommandParams([source, indexName])
        res = self.uqlSingle(uqlMaker=uqlMaker)
        result = [{'new_job_id': ''}]
        if res.status.code == ErrorCode.SUCCESS and res.items:
            result = convertTableToDict(res.alias(res.aliases[0].name).entities.rows,
                                        res.alias(res.aliases[0].name).entities.headers)

        return JobResponse(jobId=result[0].get('new_job_id'), status=res.status, statistics=res.statistics)

    def createNodeIndex(self, source: str, indexName: str,
                        config: RequestConfig = RequestConfig()) -> JobResponse:
        '''
        Create an node index.

        Args:
            source: Property Related Information

            indexName: The name of index

            config: An object of RequestConfig class

        Returns:
            JobResponse
        '''
        return self.createIndex(dbType=DBType.DBNODE, source=source, indexName=indexName, config=config)

    def createEdgeIndex(self, source: str, indexName: str,
                        config: RequestConfig = RequestConfig()) -> JobResponse:
        '''
        Create an edge index.

        Args:
            source: Property Related Information

            indexName: The name of index

            config: An object of RequestConfig class

        Returns:
            JobResponse
        '''

        return self.createIndex(dbType=DBType.DBEDGE, source=source, indexName=indexName, config=config)

    def createFulltext(self, dbType: DBType, schemaName: str, propertyName: str, indexName: str,
                       config: RequestConfig = RequestConfig()) -> JobResponse:
        '''
        Create an full-text index.

        Args:
            dbType: The DBType of data (DBNODE or DBEDGE)

            schemaName: The name of schema

            propertyName: An object of propertyName

            indexName: Name of the fulltext index

            config: An object of RequestConfig class

        Returns:
            JobResponse

        '''
        if checkNone(schemaName) or checkNone(propertyName) or checkNone(indexName):
            message = 'The schemaName cannot be None' if checkNone(
                schemaName) else 'The propertyName cannot be None' if checkNone(
                propertyName) else 'The indexName cannot be None'
            return Response(status=Status(code=ErrorCode.PARAM_ERROR, message=message))
        command = dbType == DBType.DBNODE and CommandList.createNodeFulltext or CommandList.createEdgeFulltext
        command1 = "@`%s`.`%s`" % (schemaName, propertyName)
        commandP = [command1, indexName]
        uqlMaker = UQLMAKER(command=command, commonParams=config)
        uqlMaker.setCommandParams(commandP=commandP)
        res = self.uqlSingle(uqlMaker=uqlMaker)
        result = [{'new_job_id': ''}]
        if res.status.code == ErrorCode.SUCCESS:
            result = convertTableToDict(res.alias('result').entities.rows, res.alias('result').entities.headers)

        return JobResponse(jobId=result[0].get('new_job_id'), status=res.status, statistics=res.statistics)

    def createNodeFulltext(self, schemaName: str, propertyName: str, indexName: str,
                           config: RequestConfig = RequestConfig()) -> JobResponse:
        '''
        Create an node full-text index.

        Args:

            schemaName: The name of schema

            propertyName: An name of property

            indexName: Name of the fulltext index

            config: An object of RequestConfig class

        Returns:
            JobResponse

        '''
        return self.createFulltext(dbType=DBType.DBNODE, schemaName=schemaName, propertyName=propertyName,
                                   indexName=indexName, config=config)

    def createEdgeFulltext(self, schemaName: str, propertyName: str, indexName: str,
                           config: RequestConfig = RequestConfig()) -> JobResponse:
        '''
        Create an edge full-text index.

        Args:

            schemaName: The name of schema

            propertyName: An name of property

            indexName: Name of the fulltext index

            config: An object of RequestConfig class

        Returns:
            JobResponse

		'''
        return self.createFulltext(dbType=DBType.DBEDGE, schemaName=schemaName, propertyName=propertyName,
                                   indexName=indexName, config=config)

    def dropIndex(self, dbType: DBType, indexName: str,
                  config: RequestConfig = RequestConfig()) -> Response:
        '''
        Drop an index.

        Args:
            dbType: The DBType of data (DBNODE or DBEDGE)

            indexName: The name of index

            config: An object of RequestConfig class

        Returns:
            Response
        '''
        command = dbType == DBType.DBNODE and CommandList.dropNodeIndex or CommandList.dropEdgeIndex
        commandP = f'"{indexName}"'

        uqlMaker = UQLMAKER(command=command, commandP=commandP, commonParams=config)
        res = self.uqlSingle(uqlMaker=uqlMaker)
        return res

    def dropNodeIndex(self, indexName: str,
                      config: RequestConfig = RequestConfig()) -> Response:
        '''
        Drop an node index.

        Args:
            indexName: The name of index

            config: An object of RequestConfig class

        Returns:
            Response
        '''
        return self.dropIndex(dbType=DBType.DBNODE, indexName=indexName, config=config)

    def dropEdgeIndex(self, indexName: str,
                      config: RequestConfig = RequestConfig()) -> Response:
        '''
        Drop an edge index.

        Args:
            indexName: The name of index

            config: An object of RequestConfig class

        Returns:
            Response
        '''

        return self.dropIndex(dbType=DBType.DBEDGE, indexName=indexName, config=config)

    def dropFulltext(self, dbType: DBType, fulltextName: str,
                     config: RequestConfig = RequestConfig()) -> Response:
        '''
        Drop an full-text index.

        Args:
            dbType: The DBType of data (DBNODE or DBEDGE)

            fulltextName: The name of the fulltext index

            config: An object of RequestConfig class

        Returns:
            Response
        '''

        command = dbType == DBType.DBNODE and CommandList.dropNodeFulltext or CommandList.dropEdgeFulltext
        uqlMaker = UQLMAKER(command=command, commonParams=config)
        uqlMaker.setCommandParams(fulltextName)
        res = self.uqlSingle(uqlMaker=uqlMaker)
        return res

    def showNodeFulltext(self, config: RequestConfig = RequestConfig()) -> List[Index]:
        '''
        Show all full-text Node index.

        Args:

            config: An object of RequestConfig class

        Returns:

            List[Index]
        '''
        command = CommandList.showNodeFulltext
        uqlMaker = UQLMAKER(command=command, commonParams=config)
        res = self.UqlListSimple(uqlMaker=uqlMaker, isSingleOne=False)
        if isinstance(res, Response):
            return res
        fulltextdata = convertToFullText(res=res, all=False, dbtype=DBType.DBNODE)
        if len(fulltextdata) > 0:
            res.data = fulltextdata
        else:
            res.data = []
        return res.data

    def showEdgeFulltext(self, config: RequestConfig = RequestConfig()) -> List[Index]:
        '''
        Show all full-text Edge index.

        Args:

            config: An object of RequestConfig class

        Returns:

            List[Index]
        '''
        command = CommandList.showEdgeFulltext
        uqlMaker = UQLMAKER(command=command, commonParams=config)
        res = self.UqlListSimple(uqlMaker=uqlMaker, isSingleOne=False)
        if isinstance(res, Response):
            return res
        fulltextdata = convertToFullText(res=res, all=False, dbtype=DBType.DBEDGE)
        if len(fulltextdata) > 0:
            res.data = fulltextdata
        else:
            res.data = []
        return res.data
