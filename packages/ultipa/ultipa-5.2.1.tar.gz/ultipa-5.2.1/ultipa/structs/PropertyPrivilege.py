from typing import List


class PropertyPrivilegeElement:
    def __init__(self, read: List[List[str]] = None, write: List[List[str]] = None, deny: List[List[str]] = None):
        self.read = read
        self.write = write
        self.deny = deny

    def to_dict(self):
        self.__dict__.items()
        return {k: v for k, v in self.__dict__.items() if v is not None}


class PropertyPrivilege:
    def __init__(self, node: PropertyPrivilegeElement = None, edge: PropertyPrivilegeElement = None):
        self.node = node
        self.edge = edge

    def to_dict(self):
        result = {k: v for k, v in self.__dict__.items() if v is not None}.copy()
        for key, value in result.items():
            if hasattr(value, 'to_dict'):
                result[key] = value.to_dict()
        return result
