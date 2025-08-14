from ultipa.configuration.RequestConfig import RequestConfig
from ultipa.operate.base_extra import BaseExtra
from ultipa.structs import DBType, checkNone
from ultipa.types.types_response import *
from ultipa.utils import UQLMAKER, CommandList
from ultipa.utils.convert import convertTableToDict


class LteUfeExtra(BaseExtra):
    '''
    Processsing class that defines settings for LTE and UFE related operations.
    '''

    def lte(self, dbType: DBType, propertyName: str, schemaName: str = None,
            config: RequestConfig = RequestConfig()) -> JobResponse:
        '''
        Load properties to memory (LTE).

        Args:
            dbType: The DBType of data (DBNODE or DBEDGE)

            schemaName: The name of schema

            propertyName: The name of property

            config: An object of RequestConfig class

        Returns:
            JobResponse
        '''
        if checkNone(propertyName):
            return Response(status=Status(code=ErrorCode.PARAM_ERROR, message='The propertyName cannot be None'))
        command = dbType == DBType.DBNODE and CommandList.lteNode or CommandList.lteEdge
        uqlMaker = UQLMAKER(command=command, commonParams=config)
        if schemaName:
            commandP = "@`%s`.`%s`" % (schemaName, propertyName)
        elif schemaName == None:
            commandP = "@`*`.`%s`" % (propertyName)
        uqlMaker.setCommandParams(commandP=commandP)
        res = self.uqlSingle(uqlMaker=uqlMaker)
        result = [{'new_job_id': ''}]
        if res.status.code == ErrorCode.SUCCESS and res.items:
            result = convertTableToDict(res.alias(res.aliases[0].name).entities.rows,
                                        res.alias(res.aliases[0].name).entities.headers)
        return JobResponse(jobId=result[0].get('new_job_id'), status=res.status, statistics=res.statistics)

    def ufe(self, dbType: DBType, propertyName: str, schemaName: str = None,
            config: RequestConfig = RequestConfig()) -> Response:
        '''
        Unload properties from memory (UFE).

        Args:
            dbType: The DBType of data (DBNODE or DBEDGE)

            schemaName: The name of schema

            propertyName: The name of property

            config: An object of RequestConfig class

        Returns:
            JobResponse
        '''
        if checkNone(propertyName):
            return Response(status=Status(code=ErrorCode.PARAM_ERROR, message='The propertyName cannot be None'))
        command = dbType == DBType.DBNODE and CommandList.ufeNode or CommandList.ufeEdge
        uqlMaker = UQLMAKER(command=command, commonParams=config)
        if schemaName:
            commandP = "@`%s`.`%s`" % (schemaName, propertyName)
        elif schemaName == None:
            commandP = "@`*`.`%s`" % (propertyName)
        uqlMaker.setCommandParams(commandP=commandP)
        res = self.uqlSingle(uqlMaker=uqlMaker)
        return res
