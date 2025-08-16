import redis
from ..contracts.deduplication import BaseDeduplication


class RedisDeduplication(BaseDeduplication):
    """
    Deduplication strategy using Redis.
    This class implements the deduplication strategy using Redis as the backend.
    It checks for duplicates and marks events as processed using Redis.
    """  # noqa: E501

    def __init__(self, url: str, ttl: int = 3600):
        """
        Initialize the RedisDeduplication instance.
        Args:
            url (str): The Redis server URL. This should be a valid Redis URL
            in the format 'redis://[:password]@hostname:port/db_number'.
            Review the Redis documentation for more details on the URL format.
            ttl (int): Time to live for the event in seconds.
            Default is 3600 seconds (1 hour).
        """
        super().__init__()
        self.redis_client = redis.Redis.from_url(url)
        self.ttl = ttl

    def is_duplicate(self, event_id: str) -> bool:
        return self.redis_client.exists(event_id) > 0

    def mark_as_processed(self, event_id: str):
        self.redis_client.set(event_id, "processed", ex=self.ttl)
