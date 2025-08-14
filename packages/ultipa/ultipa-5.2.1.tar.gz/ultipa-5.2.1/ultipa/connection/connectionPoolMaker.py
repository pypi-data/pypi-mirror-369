# -*- coding: utf-8 -*-
import queue
import threading
import time


class TooManyConnections(Exception):
    ...


class Expired(Exception):
    ...


class UsageExceeded(Expired):
    ...


class TtlExceeded(Expired):
    ...


class IdleExceeded(Expired):
    ...


class WrapperConnection(object):

    def __init__(self, pool, connection):
        self.pool = pool
        self.connection = connection
        self.usage = 0
        self.last = self.created = time.time()

    def using(self):
        self.usage += 1
        self.last = time.time()
        return self

    def reset(self):
        self.usage = self.last = self.created = 0

    def __enter__(self):
        return self.connection

    def __exit__(self, *exc_info):
        self.pool.release(self)


class ConnectionPool():
    '''
        Connection pool

    '''

    __wrappers = {}

    def __init__(self, create, close=None, max_size=3, max_usage=0, ttl=0, idle=120, block=True):
        if not hasattr(create, '__call__'):
            raise ValueError('"create" argument is not callable')

        if close is not None and not hasattr(close, '__call__'):
            raise ValueError('"close" argument is not callable')

        self._create = create
        self._close = close
        self._max_size = int(max_size)
        self._max_usage = int(max_usage)
        self._ttl = int(ttl)
        self._idle = int(idle)
        self._block = bool(block)
        self._lock = threading.Condition()
        self._pool = queue.Queue()
        self._size = 0
        if self._pool.qsize() == 0:
            while self._max_size:
                self._pool.put_nowait(self._wrapper(self._create()))
                self._max_size -= 1

    def item(self):
        self._lock.acquire()

        try:
            while (self._max_size and self._pool.empty() and self._size >= self._max_size):
                if not self._block:
                    raise TooManyConnections('Too many connections')

                self._lock.wait()  # Waiting for idle connections
            if self._pool.qsize() == 0:
                while self._max_size:
                    self._pool.put_nowait(self._wrapper(self._create()))
                    self._max_size -= 1
            try:
                wrapped = self._pool.get_nowait()  # Get an idle connection from the connection pool
                if self._idle and (wrapped.last + self._idle) < time.time():
                    self._destroy(wrapped, isCreate=True)
                    raise IdleExceeded('Idle exceeds %d secs' % self._idle)
            except (queue.Empty, IdleExceeded):
                wrapped = self._wrapper(self._create())  # Create new connection
                self._size += 1
        finally:
            self._lock.release()

        return wrapped.using()

    def release(self, conn):
        self._lock.acquire()
        wrapped = self._wrapper(conn)

        try:
            self._test(wrapped)
        except Expired:
            self._destroy(wrapped)
        else:
            self._pool.put_nowait(wrapped)
            self._lock.notifyAll()  # Notify the rest of threads on the availability of idle connection
        finally:
            self._lock.release()

    def _destroy(self, wrapped, isCreate: bool = False):
        if self._close:
            self._close(wrapped.connection)

        self._unwrapper(wrapped)
        self._size += 1
        if isCreate:
            self._pool.put_nowait(self._wrapper(self._create()))
            self._size -= 1

    def _wrapper(self, conn):
        if isinstance(conn, WrapperConnection):
            return conn

        _id = id(conn)

        if _id not in self.__wrappers:
            self.__wrappers[_id] = WrapperConnection(self, conn)

        return self.__wrappers[_id]

    def _unwrapper(self, wrapped):
        if not isinstance(wrapped, WrapperConnection):
            return

        _id = id(wrapped.connection)
        wrapped.reset()
        del wrapped

        if _id in self.__wrappers:
            del self.__wrappers[_id]

    def _test(self, wrapped):
        if self._max_usage and wrapped.usage >= self._max_usage:
            raise UsageExceeded('Usage exceeds %d times' % self._max_usage)

        if self._ttl and (wrapped.created + self._ttl) < time.time():
            raise TtlExceeded('TTL exceeds %d secs' % self._ttl)
