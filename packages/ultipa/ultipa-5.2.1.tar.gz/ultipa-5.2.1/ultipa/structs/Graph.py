# -*- coding: utf-8 -*-
# @Time    : 2023/8/1 10:47
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : Graph.py
from typing import Dict, List

from ultipa.structs.BaseModel import BaseModel
from ultipa.structs.Edge import Edge
from ultipa.structs.Node import Node
from ultipa.structs.Path import Path


class Graph(BaseModel):
    '''
        Data class for graph.
    '''

    def __init__(self,
                 paths: List[Path] = [],
                 nodes: Dict[int, Node] = {},
                 edges: Dict[int, Edge] = {}):
        self.paths = paths
        self.nodes = nodes
        self.edges = edges

    def getPaths(self):
        for data in self.paths:
            data.nodes = {nodeuuidsdata: self.nodes[nodeuuidsdata] for nodeuuidsdata in data.nodeUuids}
            data.edges = {edgeuuidsdata: self.edges[edgeuuidsdata] for edgeuuidsdata in data.edgeUuids}
        return self.paths

    def addNode(self, node: Node):
        self.nodes.update({node.uuid: node})

    def addEdge(self, edge: Edge):
        self.edges.update({edge.uuid: edge})


class GraphAlias(BaseModel):
    def __init__(self, alias: str, graph: Graph = None):
        self.alias = alias
        self.graph = graph
