# -*- coding=utf-8 -*-

import redis
import traceback
from django.conf import settings


class RedisConPool(object):
    REDIS_POOL = 10000

    @staticmethod
    def getRedisConnection(self, db=10000):
        if db == RedisConPool.REDIS_POOL:
            args = settings.REDSI_KWARGS_LPUSH
            if not settings.REDSI_LPUSH_POOL:
                settings.REDSI_LPUSH_POOL = redis.ConnectionPool(host=args.get('host'), port=args.get('port'),
                                                                 db=args.get('db'))
                pools = settings.REDSI_LPUSH_POOL
        connection = redis.Redis(connection_pool=pools)
        return connection


class DsRedis(object):
    """
    封装常用操作涉及添加，删除，设置锁
    """

    @staticmethod
    def lpush(redisKey, data):
        try:
            redisConn = RedisConPool.getRedisConnection(RedisConPool.REDIS_POOL)
            redisConn.lpush(redisKey, data)
            redisConn = None
        except:
            return False

    @staticmethod
    def rpop(redisKey):
        try:
            redisConn = RedisConPool.getRedisConnection(RedisConPool.REDIS_POOL)
            data = redisConn.rpop(redisKey)
            redisConn = None
            return data
        except:
            return False

    @staticmethod
    def delete(redisKey):
        try:
            redisConn = RedisConPool.getRedisConnection(RedisConPool.REDIS_POOL)
            data = redisConn.delete(redisKey)
            redisConn = None
            return data
        except:
            return False

    @staticmethod
    def setlock(rkey, value):
        try:
            redisConn = RedisConPool.getRedisConnection(10000)
            redisConn.set(rkey, value)
            # redisConn.expire(redisKey, 1800)
            redisConn.expire(rkey, 1800)
            redisConn = None
        except:
            print(traceback.print_exc())
            return False

    @staticmethod
    def get(rkey):
        try:
            redisConn = RedisConPool.getRedisConnection(10000)
            result = redisConn.get(rkey)
            redisConn = None
            return result
        except:
            return False
