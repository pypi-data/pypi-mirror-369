
class ParameterException(Exception):
    '''
        Class for customizing errors related to parameter
    '''

    def __init__(self, err='Parameter error!'):
        Exception.__init__(self, err)


class ServerException(Exception):
    '''
       Class for customizing errors related to server connection
    '''

    def __init__(self, err='Server connection failed!'):
        Exception.__init__(self, err)


class SerializeException(Exception):
    '''
       Class for customizing errors related to serialization
    '''

    def __init__(self, err='Serialize failed!'):
        Exception.__init__(self, err)


class SettingException(Exception):
    '''
        Class for customizing errors related to settings
    '''

    def __init__(self, err='Setting error!'):
        Exception.__init__(self, err)


def checkError(error: str):
    '''
        Method for customizing errors related to parameter validation
    '''
    if "large" in error:
        return "argument out of range"
    else:
        return error
