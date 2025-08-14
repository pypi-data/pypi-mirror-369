from ultipa.structs.BaseModel import BaseModel


class License(BaseModel):
    def __init__(self, limitedShard: str = '', limitedHdc: str = '', expiredDate: str = '',
                 licenseUUId: str = '', company: str = '', department: str = '', limitedUser: str = '',
                 limitedGraph: str = '', limitedNode: str = '',
                 limitedEdge: str = ''):
        # self.licenseUUId = licenseUUId
        # self.company = company
        # self.department = department
        # self.limitedUser = limitedUser
        # self.limitedGraph = limitedGraph
        # self.limitedNode = limitedNode
        # self.limitedEdge = limitedEdge
        self.limitedShard = limitedShard
        self.limitedHdc = limitedHdc
        self.expiredDate = expiredDate
