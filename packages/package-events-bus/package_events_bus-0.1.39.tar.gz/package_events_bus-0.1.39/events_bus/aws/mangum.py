from mangum import Mangum
from typing import Generic
from mangum.types import (
    LambdaEvent,
    LambdaContext,
    LambdaConfig,
    LambdaHandler,
    ASGI,
    LifespanMode,
)

from ..core import (AsyncHandler, SyncHandler)
from ..typing import BaseEvent
from ..core.infrastructure.event_deserializer import EventDeserializer
from ..core.runtime.event_register import EventHandlerRegistry


class SQSEventBridgeHandler:
    """Handler for processing events from AWS SQS or EventBridge.
    This handler is designed to process events that are either received from
    an SQS queue or from an EventBridge event. It determines the type of event
    based on the structure of the incoming event and executes the appropriate
    handler registered in the `EventHandlerRegistry`.
    Args:
        event (LambdaEvent): The event data received from AWS Lambda.
        context (LambdaContext): The context object provided by AWS Lambda.
        config (LambdaConfig): Configuration settings for the handler.
    Raises:
        ValueError: If the event type is not recognized or if required fields are missing.
    """  # noqa: E501

    def __init__(
        self, event: LambdaEvent, context: LambdaContext, config: LambdaConfig
    ):
        self.event = event
        self.context = context
        self.config = config

    @classmethod
    def infer(
        cls, event: LambdaEvent, context: LambdaContext, config: LambdaConfig
    ) -> bool:
        return "Records" in event or "detail" in event

    def __get_handlers_by_event_name(self, event_name: str):
        handlers = EventHandlerRegistry.get_handlers_by_event(event_name)  # noqa: E501
        if not handlers:
            raise ValueError(f"No handler found for event type: {event_name}")
        return handlers

    def __execute_handlers_from_sqs(self):
        event_name = EventDeserializer.get_event_type_json(
            self.event["Records"][0]["body"]
        )
        handlers = self.__get_handlers_by_event_name(event_name)
        for handler in handlers:
            event = EventDeserializer.json_deserializer(
                self.event["Records"][0]["body"], handler=handler
            )
            self.execute_handler(handler, event)

    def __execute_handlers_from_event(self, event_name: str):
        handlers = self.__get_handlers_by_event_name(event_name)
        for handler in handlers:
            event = EventDeserializer.dict_deserializer(
                self.event, handler=handler
            )  # noqa: E501
            self.execute_handler(handler, event)

    def execute_handler(self, handler: SyncHandler | AsyncHandler,
                        event: Generic[BaseEvent]):
        """Execute the handler for the given event."""
        if isinstance(handler, SyncHandler):
            handler.handle(event)
        elif isinstance(handler, AsyncHandler):
            import asyncio
            loop = asyncio.get_event_loop()
            loop.run_until_complete(handler.handle(event))
        else:
            raise TypeError("Handler must be an instance of SyncHandler or AsyncHandler")  # noqa: E501

    def execute(self):
        """Execute the handler based on the event type."""
        if "Records" in self.event:
            self.__execute_handlers_from_sqs()
        elif "detail" in self.event:
            if "detail-type" not in self.event:
                raise ValueError("Event detail must contain 'detail-type' field.")  # noqa: E501
            event_name = self.event.get("detail-type", {})
            self.__execute_handlers_from_event(event_name)


class MangumExtended(Mangum):
    def __init__(
        self,
        app: ASGI,
        lifespan: LifespanMode = "auto",
        api_gateway_base_path: str = "/",
        custom_handlers: list[type[LambdaHandler]] | None = None,
        text_mime_types: list[str] | None = None,
        exclude_headers: list[str] | None = None,
    ) -> None:
        handlers = list(custom_handlers) if custom_handlers else []
        if SQSEventBridgeHandler not in handlers:
            handlers.append(SQSEventBridgeHandler)
        super().__init__(
            app,
            lifespan,
            api_gateway_base_path,
            handlers,
            text_mime_types,
            exclude_headers,
        )

    def __call__(self, event, context):
        handler = self.infer(event, context)
        if isinstance(handler, SQSEventBridgeHandler):
            return handler.execute()
        return super().__call__(event, context)
