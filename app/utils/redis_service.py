import redis
import os
import datetime
from app.utils import (
    exceptions, helpers
)
from flask_jwt_extended import decode_token


def redis_client():
    '''
    define a redis client with os.environ variables.
    '''
    r = redis.Redis(
        host= os.environ.get('REDIS_HOST', 'localhost'),
        port= os.environ.get('REDIS_PORT', '6379'), 
        password= os.environ.get('REDIS_PASSWORD', None)
    )
    return r


def add_jwt_to_redis(claims):

    r = redis_client()

    jti = claims['jti']
    print(helpers._epoch_utc_to_datetime(claims['exp']) - datetime.datetime.utcnow())
    expires = datetime.timedelta(hours=1)

    try:
        r.set(jti, "", ex=expires)
    except :
        raise exceptions.APIException("connection error with redis host", status_code=500)

    pass