from ultipa.configuration.RequestConfig import RequestConfig
from ultipa.operate.base_extra import BaseExtra
from ultipa.types import ULTIPA
from ultipa.types.types import *
from ultipa.types.types_response import *
from ultipa.types.types_response import Response
from ultipa.utils import UQLMAKER, CommandList
from ultipa.utils.convert import convertToUser
from ultipa.utils.format import FormatType
from ultipa.utils.noneCheck import checkNone

JSONSTRING_KEYS = ["graphPrivileges", "systemPrivileges", "policies", "policy", "privilege"]
formatdata = ['graph_privileges']


class UserExtra(BaseExtra):
    '''
        Processing class that defines settings for user related operations.
    '''

    def _GRPATH_PRIVILEGES_DATA_FORMAT(self, obj):
        if isinstance(obj.get('graph_privileges'), list):
            resr = FormatType.graphPrivileges(obj.get('graph_privileges'))
            return resr
        else:
            return '[]'

    def showUser(self, config: RequestConfig = RequestConfig()) -> List[User] | Response:
        '''
        Show user list.

        Args:
            config: An object of RequestConfig class

        Returns:
            List[User]

        '''

        uqlMaker = UQLMAKER(command=CommandList.showUser, commonParams=config)
        res = self.UqlListSimple(uqlMaker=uqlMaker,
                                 responseKeyFormat=ResponseKeyFormat(jsonKeys=JSONSTRING_KEYS, dataFormat=formatdata))
        if isinstance(res, Response):
            return res
        if res.status.code == ULTIPA.ErrorCode.SUCCESS and len(res.data) > 0:
            res.data = convertToUser(res)
        return res.data

    def createUser(self, user: User,
                   config: RequestConfig = RequestConfig()) -> Response:
        '''
        Create a user.

        Args:
            user: The user to be created; the fields username and password must be set, systemPrivileges, graphPrivileges, propertyPrivilege and policies are optional

            config: An object of RequestConfig class

        Returns:
            Response

        '''
        if checkNone(user.username) or checkNone(user.password):
            return Response(
                status=Status(code=ErrorCode.PARAM_ERROR, message='The user`s username and password cannot be None'))

        uqlMaker = UQLMAKER(command=CommandList.createUser, commonParams=config)
        userparam = []

        if user.username:
            userparam.append(user.username)
        else:
            raise ParameterException(err='username is a required parameter')

        if user.password:
            userparam.append(user.password)
        else:
            raise ParameterException(err='password is a required parameter')

        uqlMaker.setCommandParams(userparam)

        params = []

        if user.graphPrivileges:
            params.append(f"graph_privileges:{user.graphPrivileges}")

        if user.systemPrivileges:
            params.append(f"system_privileges:{user.systemPrivileges}")

        if user.policies:
            params.append(f"policies:{user.policies}")

        if user.propertyPrivileges:
            params.append(f"property_privileges:{user.propertyPrivileges.to_dict()}")

        result = "{" + ",".join(params) + "}"
        uqlMaker.addParam('params', result, notQuotes=True)

        return self.uqlSingle(uqlMaker=uqlMaker)

    def dropUser(self, username: str,
                 config: RequestConfig = RequestConfig()) -> Response:
        '''
        Drop a user.

        Args:
            username: The name of user

            config: An object of RequestConfig class

        Returns:
            Response

        '''

        uqlMaker = UQLMAKER(command=CommandList.dropUser, commonParams=config)
        uqlMaker.setCommandParams(username)
        return self.uqlSingle(uqlMaker=uqlMaker)

    def alterUser(self, user: User,
                  config: RequestConfig = RequestConfig()) -> Response:
        '''
        Alter a user.

        Args:
            user: The user to be altered; the fields username must be set, systemPrivileges, graphPrivileges, propertyPrivilege and policies are optional.

            config: An object of RequestConfig class

        Returns:
            Response

        '''
        if checkNone(user.username):
            return Response(status=Status(code=ErrorCode.PARAM_ERROR, message='The user`s username cannot be None'))
        uqlMaker = UQLMAKER(command=CommandList.alterUser, commonParams=config)
        if user.username:
            uqlMaker.setCommandParams(user.username)
        else:
            raise ParameterException(err='username is a required parameter')

        paramsDict = {}
        if user.password:
            paramsDict.setdefault('password', user.password)

        if user.graphPrivileges:
            paramsDict.setdefault('graph_privileges', user.graphPrivileges)

        if user.systemPrivileges:
            paramsDict.setdefault('system_privileges', user.systemPrivileges)

        if user.policies:
            paramsDict.setdefault('policies', user.policies)

        if user.propertyPrivileges:
            paramsDict.setdefault('property_privileges', user.propertyPrivileges.to_dict())

        uqlMaker.addParam('set', paramsDict)
        return self.uqlSingle(uqlMaker=uqlMaker)

    def getUser(self, username: str,
                config: RequestConfig = RequestConfig()) -> Response | Any | None:
        '''
        Get a designated user.

        Args:
            username: The name of user

            config: An object of RequestConfig class

        Returns:
            User

        '''

        uqlMaker = UQLMAKER(command=CommandList.getUser, commonParams=config)
        uqlMaker.setCommandParams(username)
        res = self.UqlListSimple(uqlMaker=uqlMaker,
                                 responseKeyFormat=ResponseKeyFormat(jsonKeys=JSONSTRING_KEYS, dataFormat=formatdata))
        if res.status.code == ULTIPA.ErrorCode.FAILED:
            return None
        if isinstance(res, Response):
            return res
        if res.status.code == ULTIPA.ErrorCode.SUCCESS and res.data:
            res.data = convertToUser(res)
        return res.data
