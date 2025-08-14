import json
import re
from datetime import datetime
from typing import List

from ultipa.utils import errors
from ultipa.utils.ufilter.new_ufilter import Filter
from ultipa.utils.ufilter.ufilter import FilterBase


class CommandList:
    ab = "ab"
    khop = "khop"
    nodes = "find().nodes"
    edges = "find().edges"
    deleteNodes = "delete().nodes"
    deleteEdges = "delete().edges"
    updateNodes = "update().nodes"
    updateEdges = "update().edges"
    template = "t"
    autoNet = "autoNet"
    autoNetByPart = "autoNetByPart"
    nodeSpread = "spread"
    insert = "insert"
    upsert = "upsert"
    grant = "grant"
    showProperty = "show().property"
    showNodeProperty = "show().node_property"
    showEdgeProperty = "show().edge_property"
    createNodeProperty = "create().node_property"
    createEdgeProperty = "create().edge_property"
    dropNodeProperty = "drop().node_property"
    dropEdgeProperty = "drop().edge_property"
    alterNodeProperty = "alter().node_property"
    alterEdgeProperty = "alter().edge_property"
    showSchema = "show().schema"
    showNodeSchema = "show().node_schema"
    showEdgeSchema = "show().edge_schema"
    createNodeSchema = "create().node_schema"
    createEdgeSchema = "create().edge_schema"
    alterNodeSchema = "alter().node_schema"
    alterEdgeSchema = "alter().edge_schema"
    dropNodeSchema = "drop().node_schema"
    dropEdgeSchema = "drop().edge_schema"
    lteNode = "LTE().node_property"
    lteEdge = "LTE().edge_property"
    ufeNode = "UFE().node_property"
    ufeEdge = "UFE().edge_property"
    createNodeIndex = "create().node_index"
    createEdgeIndex = "create().edge_index"
    createNodeFulltext = "create().node_fulltext"
    createEdgeFulltext = "create().edge_fulltext"
    showIndex = "show().index"
    showNodeIndex = "show().node_index"
    showEdgeIndex = "show().edge_index"
    showFulltext = "show().fulltext"
    showNodeFulltext = "show().node_fulltext"
    showEdgeFulltext = "show().edge_fulltext"
    dropNodeIndex = "drop().node_index"
    dropEdgeIndex = "drop().edge_index"
    dropNodeFulltext = "drop().node_fulltext"
    dropEdgeFulltext = "drop().edge_fulltext"
    stat = "stats"
    algo = "algo"
    algo_dv = "algo_dv"
    showPrivilege = "show().privilege"
    grantUser = "grant().user"
    revoke = "revoke().user"
    showAlgo = "show().algo"
    showExta = "show().exta"
    showGraph = "show().graph"
    createGraph = "create().graph"
    dropGraph = "drop().graph"
    alterGraph = "alter().graph"
    truncate = "truncate"
    compact = "compact"
    showUser = "show().user"
    getUser = "show().user"
    getSelfInfo = "show().self"
    createUser = "create().user"
    alterUser = "alter().user"
    dropUser = "drop().user"
    createPolicy = "create().policy"
    alterPolicy = "alter().policy"
    dropPolicy = "drop().policy"
    showPolicy = "show().policy"
    getPolicy = "show().policy"
    showTask = "show().task"
    clearTask = "clear().task"
    pauseTask = "pause().task"
    resumeTask = "resume().task"
    stopTask = "stop().task"
    top = "top"
    kill = "kill"
    mount = "mount().graph"
    unmount = "unmount().graph"
    createBackup = "db.backup.create"
    showBackup = "db.backup.show"
    restoreBackup = "db.backup.restore"
    showHDCAlgo = "hdc.server.show"
    showJob = "show().job"
    clearJob = "clear().job"
    stopJob = "stop().job"
    showHDCGraph = "hdc.graph.show"
    createHDCGraph = "hdc.graph.create"
    dropHDCGraph = "hdc.graph.drop"
    licenseDump = "license.dump"
    showGraphMore = "show().graph().more"
    rebalanceGraph = 'alter().graph'
    createGraphGql = 'create graph '


