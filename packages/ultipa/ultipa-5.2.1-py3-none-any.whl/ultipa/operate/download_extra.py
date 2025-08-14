import json

from ultipa.configuration.RequestConfig import RequestConfig
from ultipa.connection.clientType import ClientType
from ultipa.operate.base_extra import BaseExtra
from ultipa.operate.task_extra import TaskExtra
from ultipa.proto import ultipa_pb2
from ultipa.types import ULTIPA
from ultipa.types.types_response import *
from ultipa.utils.format import FormatType


class DownloadExtra(BaseExtra):
    '''
    Processing class that defines settings for file downloading operation.

    '''

    def _downloadAlgoResultFile(self, fileName: str, cb: Callable[[bytes], None],
                                config: RequestConfig = RequestConfig()):
        '''
        Download file.

        Args:
            fileName: Name of the file

            cb: Callback function that accepts bytes

            config: An object of RequestConfig class

        '''
        downResponse = UltipaResponse()
        try:

            clientInfo = self.getClientInfo(graphSetName=config.graph,
                                            clientType=ClientType.Leader)
            res = clientInfo.Controlsclient.DownloadFile(
                ultipa_pb2.DownloadFileRequest(file_name=fileName), metadata=clientInfo.metadata)

            for data_flow in res:
                ultipa_response = UltipaResponse()
                status = FormatType.status(data_flow.status)
                ultipa_response.status = status
                if status.code != ULTIPA.ErrorCode.SUCCESS:
                    cb(ultipa_response)
                    break
                ultipa_response.data = data_flow.chunk
                cb(ultipa_response.data)
        except Exception as e:
            downResponse.status = ULTIPA.Status(code=ULTIPA.ErrorCode.UNKNOW_ERROR, message=str(e))
            print(downResponse.status.message)

    def downloadAlgoResultFile(self, fileName: str, cb: Callable[[bytes], None],
                               config: RequestConfig = RequestConfig()):
        '''
        Download file.

        Args:
            fileName: Name of the file

            cb:Callback function that accepts bytes

            config: An object of RequestConfig class

        '''
        return self._downloadAlgoResultFile(fileName=fileName, cb=cb, config=config)

    def _downloadAllAlgoResultFile(self, fileName: str, cb: Callable[[bytes, str], None],
                                   config: RequestConfig = RequestConfig()):
        '''
        Download all files.

        Args:
            fileName: Name of the file

            cb: Callback function that accepts bytes and string inputs

            config: An object of RequestConfig class

        '''
        downResponse = UltipaResponse()
        try:

            clientInfo = self.getClientInfo(graphSetName=config.graph,
                                            clientType=ClientType.Leader)
            res = clientInfo.Controlsclient.DownloadFile(
                ultipa_pb2.DownloadFileRequest(file_name=fileName), metadata=clientInfo.metadata)

            for data_flow in res:
                ultipa_response = UltipaResponse()
                status = FormatType.status(data_flow.status)
                ultipa_response.status = status
                if status.code != ULTIPA.ErrorCode.SUCCESS:
                    cb(ultipa_response)
                    break
                ultipa_response.data = data_flow.chunk
                cb(ultipa_response.data, fileName)
        except Exception as e:
            downResponse.status = ULTIPA.Status(code=ULTIPA.ErrorCode.UNKNOW_ERROR, message=str(e))
            print(downResponse.status.message)

    def downloadAllAlgoResultFile(self, cb: Callable[[bytes, str], None], jobId: str = None,
                                  config: RequestConfig = RequestConfig()):
        '''
        Download all files.

        Args:

            jobId: id of the jobId

            cb: callback function for receiving data

            config: An object of RequestConfig class

        '''
        result = TaskExtra.showJob(self, id=jobId)
        filename = []
        if result:
            for data in result:
                if data.id == str(jobId):
                    for key, value in json.loads(data.result).items():
                        if key[:11] == 'output_file':
                            filename.append(value)

        else:
            raise Exception('Job not found')

        for name in filename:
            self._downloadAllAlgoResultFile(fileName=name, cb=cb, config=config)
