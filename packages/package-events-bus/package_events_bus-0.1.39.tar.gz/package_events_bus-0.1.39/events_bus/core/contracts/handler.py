from typing import Generic
from abc import ABC, abstractmethod


from events_bus.typing import BaseEvent


class BaseHandler(ABC, Generic[BaseEvent]):
    """
    Abstract base class for event handlers.
    This class defines the interface for handling events.
    Subclasses should implement the `handle` method to process the event.
    Attributes:
        event_type (type[BaseEvent]):
        The type of event that this handler can process.
    """
    @abstractmethod
    def handle(self, event: BaseEvent) -> None:
        pass


class SyncHandler(BaseHandler, Generic[BaseEvent]):
    """
    Synchronous event handler.
    This class implements the `handle` method to process events synchronously.
    """

    def handle(self, event: BaseEvent) -> None:
        """Handle the event synchronously.
        Args:
            event (BaseEvent): The event data to handle.
        """
        pass


class AsyncHandler(BaseHandler, Generic[BaseEvent]):
    """
    Asynchronous event handler.
    This class implements the `handle` method to process events asynchronously.
    """

    async def handle(self, event: BaseEvent) -> None:
        """Handle the event asynchronously.
        Args:
            event (BaseEvent): The event event to handle.
        """
        pass
        # Implement asynchronous event handling logic here
        # For example, you can process the event data and perform actions
        # based on the event type and data.
