import logging


class LoggerConfig:
    '''
        A class that defines how log messages related to Ultipa connection are handled.

        It specifies settings such as log name, log file paths, log level, etc.
    '''

    def __init__(self, name: str, fileName: str = None, isWriteToFile: bool = False,
                 level: logging = logging.INFO, isStream: bool = False):
        self.name = name
        self.filename = fileName
        self.isWriteToFile = isWriteToFile
        self.level = level
        self.isStream = isStream

    def getlogger(self):
        fmt = '%(asctime)s - %(levelname)s: %(message)s'
        format_str = logging.Formatter(fmt)
        logger = logging.getLogger(self.name)
        logger.name = self.name
        logger.setLevel(level=self.level)
        if logger.handlers:
            return logger
        if self.isStream:
            sh = logging.StreamHandler()
            sh.setFormatter(format_str)
            logger.addHandler(sh)
        if self.isWriteToFile and self.filename:
            th = logging.FileHandler(filename=self.filename, encoding='utf-8', delay=True)
            th.setFormatter(format_str)
            logger.addHandler(th)
        return logger