def _replace(value: str):
    template = re.compile(r"\'?\"?(point\([^)]*\))\'?\"?")
    matches = re.search(template, value)
    if matches:
        return re.sub(r"\'?\"?(point\([^)]*\))\'?\"?", matches.group(1), value)
    return value


class UQLMAKER:
    '''
    A class that assembles UQL.
    '''

    def __init__(self, command: CommandList, commandP: any = None, commonParams=None):
        self._command = command
        self._commandP = commandP
        self.commonParams = commonParams
        self._params: List[object] = []
        self.templateParams: List[object] = []

    def setCommandParams(self, commandP: any):
        if commandP:
            if not isinstance(commandP, list):
                self._commandP = [commandP]
            else:
                self._commandP = commandP
            newcommandP = []
            for i, comm in enumerate(self._commandP):
                if isinstance(comm, list) or isinstance(comm, dict) or isinstance(comm, int):
                    newcommandP.append(str(comm))
                    continue
                if isinstance(comm, Filter):
                    if isinstance(comm, str):
                        continue
                    newcommandP.append("{%s}" % (comm.builder()))
                    continue
                if not comm:
                    newcommandP.append(comm)
                    continue
                if comm.startswith('{'):
                    newcommandP.append(comm)
                    continue
                if comm.startswith('@') and i == 0:
                    newcommandP.append(comm)
                else:
                    if comm.startswith("`"):
                        newcommandP.append(comm)
                        continue
                    else:
                        newcommandP.append(json.dumps(comm, ensure_ascii=False))

            commandP = ','.join(newcommandP)
        else:
            return
        if type(commandP) == object:
            commandP = json.dumps(commandP, ensure_ascii=False)
        if isinstance(commandP, Filter):
            commandP = commandP.builder()
        self._commandP = commandP

    def addTemplateParams(self, templateParams: List[object]):
        self.templateParams = templateParams

    def addParam(self, key: str, value: any, required: bool = True, notQuotes=False):
        try:
            if notQuotes:
                self._params.append({"key": key, "value": value})
                return
            _notStringify = False
            if type(value) == bool:
                if value:
                    required = False
                value = ""
            if required:
                if isinstance(value, list) or value or value == 0 or value is None:
                    pass
                else:
                    return
            if "filter" == key:
                self.addParam("node_filter", value)
                self.addParam("edge_filter", value)
                return

            if key in ["filter", "node_filter", "edge_filter"]:
                _notStringify = True
                if isinstance(value, FilterBase):
                    value = value.builder()

            if key == 'return':
                if type(value) == list:
                    value = ','.join([i.toString for i in value])
                elif type(value) == str:
                    self._params.append({"key": key, "value": value})
                    return
                else:
                    value = value.toString
                self._params.append({"key": key, "value": value})
                return
            if key == 'shards':
                self._params.append({"key": key, "value": value})
                return
            if key == 'more':
                self._params.append({"key": key, "value": ''})
                return
            if key == 'partitionByHash':
                if type(value) == list:
                    value = ','.join([i.toString for i in value])
                elif type(value) == str:
                    self._params.append({"key": key, "value": value})
                    return
                else:
                    value = value.toString
                self._params.append({"key": key, "value": value})
                return
            if key in ['into', 'as']:
                self._params.append({"key": key, "value": value})
                return

            if key in ['graph_privileges']:
                if isinstance(value, list):
                    value = [{v.toDict().get('name'): v.toDict().get('values')} for v in value]
                else:
                    value = [{value.toDict().get('name'): value.toDict().get('values')}]

            if type(value) == object or type(value) == dict or (
                    type(value) == str and len(value) > 0 and not _notStringify):
                value = json.dumps(value, ensure_ascii=False)
            if isinstance(value, list):
                value = [
                    {k: v.isoformat() if isinstance(v, datetime) else v for k, v in item.items() if v is not None}
                    for item in value if isinstance(item, dict)
                ]
            if value == []:
                return
            if value is None:
                value = ""
            self._params.append({"key": key, "value": value})
        except Exception as e:
            raise errors.ParameterException(e)

    def toString(self):
        uql = ""
        str_return = ""
        if self._commandP:
            self._commandP = self._commandP
            uql += "{}({})".format(self._command, self._commandP)
        else:
            uql += "{}({})".format(self._command, '')
        if len(self.templateParams) > 0:
            for tp in self.templateParams:
                filterString = ''
                if tp.filter:
                    if isinstance(tp.filter, FilterBase):
                        tp.filter = tp.filter.builder()
                    filterString = tp.filter
                node_filter_str = ''
                if tp.__dict__.get('node_fitler'):
                    if isinstance(tp.node_fitler, FilterBase):
                        tp.node_fitler = tp.node_fitler.builder()
                    node_filter_str = f'.nf{tp.node_fitler}'
                step = tp.__dict__.get('steps')
                stepStr = ''
                if step:
                    stepStr = f'[{":".join(step)}]'
                uql += f'.{tp.name}({tp.alias or ""}{filterString or ""}){node_filter_str}{stepStr}'
        if len(self._params) > 0:
            ps = []
            for p in self._params:
                value = p["value"]
                if p['key'] in ["return", "limit", "as"]:
                    fstr = "{} {}".format(p['key'], value)
                    str_return += fstr + " "
                    continue

                if p['key'] in ["shards", "partitionByHash"]:
                    fstr = '{}({})'.format(p['key'], value)

                if p['key'] in ["select_node_properties", "select_edge_properties", "srcs",
                                "dests", "return"]:
                    fstr = "{}({})".format(p["key"], value)
                else:
                    fstr = "{}({})".format(p["key"], value)
                fstr = _replace(fstr)
                ps.append(fstr)
            if len(ps) > 0:
                uql += "." + ".".join(ps)
        uql += " " + str_return
        return uql.strip()


