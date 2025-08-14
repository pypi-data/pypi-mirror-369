import copy

from ultipa.structs.Retry import Retry, RetryResponse
from ultipa.types import ULTIPA


class RetryHelp:
    '''
        Configuration class that defines settings for the retry mechanism.
    '''
    currentRetry: Retry = None

    @staticmethod
    def getRty(requestConfig):

        nextRetry = Retry(current=0, max=3)

        if not RetryHelp.currentRetry:
            RetryHelp.currentRetry = copy.deepcopy(nextRetry)
        return RetryHelp.currentRetry, nextRetry

    @staticmethod
    def check(conn, requestConfig, response) -> RetryResponse:
        canRetry: bool = False
        currentRetry, nextRetry = RetryHelp.getRty(requestConfig)
        if response.status.code in [
            ULTIPA.ErrorCode.RAFT_REDIRECT,
            ULTIPA.ErrorCode.RAFT_LEADER_NOT_YET_ELECTED,
            ULTIPA.ErrorCode.RAFT_NO_AVAILABLE_FOLLOWERS,
            ULTIPA.ErrorCode.RAFT_NO_AVAILABLE_ALGO_SERVERS
        ]:
            if nextRetry.current < nextRetry.max:
                # redirectHost = response.status.clusterInfo.redirect
                # refresh = conn.refreshRaftLeader(redirectHost, requestConfig)
                # if refresh:
                nextRetry.current += 1
                canRetry = True
        reTry = RetryResponse(canRetry, currentRetry, nextRetry)
        return reTry

    @staticmethod
    def checkRes(response):
        if response.status.code in [
            ULTIPA.ErrorCode.RAFT_REDIRECT,
            ULTIPA.ErrorCode.RAFT_LEADER_NOT_YET_ELECTED,
            ULTIPA.ErrorCode.RAFT_NO_AVAILABLE_FOLLOWERS,
            ULTIPA.ErrorCode.RAFT_NO_AVAILABLE_ALGO_SERVERS
        ]:
            return True
        else:
            return False
