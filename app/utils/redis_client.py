import os
import redis

def client():
    return redis.Redis(
        host= os.environ.get('REDIS_HOST', 'localhost'),
        port= int(os.environ.get('REDIS_PORT', '6379')),
        db= int(os.environ.get('REDIS_DB', '0'))
    )