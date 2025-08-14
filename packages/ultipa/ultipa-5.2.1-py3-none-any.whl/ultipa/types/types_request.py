from ultipa.structs import DBType
from ultipa.structs.Schema import Schema
from ultipa.types import ULTIPA
from ultipa.utils.ufilter.new_ufilter import *


class CommonSchema:
    '''
        Data calss for schema with name and description.
    '''

    def __init__(self, schema: str, property: str):
        self.schemaName = '@' + schema
        self.propertyName = property

    @property
    def toString(self):
        return "%s.%s" % (self.schemaName, self.propertyName)


class UltipaPath:
    def __init__(self, nodeSchema: List[CommonSchema], edgeSchema: List[CommonSchema]):
        self.nodeSchema = nodeSchema
        self.edgeSchema = edgeSchema

    @property
    def toString(self):
        if self.nodeSchema == '*':
            nodeSchema = '*'
        else:
            nodeSchema = ','.join([i.toString for i in self.nodeSchema])

        if self.edgeSchema == '*':
            edgeSchema = '*'
        else:
            edgeSchema = ','.join([i.toString for i in self.edgeSchema])

        return "{%s}{%s}" % (nodeSchema, edgeSchema)


class Return:
    def __init__(self, alias: str, propertys: List[str] = None, allProperties: bool = False, limit: int = 1):
        if propertys is None:
            propertys = []
        self.aliasName = alias
        self.propertys = propertys
        self.all = allProperties
        self.limit = limit

    @property
    def toString(self):
        if self.all:
            return "%s{%s} limit %s" % (self.aliasName, "*", self.limit)
        if len(self.propertys) == 1:
            return "%s.%s limit %s" % (self.aliasName, self.propertys[0], self.limit)
        else:
            return "%s{%s} limit %s" % (self.aliasName, ','.join(self.propertys), self.limit)


class CreateUser:
    def __init__(self, username: str, password: str, graphPrivileges: [dict] = None,
                 systemPrivileges: List[str] = None, propertyPrivileges: dict = None, policies: List[str] = None):
        self.username = username
        self.password = password
        self.graph_privileges = graphPrivileges
        self.system_privileges = systemPrivileges
        self.policies = policies
        self.property_privileges = propertyPrivileges


class AlterUser(CreateUser):
    def __init__(self, username: str, password: str = None, graphPrivileges: [dict] = None,
                 systemPrivileges: List[str] = None, propertyPrivileges: dict = None, policies: List[str] = None):
        super().__init__(username, password, graphPrivileges, systemPrivileges, propertyPrivileges, policies)


class getUserSetting():
    def __init__(self, username: str, type: str = ''):
        self.username = username
        self.type = type


class setUserSetting(getUserSetting):
    def __init__(self, username: str, type: str = '', data: str = ''):
        super().__init__(username, type)
        self.data = data


# class ShowTask:
# 	def __init__(self, id: int = None, name: str = None, limit: int = None, status: str = ''):
# 		self.id = id
# 		self.limit = limit
# 		self.name = name
# 		self.status = status


# class ClearTask:
# 	def __init__(self, id: int = None, name: str = None, status: str = None, all: bool = False):
# 		self.id = id
# 		self.name = name
# 		self.status = status
# 		self.all = all


# class InsertNodes:
# 	def __init__(self, nodes: List[Node], schemaName: str, config:InsertConfig):
# 		combined_values=[] #to combine values and id for insertion
# 		for node in nodes:
# 			combined_values.append({
# 				"_id":node.id,
# 				**node.values
# 			})

# 		self.nodes = combined_values
# 		self.schemaName = '@' + schemaName
# 		self.insertType=config.insertType
# 		self.silent = config.silent

# 	def setSchema(self, schema: str):
# 		self.schemaName = '@' + schema


# class InsertEdges:
# 	def __init__(self, edges: List[Edge], schemaName: str, config:InsertConfig):
# 		combined_values=[] #to combine values and id for insertion
# 		for edge in edges:
# 			combined_values.append({
# 				**edge.values,
# 				'_from':edge.from_id,
# 				'_to':edge.to_id
# 			})
# 		self.edges=combined_values
# 		self.schemaName = '@' + schemaName
# 		self.insertType=config.insertType
# 		self.silent=config.silent

