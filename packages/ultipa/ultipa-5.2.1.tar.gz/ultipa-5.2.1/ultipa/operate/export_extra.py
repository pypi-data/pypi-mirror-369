from typing import Callable, List
from ultipa.configuration.RequestConfig import RequestConfig
from ultipa.operate.base_extra import BaseExtra
from ultipa.structs.Edge import Edge
from ultipa.structs.Node import Node
from ultipa.types.types_request import ExportRequest


class ExportExtra(BaseExtra):
    '''
        Processing class that defines settings for data exporting operation.
    '''

    def export(self, exportRequest: ExportRequest, cb: Callable[[List[Node], List[Edge]], None],
               config: RequestConfig = RequestConfig()):
        '''
        Export data.

        Args:
            exportRequest: An object of ExportRequest class

            cb: callback function for receiving data

            config: An object of RequestConfig class

        Returns:
            Stream
        '''
        self.exportData(exportRequest, cb, config)
        return
