from ultipa.configuration import RequestConfig
from ultipa.operate.base_extra import BaseExtra
from ultipa.structs.HDC import HDCGraph
from ultipa.types import ULTIPA
from ultipa.types.types import HDCBuilder
from ultipa.types.types_response import *
from ultipa.utils import CommandList, UQLMAKER
from ultipa.utils.convert import convertTableToDict, converToHDCGraph

REPLACE_KEYS = {
    "graph": "name",
}


class HDCExtra(BaseExtra):
    '''
    	Processing class that defines settings for HDC related operations.
    '''

    def createHDCGraphBySchema(self,
                               builder: HDCBuilder,
                               config: RequestConfig = RequestConfig()) -> JobResponse:
        '''
        create HDCGraph

        Args:
            builder: The object of HDCBuilder

            config: An object of RequestConfig class

        Returns:
            JobResponse
        '''

        command = CommandList.createHDCGraph
        uqlmarker = UQLMAKER(command=command, commonParams=config)

        def getschemalist(schemas: []):
            schemalist = []
            for data in schemas:
                for key, value in data.items():
                    if key == '*':
                        schemalist.append(f'"{key}":{value}')
                    else:
                        schemalist.append(f'{key}:{value}')
            return schemalist

        nodeSchemas = ','.join(getschemalist(builder.nodeSchema))
        edgeSchemas = ','.join(getschemalist(builder.edgeSchema))
        commP = '{nodes:{%s},edges:{%s},direction:"%s",load_id:%s,update:"%s",query:"query",default:%s}' % (
            nodeSchemas, edgeSchemas, builder.direction.value, str(builder.loadId).lower(), builder.syncType,
            str(builder.isDefault).lower())

        uqlmarker.setCommandParams([builder.hdcGraphName, commP])
        uqlmarker.addParam(key='to', value=f'{builder.hdcServerName}')
        res = self.uqlSingle(uqlmarker)
        result = [{'new_job_id': ''}]
        if res.status.code == ErrorCode.SUCCESS and res.items:
            result = convertTableToDict(res.alias(res.aliases[0].name).entities.rows,
                                        res.alias(res.aliases[0].name).entities.headers)

        return JobResponse(jobId=result[0].get('new_job_id'), status=res.status, statistics=res.statistics)

    def showHDCGraph(self, config: RequestConfig = RequestConfig()) -> List[HDCGraph]:

        '''
        show HDCGraph

        Args:

            config: An object of RequestConfig class

        Returns:
            List[HDCGraph]
        '''

        command = CommandList.showHDCGraph
        uqlmaker = UQLMAKER(command=command, commonParams=config)
        uqlmaker.setCommandParams("")
        res = self.uqlSingle(uqlmaker)
        if res.status.code == ULTIPA.ErrorCode.SUCCESS:
            if res.aliases:
                proj = convertTableToDict(res.alias(res.aliases[0].name).entities.rows,
                                          res.alias(res.aliases[0].name).entities.headers)
                projres = converToHDCGraph(proj)
                return projres
        return res

    def dropHDCGraph(self, hdcGraphName: str, config: RequestConfig = RequestConfig()) -> Response:

        '''
        drop HDCGraph

        Args:

            hdcGraphName: The name of HDCGraph

            config: An object of RequestConfig class

        Returns:
            Response
        '''

        command = CommandList.dropHDCGraph
        uqlmaker = UQLMAKER(command=command, commonParams=config)
        uqlmaker.setCommandParams(hdcGraphName)
        res = self.uqlSingle(uqlmaker)
        return res
