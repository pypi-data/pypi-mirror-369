from ultipa.structs.BaseModel import BaseModel


class HDCGraph(BaseModel):
    '''
        Data class for HDCGraph.
    '''

    def __init__(self,
                 name: str = None,
                 graphName: str = None,
                 status: str = None,
                 stats: str = None,
                 isDefault: str = None,
                 hdcServerName: str = None,
                 hdcServerStatus: str = None,
                 config: str = None):
        self.name = name
        self.isDefault = isDefault
        self.graphName = graphName
        self.status = status
        self.stats = stats
        self.hdcServerName = hdcServerName
        self.hdcServerStatus = hdcServerStatus
        self.config = config


class HDCSyncType(BaseModel):
    SYNC = "sync"
    ASYNC = "async"
    STATIC = "static"