# 	def setSchema(self, schema: str):
# 		self.schemaName = '@' + schema


class SearchNode:
    def __init__(self, select: Return, id=None,
                 filter: UltipaFilter or list or str = None):
        if id is None:
            id = []
        self.id = id
        self.filter = filter
        self.select = select


class SearchEdge(SearchNode):
    pass


class UpdateNode:
    def __init__(self, values: dict, uuid: [int] = None, filter: UltipaFilter = None, silent: bool = False):
        if uuid is None:
            uuid = []
        self.id = uuid
        self.filter = filter
        self.values = values
        self.silent = silent


class UpdateEdge(UpdateNode):
    pass


class DeleteNode:
    def __init__(self, uuid: [int] = None, filter: UltipaFilter = None, silent: bool = False):
        if uuid is None:
            uuid = []
        self.id = uuid
        self.filter = filter
        self.silent = silent


class DeleteEdge(DeleteNode):
    pass


# class LTE:
# 	def __init__(self, schemaName: CommonSchema, type: DBType):
# 		'''LTE UFE Node and Edge property'''
# 		self.schemaName = schemaName
# 		self.type = type


# class UFE(LTE):
# 	...


class Index(CommonSchema):
    def __init__(self, type: DBType, schema: str, property: str):
        super().__init__(schema=schema, property=property)
        self.DBtype = type


class CreateIndex(Index):
    def __init__(self, type: DBType, schema: str, property: str):
        super().__init__(type, schema, property)


class CreateFulltext(Index):
    def __init__(self, type: DBType, schema: str, property: str, name: str):
        super().__init__(type, schema, property)
        self.name = name


class DropIndex(Index):
    def __init__(self, type: DBType, schema: str, property: str):
        super().__init__(type, schema, property)


class DropFulltext:
    def __init__(self, type: DBType, name: str = ""):
        self.fulltextName = name
        self.DBtype = type


#
# class Download:
# 	def __init__(self, fileName: str, taskId: str, savePath: str = None):
# 		self.fileName = fileName
# 		self.taskId = taskId
# 		self.savePath = savePath
#
#
# class CreatePolicy(Policy):
# 	pass
#
#
# class AlterPolicy(Policy):
# 	pass
#

class GetPolicy:
    def __init__(self, name: str):
        self.name = name


class DropPolicy(GetPolicy):
    pass


# class GrantPolicy:
# 	def __init__(self, username: str = '', graphPrivileges: dict = None,
# 				 systemPrivileges: List[str] = None, policies: List[str] = None):
# 		self.username = username
# 		self.graph_privileges = graphPrivileges
# 		self.system_privileges = systemPrivileges
# 		self.policies = policies


# class RevokePolicy(GrantPolicy):
# 	pass


class ExportRequest:
    def __init__(self, dbType: DBType, schema: str, selectProperties: List[str], graph: str = None, limit: int = -1):
        self.dbType = dbType
        self.limit = limit
        self.selectProperties = selectProperties
        self.schema = schema
        self.graph = graph


class TruncateParams:
    def __init__(self, graphName: str = None, dbType: DBType = None, schemaName: str = None):
        self.dbType = dbType
        self.graphName = graphName
        self.schemaName = schemaName


class InstallAlgo:
    def __init__(self, files: List[str], hdcName: str = None):
        self.files = files
        self.hdcName = hdcName


class InstallExtaAlgo(InstallAlgo):
    ...


class Batch:
    Nodes: List[ULTIPA.EntityRow]
    Edges: List[ULTIPA.EntityRow]
    Schema: Schema

    def __init__(self, Schema: Schema = None, Nodes: List[ULTIPA.EntityRow] = None,
                 Edges: List[ULTIPA.EntityRow] = None):
        if Nodes is None:
            Nodes = []
        if Edges is None:
            Edges = []
        self.Nodes = Nodes
        self.Edges = Edges
        self.Schema = Schema


class TaskStatus(Enum):
    All = '*'
    Pending = 'pending'
    Computing = 'computing'
    Writing = 'writing'
    Failed = 'failed'
    Done = 'done'
    Stopped = 'stopped'
