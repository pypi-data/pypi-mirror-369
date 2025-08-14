# -*- coding: utf-8 -*-
# @Time    : 2023/12/15 14:49
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : PointType.py
class PointType:

    @staticmethod
    def PointFunction(latitude: float, longitude: float):
        return "point({latitude:%s, longitude:%s})" % (latitude, longitude)

    @staticmethod
    def PointString(latitude: float, longitude: float):
        return f"POINT({latitude} {longitude})"
