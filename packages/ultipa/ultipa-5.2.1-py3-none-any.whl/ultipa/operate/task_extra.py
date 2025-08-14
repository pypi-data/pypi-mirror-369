from ultipa.configuration.RequestConfig import RequestConfig
from ultipa.operate.base_extra import BaseExtra
from ultipa.structs.Job import Job
from ultipa.structs.Process import Process
from ultipa.types import ULTIPA
from ultipa.types.types_response import *
from ultipa.utils import UQLMAKER, CommandList
from ultipa.utils.ResposeFormat import ResponseKeyFormat
from ultipa.utils.convert import convertToTop, converToJob


class ALGO_RETURN_TYPE:
    ALGO_RETURN_REALTIME = 1
    ALGO_RETURN_WRITE_BACK = 2
    ALGO_RETURN_VISUALIZATION = 4


class TaskExtra(BaseExtra):
    '''
	Processing class that defines settings for task and process related operations.
	'''

    def top(self,
            config: RequestConfig = RequestConfig()) -> List[Process]:
        '''
        Top real-time processes.

        Args:
            config: An object of RequestConfig class

        Returns:
            List[Process]

        '''
        uqlMaker = UQLMAKER(command=CommandList.top, commonParams=config)
        res = self.UqlListSimple(uqlMaker)
        if hasattr(res, 'data'):
            if len(res.data) > 0:
                res.data = convertToTop(res)

        else:
            res.data = res
        return res.data

    def kill(self, processId: str,
             config: RequestConfig = RequestConfig()) -> Response:
        '''
        Kill real-time processes.

        Args:
            processId: ID of the process to kill; set to * to kill all processes.

            config: An object of RequestConfig class

        Returns:
            Response

        '''
        commonP = processId
        uqlMaker = UQLMAKER(command=CommandList.kill, commonParams=config)
        uqlMaker.setCommandParams(commonP)
        res = self.uqlSingle(uqlMaker)
        return res

    def showJob(self, id: str = None,
                config: RequestConfig = RequestConfig()) -> List[Job]:
        '''
        Show back-end job.

        Args:
            id: ID of the job.

            config: An object of RequestConfig class

        Returns:
            List[Job]

        '''

        _jsonKeys = ['taskJson']
        uqlMaker = UQLMAKER(command=CommandList.showJob, commonParams=config)
        if id:
            commonP = int(id)
            uqlMaker.setCommandParams(commandP=commonP)
        res = self.UqlListSimple(uqlMaker=uqlMaker, responseKeyFormat=ResponseKeyFormat(jsonKeys=_jsonKeys))
        if isinstance(res, Response):
            return res
        newDatas = []
        if res.data:
            for obj in res.data:
                obj = obj.__dict__
                job = converToJob(obj)
                newDatas.append(job)
            res.data = newDatas
        return res.data

    def clearJob(self, id: str,
                 config: RequestConfig = RequestConfig()) -> Response:
        '''
        Clear back-end job.

        Args:
            id: ID of the job.

            config: An object of RequestConfig class

        Returns:
            Response

        '''

        uqlMaker = UQLMAKER(command=CommandList.clearJob, commonParams=config)

        commonP = id
        uqlMaker.setCommandParams(commandP=commonP)

        res = self.uqlSingle(uqlMaker)

        return res

    def stopJob(self, id: str,
                config: RequestConfig = RequestConfig()) -> Response:
        '''
        Stop back-end job.

        Args:
            id: The ID of back-end job

            config: An object of RequestConfig class

        Returns:
            Response

        '''
        uqlMaker = UQLMAKER(command=CommandList.stopJob, commonParams=config)
        commonP = id
        uqlMaker.setCommandParams(commandP=commonP)
        res = self.uqlSingle(uqlMaker)
        if res.status.code != ULTIPA.ErrorCode.SUCCESS:
            return Response(status=res.status, statistics=res.statistics)
        return res
