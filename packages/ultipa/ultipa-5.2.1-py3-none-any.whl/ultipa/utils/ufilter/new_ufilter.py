from enum import Enum
from typing import List

from ultipa.utils.errors import ParameterException
from ultipa.utils.ufilter.ufilter import FilterBase


class FilterEnum(Enum):
    EQ = "=="
    NEQ = "!="
    LT = "<"
    LTE = "<="
    GT = ">"
    GTE = ">="
    BT = "<>"
    BTE = "<=>"
    OR = "||"
    AND = "&&"
    NOT = "!"
    IN = "in"
    NIN = "nin"


class Filter(FilterBase):
    # def __init__(self, name: str, value: object = None):
    #     self.propertyName = name
    #     self.value = value

    def builder(self):
        ...


class UltipaFilter(Filter):
    def __init__(self, schema: str = 'default', filterType: FilterEnum = None, property: str = None,
                 value: any = None):
        self.propertyName = property
        self.value = value
        self.opt = filterType
        self.schemaName = '@' + schema

    def builder(self):
        # if not self.propertyName and not self.value:
        #     return "{%s}"%self.schemaName.name
        # if not self.schemaName:
        #     return self.value
        if self.value == 0:
            self.value = '0'
        if self.propertyName and (not self.opt or self.value == None):
            raise ParameterException()

        if self.schemaName and self.propertyName and self.value != None and self.opt:
            if self.propertyName in ['_uuid', '_from_uuid', '_to_uuid']:
                return "%s %s %s" % (self.propertyName, self.opt.value, self.value)
            if self.propertyName in ['_id', '_from', '_to']:
                if isinstance(self.value, list):
                    return "%s %s %s" % (self.propertyName, self.opt.value, self.value)
                return "%s %s '%s'" % (self.propertyName, self.opt.value, self.value)
            if isinstance(self.value, list) or isinstance(self.value, int):
                return "%s.%s %s %s" % (self.schemaName, self.propertyName, self.opt.value, self.value)
            return "%s.%s %s '%s'" % (self.schemaName, self.propertyName, self.opt.value, self.value)
        if self.propertyName and self.value != None and self.opt:
            if isinstance(self.value, list) or isinstance(self.value, int):
                return "%s %s %s" % (self.propertyName, self.opt.value, self.value)
            return "%s %s '%s'" % (self.propertyName, self.opt.value, self.value)
        if self.schemaName and not self.propertyName:
            return "%s" % self.schemaName


class UltipaAndFilter(Filter):
    def __init__(self, values: List[UltipaFilter]):
        # super().__init__(propertyName, value)
        self.values = values

    def builder(self):
        va = []
        for i in self.values:
            if isinstance(i, Filter):
                va.append(i.builder())
            else:
                va.append(i)
        return " && ".join(va)


class UltipaOrFilter(Filter):
    def __init__(self, values: List[UltipaFilter]):
        # super().__init__(propertyName, value)
        self.values = values

    def builder(self):
        va = []
        for i in self.values:
            if isinstance(i, Filter):
                va.append(i.builder())
            else:
                va.append(i)
        return " || ".join(va)


class UltipaFilterList(FilterBase):

    def __init__(self, *args: UltipaFilter):
        self.firstFilter = args
        print(self.firstFilter)

    # def builder(self):
    #     for i in


# class LtFilter(Filter):
#     def __init__(self,schemaName:Schema, propertyName: str=None, value: any=None):
#         super().__init__(propertyName,value)
#         self.opt = FilterEnum.LT
#         self.schemaName = schemaName.name
#
#     def builder(self):
#         if not self.propertyName and not self.value:
#             return "{%s}"%self.schemaName
#         if not self.schemaName:
#             return self.value


if __name__ == '__main__':
    # ret = UltipaFilter(Schema('test'),filterType=FilterEnum.EQ)
    ret = UltipaFilter(filterType=FilterEnum.BTE, propertyName='test', value=1, schemaName='test')
    # ret1 = ret.builder()
    # print(ret1)
    # UltipaFilterList(ret, ret, ret)

    ret = UltipaAndFilter([ret, ret])
    print(ret.builder())
