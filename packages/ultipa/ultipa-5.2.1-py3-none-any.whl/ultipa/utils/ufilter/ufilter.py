from typing import List

from ultipa.utils.checkStrTime import is_valid_date


class FilterOpt:
    EQ = "$eq"
    LT = "$lt"
    LTE = "$lte"
    GT = "$gt"
    GTE = "$gte"
    BT = "$bt"
    IN = "$in"
    OR = "$or"
    AND = "$and"
    NIN = "$nin"


class FilterBase:
    pass


class Filter(FilterBase):
    def __init__(self, name: str, value: object = None):
        self.name = name
        self.value = value

    def builder(self):
        if self.name == 'id':
            self.name = '_id'
        try:
            if is_valid_date(self.value):
                filter = '{%s:{%s:"%s"}}' % (self.name, self.opt, self.value)
            else:
                filter = '{%s:{%s:%s}}' % (self.name, self.opt, self.value)
            return filter
        except Exception as e:
            print(e)
            return "%s" % self.value


class EqFilter(Filter):
    def __init__(self, name: str, value: any):
        super().__init__(name, value)
        self.opt = FilterOpt.EQ

    def builder(self):
        if self.name == 'id':
            self.name = '_id'
        try:
            filter = '{%s:{%s:"%s"}}' % (self.name, self.opt, self.value)
            return filter
        except:
            return "%s" % self.value


class LtFilter(Filter):
    def __init__(self, name: str, value: any):
        super().__init__(name, value)
        self.opt = FilterOpt.LT


class LteFilter(Filter):
    def __init__(self, name: str, value: any):
        super().__init__(name, value)
        self.opt = FilterOpt.LTE


class GtFilter(Filter):
    def __init__(self, name: str, value: any):
        super().__init__(name, value)
        self.opt = FilterOpt.GT


class GteFilter(Filter):
    def __init__(self, name: str, value: any):
        super().__init__(name, value)
        self.opt = FilterOpt.GTE


class BtFilter(Filter):
    def __init__(self, name: str, value: object):
        super().__init__(name, value)
        self.opt = FilterOpt.BT

    def builder(self):
        if self.name == 'id':
            self.name = '_id'
        try:
            filter = '{%s:{%s:%s}}' % (self.name, self.opt, self.value)
            return filter
        except:
            return "%s" % self.value


class InFilter(Filter):
    def __init__(self, name: str, value: object):
        super().__init__(name, value)
        self.opt = FilterOpt.IN

    def builder(self):
        if self.name == 'id':
            self.name = '_id'
        try:
            filter = '{%s:{%s:%s}}' % (self.name, self.opt, self.value)
            return filter
        except:
            return "%s" % self.value


class NinFilter(Filter):
    def __init__(self, name: str, value: object):
        super().__init__(name, value)
        self.opt = FilterOpt.NIN

    def builder(self):
        if self.name == 'id':
            self.name = '_id'
        try:
            filter = '{%s:{%s:%s}}' % (self.name, self.opt, self.value)
            return filter
        except:
            return "%s" % self.value


class OrFilter(FilterBase):
    def __init__(self, value: List[Filter]):
        # super().__init__(name)
        self.value = value
        self.opt = FilterOpt.OR

    def builder(self):
        # if self.name == 'id':
        #     self.name = '_id'
        filter = '{%s:[%s]}' % (self.opt, ','.join([f.builder() for f in self.value]))
        return filter


class AndFilter(FilterBase):
    def __init__(self, value: List[Filter]):
        # super().__init__(name)
        self.value = value
        self.opt = FilterOpt.AND

    def builder(self):
        # if self.name == 'id':
        #     self.name = '_id'
        filter = '{%s:[%s]}' % (self.opt, ','.join([f.builder() for f in self.value]))
        # filter = filter.replace('"',"")
        return filter
