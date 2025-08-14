# -*- coding: utf-8 -*-
# @Time    : 2023/7/18 11:59
# @Author  : Ultipa
# @Email   : support@ultipa.com
# @File    : commonUql.py

class GetProperty():
    '''
            This class defines the types of getProperty.

    '''
    node: str = 'show().node_property()'
    edge: str = 'show().edge_property()'


class GetPropertyBySchema():
    '''
                This class defines the types of getSchema.

        '''
    node: str = 'show().node_schema()'
    edge: str = 'show().edge_schema()'
