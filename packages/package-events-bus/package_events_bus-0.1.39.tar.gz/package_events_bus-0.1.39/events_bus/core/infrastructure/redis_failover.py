import json
import base64
from redis import Redis

from events_bus.typing import BaseEvent
from ..contracts.failover import BaseFailover


class RedisFailover(BaseFailover):
    KEY_PREFIX = "events_bus:failover:"

    def __init__(self, url: str):
        """
        Initialize the RedisFailover instance.

        Args:
            url (str): The URL of the Redis server.
        """
        self.redis = Redis.from_url(url)

    def publish(self, event_id: str, event_name: str, event_serialized: str):
        """
        Publish an event to the Redis failover mechanism.

        Args:
            event_id (str): The unique identifier of the event.
            event_serialized (str): The serialized representation of the event.
        """
        if not isinstance(event_id, str):
            raise TypeError(
                f"Expected event_id to be a str, got {type(event_id)}"
            )  # noqa: E501
        if not isinstance(event_serialized, str):
            raise TypeError(
                f"Expected event_serialized to be a str, got {type(event_serialized)}"  # noqa: E501
            )
        raw = {
            "content": base64.b64encode(
                json.dumps(
                    {
                        "event_id": event_id,
                        "event_name": event_name,
                        "event_serialized": event_serialized,
                    }  # noqa: E501
                ).encode("ascii")
            )
        }
        self.redis.hmset(self.__define_key(event_id), raw)

    def __define_key(self, event_id: str) -> str:
        return f"{self.KEY_PREFIX}{event_id}"

    def consume(self, total_events: int) -> list[BaseEvent]:
        """
        Consume events from the Redis failover mechanism.

        Args:
            total_events (int): The number of events to consume.

        Returns:
            list[BaseEvent]: A list of consumed events.
        """
        if not isinstance(total_events, int):
            raise TypeError(
                f"Expected total_events to be an int, got {type(total_events)}"
            )
        if total_events <= 0:
            raise ValueError("total_events must be a positive integer")
        keys = self.redis.keys(f"{self.KEY_PREFIX}*")
        if not keys:
            return []
        keys = keys[:total_events]
        events = []
        for key in keys:
            row = self.redis.hgetall(key)
            if not row:
                continue
            event = json.loads(base64.b64decode(row.get(b"content")).decode("ascii"))  # noqa: E501
            events.append(event)
            self.redis.delete(key)

        return events
