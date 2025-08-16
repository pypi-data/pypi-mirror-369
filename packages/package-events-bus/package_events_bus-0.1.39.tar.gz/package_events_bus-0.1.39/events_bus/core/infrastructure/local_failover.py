from ..contracts.failover import BaseFailover


class LocalFailover(BaseFailover):
    def __init__(self):
        """
        Initialize the LocalFailover instance.
        This failover mechanism does not require any external resources.
        """
        self.events = {}

    def publish(self, event_id: str, event_name: str, event_serialized: str):
        """
        Publish an event to the local failover mechanism.

        Args:
            event_id (str): The unique identifier of the event.
            event_name (str): The name of the event.
            event_serialized (str): The serialized representation of the event.
        """
        if not isinstance(event_id, str):
            raise TypeError(f"Expected event_id to be a str, got {type(event_id)}")  # noqa: E501
        if not isinstance(event_serialized, str):
            raise TypeError(
                f"Expected event_serialized to be a str, got {type(event_serialized)}"  # noqa: E501
            )

        self.events[event_id] = {
            "event_name": event_name,
            "event_serialized": event_serialized,
        }

    def consume(self, total_events: int):
        """
        Consume events from the local failover mechanism.
        Args:
            total_events (int): The number of events to consume.
        Returns:
            list[BaseEvent]: A list of consumed events.
        """
        if not isinstance(total_events, int):
            raise TypeError(
                f"Expected total_events to be an int, got {type(total_events)}"
            )

        consumed_events = []
        for event_id, event_data in list(self.events.items())[:total_events]:
            consumed_events.append(
                {
                    "event_id": event_id,
                    "event_name": event_data["event_name"],
                    "event_serialized": event_data["event_serialized"],
                }
            )
            del self.events[event_id]

        return consumed_events
