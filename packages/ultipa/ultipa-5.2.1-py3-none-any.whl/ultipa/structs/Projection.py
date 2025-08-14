from ultipa.structs.BaseModel import BaseModel


class Projection(BaseModel):
    '''

        Data class for Projection

    '''

    def __init__(self, name: str = None, graphName: str = None, status: str = None, stats: str = None,
                 config: str = None):
        self.name = name
        self.graphName = graphName
        self.status = status
        self.stats = stats
        self.config = config
