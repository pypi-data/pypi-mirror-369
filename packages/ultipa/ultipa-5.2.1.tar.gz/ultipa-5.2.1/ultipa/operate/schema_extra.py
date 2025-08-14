from ultipa.configuration.RequestConfig import RequestConfig
from ultipa.operate.base_extra import BaseExtra
from ultipa.operate.property_extra import PropertyExtra
from ultipa.structs import DBType
from ultipa.types import ULTIPA
from ultipa.types.types_response import *
from ultipa.types.types_response import Response
from ultipa.utils import UQLMAKER, CommandList
from ultipa.utils.convert import convertToSchemas
from ultipa.utils.format import FormatType
from ultipa.utils.noneCheck import checkNone

BOOL_KEYS = ["index", "lte"]
REPLACE_KEYS = {
    "name": "schemaName",
    "type": "propertyType",
}


class SchemaExtra(BaseExtra):
    '''
        Prcessing class that defines settings for schema related operations.
    '''

    def showSchema(self,
                   config: RequestConfig = RequestConfig()) -> List[Schema]:
        '''
        Show schema(s).

        Args:

            config: An object of RequestConfig class

        Returns:
            List[Schema]

        '''

        command = CommandList.showSchema
        commandP = ''

        uqlMaker = UQLMAKER(command=command, commandP=commandP, commonParams=config)
        res = self.uqlSingle(uqlMaker)
        if res.status.code == ULTIPA.ErrorCode.SUCCESS and res.items:
            schemas = convertToSchemas(res)
            return schemas.schema
        return res

    def showNodeSchema(self, config: RequestConfig = RequestConfig()) -> List[Schema]:
        '''
        Show Nodeschema(s).

        Args:
            config: An object of RequestConfig class

        Returns:
            List[Schema]

        '''

        command = CommandList.showNodeSchema
        commandP = ''

        uqlMaker = UQLMAKER(command=command, commandP=commandP, commonParams=config)
        res = self.uqlSingle(uqlMaker)
        if res.status.code == ULTIPA.ErrorCode.SUCCESS and res.items:
            schemas = convertToSchemas(res)
            return schemas.schema
        return res

    def showEdgeSchema(self, config: RequestConfig = RequestConfig()) -> List[Schema]:
        '''
        Show Edgeschema(s).

        Args:
            config: An object of RequestConfig class

        Returns:
            List[Schema]

        '''

        command = CommandList.showEdgeSchema
        commandP = ''

        uqlMaker = UQLMAKER(command=command, commandP=commandP, commonParams=config)
        res = self.uqlSingle(uqlMaker)
        if res.status.code == ULTIPA.ErrorCode.SUCCESS and res.items:
            schemas = convertToSchemas(res)
            return schemas.schema
        return res

    def createSchema(self, schema: Schema, isCreateProperties: bool = False,
                     config: RequestConfig = RequestConfig()) -> Response:
        '''
        Create a schema.

        Args:
            schema: The schema to be created; the attributes name and dbType are mandatory, properties and description are optional.

            isCreateProperties: Whether to create properties associated with the schema, the default is False.

            config: An object of RequestConfig class

        Returns:
            Response

        '''

        if checkNone(schema.name) or checkNone(schema.dbType):
            message = checkNone(
                schema.name) and 'The name of the schema cannot be None' or 'The dbType of the schema cannot be None'
            return Response(status=Status(code=ULTIPA.ErrorCode.PARAM_ERROR,
                                          message=message))

        command = schema.dbType == DBType.DBNODE and CommandList.createNodeSchema or CommandList.createEdgeSchema
        commandP = [f"`{schema.name}`"]
        if schema.description:
            commandP.append(schema.description)
        uqlMaker = UQLMAKER(command=command, commonParams=config)
        uqlMaker.setCommandParams(commandP=commandP)
        res = self.uqlSingle(uqlMaker=uqlMaker)
        if res.status.code != ErrorCode.SUCCESS:
            return res
        if isCreateProperties:
            if schema.properties:
                for prop in schema.properties:
                    try:
                        prop.schema = schema.name
                        res1 = PropertyExtra.createProperty(self, dbType=schema.dbType,
                                                            property=prop, config=config)
                    except Exception as e:
                        print("An error occurred while creating property:", prop.name, "Error:", e)
        return res

    def createSchemaIfNotExist(self, schema: Schema, isCreateProperties: bool,
                               config: RequestConfig = RequestConfig()) -> ResponseWithExistCheck:
        '''
        Create a schema if schema does not exist.

        Args:
            schema: The schema to be created; the attributes name and dbType are mandatory, properties and description are optional.

            config: An object of RequestConfig class

        Returns:
            ResponseWithExistCheck

        '''
        check = self.getSchema(schemaName=schema.name, dbType=schema.dbType, config=config)
        if check is not None:
            return ResponseWithExistCheck(exist=True, response=Response())

        elif check is None:
            res = self.createSchema(schema=schema, isCreateProperties=isCreateProperties, config=config)
            return ResponseWithExistCheck(exist=False, response=res)

    def dropSchema(self, schema: Schema,
                   config: RequestConfig = RequestConfig()) -> Response:
        '''
        Drop schema.

        Args:
            schema: The schema to be dropped; the attributes name and dbType are mandatory.

            config: An object of RequestConfig class

        Returns:
            Response

        '''
        if checkNone(schema.name) or checkNone(schema.dbType):
            return Response(
                status=Status(code=ErrorCode.PARAM_ERROR, message='The name and dbType of schema cannot be None'))
        command = schema.dbType == DBType.DBNODE and CommandList.dropNodeSchema or CommandList.dropEdgeSchema
        commandP = "@`%s`" % (schema.name)

        uqlMaker = UQLMAKER(command=command, commandP=commandP, commonParams=config)
        res = self.uqlSingle(uqlMaker=uqlMaker)
        return res

    def alterSchema(self, originalSchema: Schema, newSchema: Schema,
                    config: RequestConfig = RequestConfig()) -> Response:
        '''
        Alter schema.

        Args:
            originalSchema: The schema to be altered; the attributes name and dbType are mandatory

            newSchema: Schema: A Schema object used to set the new name and/or description for the schema.

            config: An object of RequestConfig class

        Returns:
            Response
        '''
        if checkNone(originalSchema.name) or checkNone(originalSchema.dbType):
            return Response(status=Status(code=ErrorCode.PARAM_ERROR,
                                          message='The name and dbType of originalSchema cannot be None'))
        if newSchema.dbType is not None and newSchema.dbType != originalSchema.dbType:
            return Response(status=Status(code=ErrorCode.PARAM_ERROR,
                                          message='The new dbType must be consistent with the old dbType'))
        command = originalSchema.dbType == DBType.DBNODE and CommandList.alterNodeSchema or CommandList.alterEdgeSchema
        commandP = "@`%s`" % (originalSchema.name)
        update_dict = {}
        if newSchema.name:
            update_dict.setdefault('name', newSchema.name)
        if newSchema.description:
            update_dict.update({'description': newSchema.description})
        uqlMaker = UQLMAKER(command=command, commandP=commandP, commonParams=config)
        uqlMaker.addParam("set", update_dict)
        res = self.uqlSingle(uqlMaker=uqlMaker)
        return res

    def getSchema(self, schemaName: str, dbType: DBType, config: RequestConfig = RequestConfig()) -> Response | Any | None:
        '''
        Acquire a designated Schema.

        Args:
            schemaName: The name of Schema

            dbType: The DBType of data (DBNODE or DBEDGE)

            config: An object of RequestConfig class

        Returns:
            Schema
        '''

        if FormatType.checkNone(schemaName) or FormatType.checkNone(dbType):
            message = 'The schemaName and dbType cannot None' if FormatType.checkNone(schemaName) and FormatType.checkNone(dbType)\
                else 'The dbType cannot None' if FormatType.checkNone(dbType) else 'The schemaName cannot None'

            return Response(status=Status(code=ErrorCode.PARAM_ERROR, message=message))
        if dbType != None:
            if dbType == DBType.DBNODE:
                command = CommandList.showNodeSchema
            elif dbType == DBType.DBEDGE:
                command = CommandList.showEdgeSchema
            elif dbType == DBType.DBGLOBAL:
                return Response(
                    status=Status(code=ErrorCode.PARAM_ERROR, message='The dbType cannot be DBType.DBGLOBAL'))

            if schemaName:
                commandP = "@`%s`" % (schemaName)

        uqlMaker = UQLMAKER(command, commandP=commandP, commonParams=config)

        res = self.uqlSingle(uqlMaker=uqlMaker)
        if res.status.code == ULTIPA.ErrorCode.FAILED:
            return None
        elif res.status.code == ULTIPA.ErrorCode.SUCCESS and res.items:
            schemas = convertToSchemas(res)
            return schemas.schema[0]
        return res

    def getNodeSchema(self, schemaName: str, config: RequestConfig = RequestConfig()) -> Schema:
        '''
        Acquire a designated Node Schema.

        Args:
            schemaName: The name of Schema

            config: An object of RequestConfig class

        Returns:
            Schema
        '''

        return self.getSchema(dbType=DBType.DBNODE, schemaName=schemaName, config=config)

    def getEdgeSchema(self, schemaName: str, config: RequestConfig = RequestConfig()) -> Schema:
        '''
        Acquire a designated Edge Schema.

        Args:
            schemaName: The name of Schema

            config: An object of RequestConfig class

        Returns:
            Schema
        '''

        return self.getSchema(dbType=DBType.DBEDGE, schemaName=schemaName, config=config)
