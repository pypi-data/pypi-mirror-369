import hashlib
import os
from typing import List

from ultipa.configuration.RequestConfig import RequestConfig
from ultipa.operate.base_extra import BaseExtra
from ultipa.proto import ultipa_pb2
from ultipa.types import ULTIPA_REQUEST, ULTIPA
from ultipa.types.types_response import *
from ultipa.utils import UQLMAKER, CommandList
from ultipa.utils.fileSize import read_in_chunks
from ultipa.utils.format import FormatType


class AlgoExtra(BaseExtra):
    '''
        Processing class that defines settings for algorithm related operations.

    '''
    JSONSTRING_KEYS = ["param"]

    def __make_message(self, fileName, md5, chunk, hdcName):
        return ultipa_pb2.InstallAlgoRequest(
            file_name=fileName, md5=md5, chunk=chunk, with_server=ultipa_pb2.WithServer(hdc_server_name=hdcName)
        )

    def __generate_messages(self, request: ULTIPA_REQUEST.InstallAlgo):
        messages = []
        hdcName = request.hdcName
        for file in request.files:
            file_object = open(file, 'rb')
            filemd5 = hashlib.md5(file_object.read()).hexdigest()
            file_object.close()

            for chunk in read_in_chunks(file):
                fileName = os.path.basename(file)
                messages.append(self.__make_message(fileName, filemd5, chunk, hdcName))
        for msg in messages:
            yield msg

    def installHDCAlgo(self, files: List[str], hdcServerName: str,
                       config: RequestConfig = RequestConfig()) -> Response:
        '''
        Installs an Ultipa graph algorithm in the instance.

        Args:
            files(List[str]): 1、The directory of the algorithm package (.so)
                              2、The directory of the algorithm configuration (.yml)

            hdcServerName: The name of the hdc

            config: An object of the RequestConfig class

        Returns:
            Response

        '''
        request = ULTIPA_REQUEST.InstallAlgo(files, hdcServerName)
        clientInfo = self.getClientInfo(graphSetName=config.graph,
                                        isGlobal=True)
        response = UltipaResponse()
        try:
            if len(files) > 0:
                installRet = clientInfo.Controlsclient.InstallAlgo(self.__generate_messages(request),
                                                                   metadata=clientInfo.metadata)
                status = FormatType.status(installRet.status)
                response.status = status
        except Exception as e:
            try:
                message = str(e._state.code) + ' : ' + str(e._state.details)
            except:
                message = str(e)

            response.status = ULTIPA.Status(code=ULTIPA.ErrorCode.UNKNOW_ERROR, message=message)

        return response

    def uninstallHDCAlgo(self, algoName: str, hdcServerName: str,
                         config: RequestConfig = RequestConfig()) -> Response:
        '''
        Uninstall an Ultipa graph algorithm in the instance.

        Args:
            algoName: The name of algorithm

            hdcServerName: The name of hdc

            config: An object of the RequestConfig class

        Returns:
            Response

        '''
        clientInfo = self.getClientInfo(graphSetName=config.graph,
                                        isGlobal=True)
        arequest = ultipa_pb2.UninstallAlgoRequest(algo_name=algoName,
                                                   with_server=ultipa_pb2.WithServer(hdc_server_name=hdcServerName))
        installRet = clientInfo.Controlsclient.UninstallAlgo(arequest, metadata=clientInfo.metadata)
        status = FormatType.status(installRet.status)
        response = Response(status=status)
        return response

    def rollbackHDCAlgo(self, algoName: str, hdcServerName: str, config: RequestConfig = RequestConfig()) -> Response:
        """
        Args:
            algoName: The name of algorithm

            hdcServerName: The name of hdc

            config: An object of the RequestConfig class

        Returns:
            Response
        """
        clientInfo = self.getClientInfo(graphSetName=config.graph,
                                        isGlobal=True)
        arequest = ultipa_pb2.RollbackAlgoRequest(algo_name=algoName,
                                                  with_server=ultipa_pb2.WithServer(hdc_server_name=hdcServerName))
        rollbackRet = clientInfo.Controlsclient.RollbackAlgo(arequest, metadata=clientInfo.metadata)
        status = FormatType.status(rollbackRet.status)
        response = Response(status=status)
        return response

    def showHDCAlgo(self, hdcServerName: str, config: RequestConfig = RequestConfig()) -> List[Algo]:
        """
        Args:
            hdcServerName: The name of hdc

            config: An object of the RequestConfig class

        Returns:
            Response
        """
        if hdcServerName == "":
            return []
        command = CommandList.showHDCAlgo
        commandp = f"'{hdcServerName}'"
        uqlMaker = UQLMAKER(command=command, commandP=commandp, commonParams=config)
        res = self.uqlSingle(uqlMaker)
        if res.status.code == ULTIPA.ErrorCode.SUCCESS:
            if res.alias("_algoList").entities:
                res = res.alias(f"_algoList").asAlgos()

        return res
