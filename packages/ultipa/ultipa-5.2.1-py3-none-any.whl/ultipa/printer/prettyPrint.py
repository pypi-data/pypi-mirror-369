# -*- coding: utf-8 -*-
# @Time    : 2022/7/7 11:01 AM
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : prettyPrint.py
import json
from typing import List

from prettytable import PrettyTable
from treelib import Tree

from ultipa.printer.treeNode import TreeNode
from ultipa.types.types import DataItem, ExplainPlan, ResultType, Path, Node, Edge, PlanNode
from ultipa.utils.convert import convertTableToDict


class PrettyPrint:
    '''
        Class that defines settings for formatted output
    '''
    count = 34
    tree = Tree()

    def printLine(self, name):
        num = int(PrettyPrint.count - len(name) / 2)
        print('-' * num + f'{name}' + '-' * num)

    def prettyStatus(self, data):
        y = PrettyTable(['Code', 'Message'], title="STATUS", end=10, align="l")
        y.add_row([data.code, data.message])
        print(y)

    def prettyStatistics(self, data):
        y = PrettyTable(['edgeAffected', 'nodeAffected', 'engineCost', 'totalCost'], title="Statistics", end=10,
                        align="l")
        y.add_row([data.edgeAffected, data.nodeAffected, data.engineCost, data.totalCost])
        print(y)

    def prettyDataList(self, data: List[dict]):
        propertList = []
        if len(data) > 0:
            if len(data[0].keys()) > 0:
                propertList.extend(list(data[0].keys()))
            y = PrettyTable(propertList, title=f"Alias: Data", align="l")
            for d in data:
                li = []
                for p in propertList:
                    li.append(d.get(p))
                y.add_row(li)
            print(y)
        else:
            return None

    def prettyData(self, data: dict):
        propertList = []
        if len(data.keys()) > 0:
            propertList.extend(list(data.keys()))
        y = PrettyTable(propertList, title=f"Alias: Data", align="l")
        li = []
        for p in propertList:
            li.append(data.get(p))
        y.add_row(li)
        print(y)

    def prettyNode(self, data: DataItem):
        schemaDict = {}
        for node in data.asNodes():
            propertList = ["id", "uuid", "schema"]
            if node is None:
                schemaDict.update({None: propertList})
                continue
            if not schemaDict.get(node.getSchema()):
                if node.values:
                    newPropertList = propertList + list(node.values.keys())
                    schemaDict.update({node.getSchema(): newPropertList})
                else:
                    schemaDict.update({node.getSchema(): propertList})

        for key in schemaDict:
            y = PrettyTable(schemaDict.get(key), title=f"Alias: {data.alias} AliasType: {data.type} Schema: {key}",
                            align="l")
            for newNode in data.asNodes():
                if newNode is None:
                    li = [None, None, None]
                    y.add_row(li)
                    continue
                if newNode.getSchema() == key:
                    li = [newNode.getID(), newNode.getUUID(), newNode.getSchema()]
                    if newNode.values:
                        li.extend(list(newNode.values.values()))
                    y.add_row(li)
                else:
                    continue
            print(y)

    def prettyAttrNode(self, alias, nodes: List[Node]):
        ret = []
        schemaDict = {}
        for node in nodes:
            propertList = ["id", "uuid", "schema"]
            if node is None:
                schemaDict.update({None: propertList})
                continue
            if not schemaDict.get(node.getSchema()):
                if node.values:
                    newPropertList = propertList + list(node.values.keys())
                    schemaDict.update({node.getSchema(): newPropertList})
                else:
                    schemaDict.update({node.getSchema(): propertList})

        for key in schemaDict:
            y = PrettyTable(schemaDict.get(key), title=f"Alias: {alias} AliasType: NODE Schema: {key}",
                            align="l")
            for newNode in nodes:
                if newNode is None:
                    li = [None, None, None]
                    y.add_row(li)
                    continue
                if newNode.getSchema() == key:
                    li = [newNode.getID(), newNode.getUUID(), newNode.getSchema()]
                    if newNode.values:
                        li.extend(list(newNode.values.values()))
                    y.add_row(li)
                else:
                    continue
            ret.append(y)
        return ret

    def prettyEdge(self, data: DataItem):
        schemaDict = {}
        for edge in data.asEdges():
            propertList = ["uuid", "from_uuid", "to_uuid", "from_id", "to_id", "schema"]
            if edge is None:
                schemaDict.update({None: propertList})
                continue
            if not schemaDict.get(edge.getSchema()):
                if edge.values:
                    newPropertList = propertList + list(edge.values.keys())
                    schemaDict.update({edge.getSchema(): newPropertList})
                else:
                    schemaDict.update({edge.getSchema(): propertList})

        for key in schemaDict:
            y = PrettyTable(schemaDict.get(key), title=f"Alias: {data.alias} AliasType: {data.type} Schema: {key}",
                            align="l")
            for newEdge in data.asEdges():
                if newEdge is None:
                    li = [None, None, None, None, None, None]
                    y.add_row(li)
                    continue
                if newEdge.getSchema() == key:
                    li = [newEdge.getUUID(), newEdge.getFromUUID(), newEdge.getToUUID(), newEdge.getFrom(),
                          newEdge.getTo(), newEdge.getSchema()]
                    if newEdge.values:
                        li.extend(list(newEdge.values.values()))
                    y.add_row(li)
                else:
                    continue
            print(y)

    def prettyAttrEdge(self, alias, edges: List[Edge]):
        ret = []
        schemaDict = {}
        for edge in edges:
            propertList = ["uuid", "from_uuid", "to_uuid", "from_id", "to_id", "schema"]
            if edge is None:
                schemaDict.update({None: propertList})
                continue
            if not schemaDict.get(edge.getSchema()):
                if edge.values:
                    newPropertList = propertList + list(edge.values.keys())
                    schemaDict.update({edge.getSchema(): newPropertList})
                else:
                    schemaDict.update({edge.getSchema(): propertList})

        for key in schemaDict:
            y = PrettyTable(schemaDict.get(key), title=f"Alias: {alias} AliasType: EDGE Schema: {key}", align="l")
            for newEdge in edges:
                if newEdge is None:
                    li = [None, None, None, None, None, None]
                    y.add_row(li)
                    continue
                if newEdge.getSchema() == key:
                    li = [newEdge.getUUID(), newEdge.getFromUUID(), newEdge.getToUUID(), newEdge.getFrom(),
                          newEdge.getTo(), newEdge.getSchema()]
                    if newEdge.values:
                        li.extend(list(newEdge.values.values()))
                    y.add_row(li)
                else:
                    continue
            ret.append(y)
        return ret

    def prettyTable(self, data: DataItem):

        if data.alias == "_algoList":
            headers = data.asTable().getHeaders()
            rows = data.asTable().getRows()
            table_rows_dict = convertTableToDict(rows, headers)
            algo_list = []
            for data1 in table_rows_dict:
                algo_list.append(json.loads(data1.get("param")))
            if len(algo_list) > 0:
                propertList = algo_list[0].keys()
                y = PrettyTable(propertList, title=f"Alias: {data.alias} AliasType: {data.type}", align="l")
                for algo in algo_list:
                    row = []
                    for key in propertList:
                        row.append(algo.get(key))
                    y.add_row(row)
            else:
                return
        else:
            propertList = []
            if len(data.asTable().rows) > 0:
                for index, header in enumerate(data.asTable().getHeaders()):
                    propertList.append(header.get("property_name"))
            else:
                return

            y = PrettyTable(propertList, title=f"Alias: {data.alias} AliasType: {data.type}", align="l")
            for row in data.asTable().getRows():
                y.add_row(row)
        print(y)

    def _PrintPath(self, path: Path):
        pathStr = ""
        end = ""
        for index, edge in enumerate(path.edges):
            d1 = "-"
            d2 = "-"
            node = path.getNodes()[index]
            if edge.getFrom() == node.getID():
                d2 = "->"
                if index == len(path.edges) - 1:
                    end = f" ({str(edge.getTo())})"
            else:
                d1 = "<-"
                if index == len(path.edges) - 1:
                    end = f" ({str(edge.getFrom())})"

            pathStr += f"({node.getID()}) {d1} [{edge.getUUID()}] {d2}"
            if end:
                pathStr += end
        return pathStr

    def prettyPath(self, data: DataItem):
        propertList = ["#", "Path"]
        y = PrettyTable(propertList, title=f"Alias: {data.alias} AliasType: {data.type}", align="l")
        for i, path in enumerate(data.asPaths()):
            li = [i]
            pathStr = self._PrintPath(path)
            li.append(pathStr)
            y.add_row(li)
        print(y)

    def _formatAttrListData(self, data: list, alias: str):
        if isinstance(data, list) and len(data) > 0:
            if isinstance(data[0], Path):
                li = []
                for i in data:
                    li.append(self._PrintPath(i))
                return str(li)
            elif isinstance(data[0], Node):
                return self.prettyAttrNode(alias, data)

            elif isinstance(data[0], Edge):
                return self.prettyAttrEdge(alias, data)
            else:
                return str(data)
        else:
            return str(data)

    def prettyAttr(self, data: DataItem):
        if data.asAttr().resultType in [ResultType.RESULT_TYPE_PATH, ResultType.RESULT_TYPE_EDGE,
                                        ResultType.RESULT_TYPE_NODE]:
            propertList = ["#", data.alias]
            y = PrettyTable(propertList, title=f"Alias: {data.alias} AliasType: {data.type}", align="l")
            for i, adata in enumerate(data.asAttr().values):
                ret = self._formatAttrListData(adata, data.alias)
                y.add_row([i + 1, ret])
            print(y)
        else:
            propertList = ["#", data.alias]
            y = PrettyTable(propertList, title=f"Alias: {data.alias} AliasType: {data.type}", align="l")
            if len(data.asAttr().values) > 0:
                for i, adata in enumerate(data.asAttr().values):
                    ret = self._formatAttrListData(adata, data.alias)
                    y.add_row([i + 1, ret])
            else:
                y.add_row([1, str(data.asAttr().values)])
            print(y)

    def prettyArray(self, data: DataItem):
        propertList = [data.alias]
        y = PrettyTable(propertList, title=f"Alias: {data.alias} AliasType: {data.type}", align="l")
        for array in data.asArray().elements:
            y.add_row([json.dumps(array, ensure_ascii=False)])
        print(y)

    def prettyTree(self, plans: ExplainPlan):
        def buildTree(plans: [PlanNode]):
            if plans == None or len(plans) == 0:
                return TreeNode()
            tree = TreeNode(plans[0])
            del (plans[0])
            for i in range(tree.explain.children_num):
                node = buildTree(plans)
                tree.childNodes.append(node)
            return tree

        root = buildTree(plans.planNodes)
        self._printTree(root, root.explain.id, True)
        ret = self.tree.show(stdout=False)
        propertList = ["data"]
        y = PrettyTable(propertList, title=f"Alias: tree AliasType: ExplainPlan", align="l")
        y.add_row([ret])
        print(y)

    def _printTree(self, root: TreeNode, parter, isRoot=False):
        if isRoot:
            self.tree.create_node(root.explain.uql, parter)
        else:
            self.tree.create_node(root.explain.uql, identifier=root.explain.id, parent=parter)
        if len(root.childNodes) > 0:
            parter = root.explain.id
            for child in root.childNodes:
                self._printTree(child, parter)
        else:
            return
