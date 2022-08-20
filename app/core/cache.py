import redis
from app.core.config import settings


def get_redis_connection():
    return redis.Redis(settings.REDIS_HOST, settings.REDIS_PORT)
