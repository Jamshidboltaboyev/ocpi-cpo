import redis

from config.settings import CELERY_BROKER_URL


class RedisClient:
    redis_url = CELERY_BROKER_URL

    def __init__(self, url=redis_url):
        self.redis_client = redis.Redis.from_url(url)

    def get(self, key):
        value = self.redis_client.get(key)
        return value.decode("utf-8") if value else None

    def set(self, key, value, ttl=120):
        if ttl:
            self.redis_client.setex(key, ttl, value)
        else:
            self.redis_client.set(key, value)

    def delete(self, key):
        self.redis_client.delete(key)

    def get_ttl(self, key):
        return self.redis_client.ttl(key)

    def get_keys_values_by_pattern(self, pattern):
        keys = self.redis_client.keys(pattern)
        values = [self.get_value(key) for key in keys]
        return dict(zip(keys, values))

    def delete_keys(self, keys):
        self.redis_client.delete(*keys)

    def delete_keys_by_pattern(self, pattern):
        keys = self.redis_client.keys(pattern)
        self.delete_keys(keys)

    def get_keys_by_pattern(self, pattern):
        return self.redis_client.keys(pattern)
