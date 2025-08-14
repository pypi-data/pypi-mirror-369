# -*- coding: utf-8 -*-
# @Time    : 2023/8/4 16:20
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : Path.py
from typing import Dict, List

from ultipa.structs.BaseModel import BaseModel
from ultipa.structs.Edge import Edge
from ultipa.structs.Node import Node


class Path(BaseModel):
    '''
        Data class for path.
    '''

    def __init__(self, nodeUuids: List[int] = None,
                 edgeUuids: List[int] = None,
                 nodes: Dict[int, Node] = {},
                 edges: Dict[int, Edge] = {}
                 ):
        self.nodeUuids = nodeUuids
        self.edgeUuids = edgeUuids
        self.nodes = nodes
        self.edges = edges

    def length(self):
        return len(self.edgeUuids)


class PathAlias:
    '''
        Data class for path with alias.
    '''

    def __init__(self, alias: str, paths: List[Path] = None):
        self.alias = alias
        if paths is None:
            paths = []
        self.paths = paths

    def length(self):
        return len(self.paths)

    def getNodes(self):
        nodes = [i.nodeUuids for i in self.paths]
        return nodes

    def getEdges(self):
        edges = [i.edgeUuids for i in self.paths]
        return edges
