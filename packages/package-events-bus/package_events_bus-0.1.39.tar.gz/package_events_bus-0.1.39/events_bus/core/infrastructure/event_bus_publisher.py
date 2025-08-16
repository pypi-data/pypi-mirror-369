from abc import ABC, abstractmethod

from .. import BaseEvent


class EventBusPublisher(ABC):
    """Abstract base class for event bus publishers.
    This class defines the interface for publishing events to an event bus.
    Subclasses should implement the `publish` and `publish_batch` methods
    to publish events to the appropriate event bus
    (e.g., RabbitMQ, Kafka, EventBridge, etc.).
    """

    @abstractmethod
    def publish(self, event: BaseEvent) -> None:
        """Publish an event to the event bus.
        This method should be implemented by subclasses to publish the event
        to the appropriate event bus
        (e.g., RabbitMQ, Kafka, EventBridge, etc.).
        """
        pass

    @abstractmethod
    def publish_batch(self, events: list[BaseEvent]) -> None:
        """Publish a batch of events to the event bus.
        This method should be implemented by subclasses to publish the events
        to the appropriate event bus
        (e.g., RabbitMQ, Kafka, EventBridge, etc.).
        """
        pass

    @abstractmethod
    def publish_from_failover(total_events: int) -> None:
        """Publish events from the failover mechanism.
        This method should be implemented by subclasses to publish events
        that were stored in the failover mechanism.
        """
        pass
