# -*- coding: utf-8 -*-
# @Time    : 2022/7/1 7:42 PM
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : ResposeFormat.py
import json
from typing import List


class ResponseKeyFormat:
    '''
        Processing class that defines settings for returnd-data formatting related operations.
    '''

    def __init__(self, jsonKeys: List[str] = None, boolKeys: List[str] = None, keyReplace: object = None,
                 dataFormat: List[str] = None, convert2Int: List[str] = None):
        self.jsonKeys = jsonKeys
        self.boolKeys = boolKeys
        self.keyReplace = keyReplace
        self.dataFormat = dataFormat
        self.convert2Int = convert2Int

    def changeKeyValue(self, objs):
        if objs:
            objs_list = []
            if type(objs) != list:
                objs_list = [objs]
            else:
                objs_list = objs
            for obj in objs_list:
                if self.jsonKeys:
                    for key in self.jsonKeys:
                        if key in obj:
                            obj[key] = json.loads(obj[key])
                if self.boolKeys:
                    for key in self.boolKeys:
                        if key in obj:
                            obj[key] = obj[key] == "true"
                if self.keyReplace:
                    for key in self.keyReplace.keys():
                        if key in obj:
                            obj[self.keyReplace[key]] = obj[key]
                            del obj[key]

                if self.convert2Int:
                    for key in self.convert2Int:
                        if key in obj:
                            obj[key] = int(obj[key])

                if self.dataFormat:
                    for gp in obj:
                        if gp in self.dataFormat:
                            dlist = []
                            for d in obj.get(gp):
                                dlist.append({'name': list(d.keys())[0], 'values': list(d.values())[0]})
                            obj[gp] = dlist
        return objs
