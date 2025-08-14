from ultipa import Connection, UltipaConfig
from ultipa.connection.connectionBase import ConnectionBase
from ultipa.connection.connectionPoolMaker import ConnectionPool


class UltipaConnectionPool():
    '''
        Ultipa connection pool class.

    '''

    def __init__(self, defaultConfig: UltipaConfig = UltipaConfig()):
        self.pool = ConnectionPool(lambda: Connection.NewConnection(defaultConfig=defaultConfig), max_size=10)

    def get_conn(self) -> ConnectionBase:
        with self.pool.item() as ultipa_cli:
            return ultipa_cli

    def __del__(self):
        conn = self.get_conn()
        wrapped = self.pool._wrapper(conn)
        self.pool._destroy(wrapped)

    def destroyConn(self, conn):
        wrapped = self.pool._wrapper(conn)
        self.pool._destroy(wrapped)
