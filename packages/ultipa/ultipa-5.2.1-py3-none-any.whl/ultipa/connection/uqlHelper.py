# -*- coding: utf-8 -*-
# @Time    : 2023/7/18 11:53
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : uqlHelper.py
from ultipa.utils import CommandList
from ultipa.utils.uqlMaker import UQL


class UQLHelper:
    '''
        Class that defines settings for UQL processing.

    '''
    # _globalCommand = [
    #     CommandList.createUser,
    #     CommandList.showUser,
    #     CommandList.alterUser,
    #     CommandList.getUser,
    #     CommandList.dropUser,
    #     CommandList.grant,
    #     CommandList.revoke,
    #     CommandList.showPolicy,
    #     CommandList.getPolicy,
    #     CommandList.createPolicy,
    #     CommandList.alterPolicy,
    #     CommandList.dropPolicy,
    #     CommandList.showPrivilege,
    #     CommandList.stat,
    #     CommandList.createGraph,
    #     CommandList.showGraph,
    #     CommandList.dropGraph,
    #     CommandList.alterGraph,
    #     CommandList.top,
    #     CommandList.kill,
    #     CommandList.createBackup,
    #     CommandList.showBackup,
    #     CommandList.restoreBackup,
    #     CommandList.mount,
    #     CommandList.unmount
    # ]
    _ForceMasterCommands = [
        CommandList.showBackup,
    ]
    _write = [
        "alter",
        "create",
        "drop",
        "grant",
        "revoke",
        "LTE",
        "UFE",
        "truncate",
        "compact",
        "insert",
        "upsert",
        "update",
        "delete",
        "clear",
        "stop",
        "pause",
        "resume",
        "top",
        "kill",
        "mount",
        "unmount",
        CommandList.createBackup,
        CommandList.restoreBackup,
    ]
    _extra = [
        CommandList.top,
        CommandList.kill,
        CommandList.showTask,
        CommandList.stopTask,
        CommandList.clearTask,
        CommandList.stat,
        CommandList.showGraph,
        CommandList.showAlgo,
        CommandList.createPolicy,
        CommandList.dropPolicy,
        CommandList.showPolicy,
        CommandList.getPolicy,
        CommandList.grant,
        CommandList.revoke,
        CommandList.showPrivilege,
        CommandList.showUser,
        CommandList.getSelfInfo,
        CommandList.createUser,
        CommandList.alterUser,
        CommandList.dropUser,
        CommandList.showIndex,
        # CommandList.clearTask,
    ]

    def __init__(self, uql: str):
        self.uql = uql
        self.parseRet = UQL.parse(uql)

    # def uqlIsGlobal(self):
    #     '''
    #     Judge whether the UQL is Global.
    #
    #     Args:
    #         uql: a uql statement
    #
    #     Returns:
    #
    #     '''
    #
    #     if self.parseRet != None:
    #         c1 = self.parseRet.getFirstCommands()
    #         c2 = f"{c1}().{self.parseRet.getSecondCommands()}"
    #         return c1 in UQLHelper._globalCommand or c2 in UQLHelper._globalCommand
    #     return False

    @staticmethod
    def uqlIsWrite(uql: str):
        '''
        Judge whether the UQL is a write operation.

        Args:
            uql: a uql statement

        Returns:

        '''

        p = UQL.parse(uql)
        if p != None:
            for command in p.commands:
                if list(filter(lambda x: x == command, UQLHelper._write)):
                    return True
        return False

    @staticmethod
    def uqlIsForceUseMaster(uql: str):
        p = UQL.parse(uql)
        if p != None:
            for command in p.commands:
                if list(filter(lambda x: x == command, UQLHelper._ForceMasterCommands)):
                    return True
        return False

    @staticmethod
    def uqlIsAlgo(uql: str):
        '''
        Judge whether the UQL is an algorithm operation.

        Args:
            uql: a uql statement

        Returns:

        '''
        p = UQL.parse(uql)
        if p != None:
            for command in p.commands:
                if command == 'algo':
                    return True
        return False

    @staticmethod
    def uqlIsExecTask(uql: str):
        return "exec task" in uql.lower()

    @staticmethod
    def uqlIsExtra(uql: str):
        p = UQL.parse(uql)
        if p != None:
            c1 = p.getFirstCommands()
            c2 = f"{c1}().{p.getSecondCommands()}"
            return c1 in UQLHelper._extra or c2 in UQLHelper._extra
        return False
