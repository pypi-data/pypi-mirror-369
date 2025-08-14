from ultipa.configuration.RequestConfig import RequestConfig
from ultipa.operate.base_extra import BaseExtra
from ultipa.types import ULTIPA
from ultipa.types.types_response import *
from ultipa.utils import UQLMAKER, CommandList
from ultipa.utils.ResposeFormat import ResponseKeyFormat
from ultipa.utils.convert import convertToPolicy
from ultipa.utils.convert import convertToPrivilege
from ultipa.utils.noneCheck import checkNone

JSONSTRING_KEYS = ["graphPrivileges", "systemPrivileges", "policies", "policy", "privilege"]
formatdata = ['graph_privileges']


class PolicyExtra(BaseExtra):
    '''
        Processing class that defines settings for policy related operations.
    '''

    def showPolicy(self,
                   config: RequestConfig = RequestConfig()) -> List[Policy]:
        '''
        Show policy list.

        Args:
            config: An object of RequestConfig class

        Returns:
            List[Policy]

        '''
        uqlMaker = UQLMAKER(command=CommandList.showPolicy, commonParams=config)
        res = self.UqlListSimple(uqlMaker=uqlMaker,
                                 responseKeyFormat=ResponseKeyFormat(jsonKeys=JSONSTRING_KEYS, dataFormat=formatdata))
        if isinstance(res, Response):
            return res
        if len(res.data) > 0:
            res.data = convertToPolicy(res)
        return res.data

    def showPrivilege(self,
                      config: RequestConfig = RequestConfig()) -> List[Privilege]:
        '''
        Show privilege list.

        Args:
            config: An object of RequestConfig class

        Returns:
            List[Privilege]

        '''

        uqlMaker = UQLMAKER(command=CommandList.showPrivilege, commonParams=config)
        res = self.UqlListSimple(uqlMaker=uqlMaker,
                                 responseKeyFormat=ResponseKeyFormat(jsonKeys=JSONSTRING_KEYS))
        if isinstance(res, Response):
            return res
        if len(res.data) > 0:
            res.data = convertToPrivilege(res)
        return res.data

    def getPolicy(self, policyName: str, config: RequestConfig = RequestConfig()) -> Policy | Response | None:
        '''
        Get a policy.

        Args:
            policyName: The name of policy

            config: An object of RequestConfig class

        Returns:
            Policy

        '''
        if checkNone(policyName):
            return Response(status=Status(code=ErrorCode.PARAM_ERROR, message='The policyName cannot be None'))
        uqlMaker = UQLMAKER(command=CommandList.getPolicy, commonParams=config)
        uqlMaker.setCommandParams(policyName)
        res = self.UqlListSimple(uqlMaker=uqlMaker,
                                 responseKeyFormat=ResponseKeyFormat(jsonKeys=JSONSTRING_KEYS, dataFormat=formatdata))
        if res.status.code == ULTIPA.ErrorCode.FAILED:
            return None
        if isinstance(res, Response):
            return res
        if res.status.code == ULTIPA.ErrorCode.SUCCESS and res.data:
            res.data = convertToPolicy(res)
        return res.data

    def createPolicy(self, policy: Policy,
                     config: RequestConfig = RequestConfig()) -> Response:
        '''
        Create a policy.

        Args:
            policy: The policy to be created; the field name must be set, systemPrivileges, graphPrivileges, propertyPrivilege and policies are optional.

            config: An object of RequestConfig class

        Returns:
            Response

        '''
        if checkNone(policy.name):
            return Response(status=Status(code=ErrorCode.PARAM_ERROR, message='The name of policy cannot be None'))
        uqlMaker = UQLMAKER(command=CommandList.createPolicy, commonParams=config)
        uqlMaker.setCommandParams(policy.name)
        paramsP = []
        if policy.graphPrivileges:
            paramsP.append(f"graph_privileges:{policy.graphPrivileges}")

        if policy.systemPrivileges:
            paramsP.append(f"system_privileges:{policy.systemPrivileges}")

        if policy.policies:
            paramsP.append(f"policies:{policy.policies}")

        if policy.propertyPrivileges:
            paramsP.append(f"property_privileges:{policy.propertyPrivileges.to_dict()}")

        result = "{" + ",".join(paramsP) + "}"
        uqlMaker.addParam('params', result, notQuotes=True)
        res = self.uqlSingle(uqlMaker=uqlMaker)
        return res

    def alterPolicy(self, policy: Policy,
                    config: RequestConfig = RequestConfig()) -> Response:
        '''
        Alter a policy.

        Args:
            policy: The policy to be created; the field name must be set, systemPrivileges, graphPrivileges, propertyPrivilege and policies are optional.

            config: An object of RequestConfig class

        Returns:
            Response

        '''
        if checkNone(policy.name):
            return Response(status=Status(code=ErrorCode.PARAM_ERROR, message='The name of policy cannot be None'))
        uqlMaker = UQLMAKER(command=CommandList.alterPolicy, commonParams=config)
        uqlMaker.setCommandParams(policy.name)
        params = {}
        if policy.systemPrivileges is not None:
            params.update({"system_privileges": policy.systemPrivileges})
        if policy.graphPrivileges is not None:
            params.update({"graph_privileges": policy.graphPrivileges})

        if policy.policies is not None:
            params.update({"policies": policy.policies})

        if policy.propertyPrivileges is not None:
            params.update({"property_privileges": policy.propertyPrivileges.to_dict()})

        uqlMaker.addParam('set', params, notQuotes=True)
        res = self.uqlSingle(uqlMaker=uqlMaker)
        return res

    def dropPolicy(self, policyName: str,
                   config: RequestConfig = RequestConfig()) -> Response:
        '''
        Drop a policy.

        Args:
            policyName:  The name of policy to be dropped

            config: An object of RequestConfig class

        Returns:
            Response

        '''

        uqlMaker = UQLMAKER(command=CommandList.dropPolicy, commonParams=config)
        uqlMaker.setCommandParams(policyName)
        res = self.uqlSingle(uqlMaker=uqlMaker)
        return res
