from .. import BaseHandler

from typing import Generic
from events_bus.typing import BaseEvent


class EventHandlerRegistry:
    """Registry for event handlers.
    This class is responsible for registering event handlers and
    providing access to them.
    """
    _registry_queues: dict[str, BaseHandler[Generic[BaseEvent]]] = {}
    _registry_handlers: dict[str, list[BaseHandler[Generic[BaseEvent]]]] = {}

    @classmethod
    def register_by_queue(cls, queue_url: str, handler: BaseHandler[Generic[BaseEvent]]):  # noqa: E501
        """Register an event handler associated with a specific queue URL.
        Args:
            queue_url (str): The URL of the queue to which the handler is
            associated.
            handler (BaseHandler): The event handler to register.
        """
        cls._registry_queues[queue_url] = handler

    @classmethod
    def register_handler(cls, event_name: str, handler: BaseHandler[Generic[BaseEvent]]):   # noqa: E501
        """Register an event handler without a specific queue URL.
        Args:
            handler (BaseHandler): The event handler to register.
        """
        if not isinstance(handler, BaseHandler):
            raise TypeError(f"Expected a BaseHandler, got {type(handler)}")
        if next(
            (h for h in cls._registry_handlers.get(event_name, []) if h.__class__ == handler.__class__),  # noqa: E501
            None,
        ):
            raise ValueError(
                f"Handler {handler.__class__.__name__} is already registered for event '{event_name}'."  # noqa: E501
            )
        cls._registry_handlers.setdefault(event_name, []).append(handler)

    @classmethod
    def register_multiple_handlers(cls, handlers: list[tuple[str, BaseHandler[Generic[BaseEvent]]]]):  # noqa: E501
        """Register multiple event handlers at once.
        Args:
            handlers (list[tuple[str, BaseHandler]]): A list of tuples where
            each tuple contains an event name and its associated handler.
            Example: [("event_name", handler), ...]
        """
        if not isinstance(handlers, list):
            raise TypeError("Expected a list of handlers.")
        for event_name, handler in handlers:
            cls.register_handler(event_name, handler)

    @classmethod
    def get_handlers_with_queues(cls) -> dict[str, BaseHandler[Generic[BaseEvent]]]:  # noqa: E501
        """Get all registered event handlers.
        Returns:
            dict[str, BaseHandler]: A dictionary mapping queue URLs to
            their associated event handlers.
        """
        return cls._registry_queues

    @classmethod
    def get_handlers_by_event(cls, event_name: str) -> list[BaseHandler[Generic[BaseEvent]]]:  # noqa: E501
        """Get all registered event handlers.
        Returns:
            dict[str, BaseHandler]: A dictionary mapping event names to
            their associated event handlers.
        """
        return cls._registry_handlers.get(event_name, [])