class UQLParams():
    def __init__(self):
        self.commands = []
        self.commandParam = {}
        self.params = {}
        self.paramsOriginal = {}

    def getFirstCommands(self):
        if len(self.commands) > 0:
            return self.commands[0]
        return None

    def getSecondCommands(self):
        if len(self.commands) > 1:
            return self.commands[1]
        return None

    def getCommands(self, index):
        if len(self.commands) > index:
            return self.commands[index]
        return None

    def getCommandsParam(self, index):
        if len(self.commands) > index:
            return self.commandParam.get(self.commands[index])
        return None


class UQL:

    @staticmethod
    def uqlObjectExample(uqlStr):
        ret = UQLParams()
        ret.uql = uqlStr
        return ret

    @staticmethod
    def parse(uqlStr):
        '''
        Parse UQL.

        Args:
            uqlStr: A uql statement

        Returns:

        '''
        commandReg = r'([a-z_A-Z][a-z_A-Z\.]*)\(([^\(|^\)]*)\)'
        matchAll = re.findall(commandReg, uqlStr)
        result = UQL.uqlObjectExample(uqlStr)
        for i, m in enumerate(matchAll):
            name, value = m
            result.commands.append(name)
            if isinstance(value, str):
                value = value.replace("\"", "").replace("'", "")
            result.commandParam.update({name: value})
        return result

    @staticmethod
    def parse_global(uqlStr):
        reg = r'(.*\(\)\.[A-Za-z]+\(?)'
        matchAll = re.findall(reg, uqlStr)
        result = UQL.uqlObjectExample(uqlStr)
        index = 0
        if matchAll:
            for value in matchAll:
                result.commands.append(value.strip("("))
                index += 1
            return result


if __name__ == '__main__':
    ret = UQL.parse("db.backup.show(\"<backup_path>\")")
    print(ret)
