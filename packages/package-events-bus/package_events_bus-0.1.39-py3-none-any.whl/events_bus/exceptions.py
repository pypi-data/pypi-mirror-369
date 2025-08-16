from .core.contracts.handler import BaseHandler


class HandlerExecutionError(BaseException):
    """
    Exception raised when an event handler fails to execute.
    """

    def __init__(self, handler: BaseHandler, event_name: str):
        super().__init__()
        self.handler = handler
        self.event_name = event_name

    def __str__(self):
        return (
            f"Error processing event {self.event_name} with handler "
            f"{self.handler.__class__.__name__}"
        )


class DeserializationEventError(BaseException):
    """
    Exception raised when an event cannot be deserialized.
    """

    def __init__(self, handler: BaseHandler):
        super().__init__()
        self.handler = handler

    def __str__(self):
        return f"Error deserializing event with handler {self.handler.__class__.__name__}"  # noqa: E501


class EventBusNotFoundError(BaseException):
    """
    Exception raised when an event is not found in the registry.
    """

    def __init__(self, event_name: str, region_name: str | None = None):
        super().__init__()
        self.event_name = event_name
        self.region_name = region_name

    def __str__(self):
        return f"Event '{self.event_name}' not found in the registry" + (
            f" for region '{self.region_name}'" if self.region_name else ""
        )
