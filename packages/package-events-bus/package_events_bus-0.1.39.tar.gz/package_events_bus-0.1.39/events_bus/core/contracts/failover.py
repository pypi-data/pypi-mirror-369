from abc import abstractmethod


class BaseFailover:

    @abstractmethod
    def publish(self, event_id: str, event_name: str, event_serialized: str):
        """Publish an event to the failover mechanism.
        This method should be implemented by subclasses to publish the event
        to the appropriate failover mechanism.
        Args:
            event_id (str): The unique identifier of the event.
            event_name (str): The name of the event.
            event_serialized (str): The serialized representation of the event.
        """
        pass

    @abstractmethod
    def consume(self, total_events: int):
        """Consume an event from the failover mechanism.
        This method should be implemented by subclasses to consume the event
        from the appropriate failover mechanism.
        """
        pass
