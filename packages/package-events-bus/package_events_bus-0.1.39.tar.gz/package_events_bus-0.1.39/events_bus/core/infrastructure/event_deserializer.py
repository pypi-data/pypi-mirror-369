import json
from datetime import datetime
from typing import get_type_hints


from ...exceptions import DeserializationEventError
from .. import BaseEvent, BaseHandler


class EventDeserializer:
    """
    Base class for event deserializers.
    """

    @staticmethod
    def json_deserializer(event_json: str, handler: BaseHandler) -> BaseEvent:
        """Convert a JSON string to an event object.
        Args:
            event_json (str): The JSON string to deserialize.
            handler (BaseHandler): The handler to determine the event type.
        Returns:
            BaseEvent: The event object created from the JSON string.
        """
        if not isinstance(event_json, str):
            raise TypeError(f"Expected a JSON string, got {type(event_json)}")
        try:
            json_obj = json.loads(event_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e.msg}") from e
        if "detail" not in json_obj:
            raise ValueError("Invalid JSON format: 'detail' key not found.")
        data = EventDeserializer._validate_and_extract_data(json_obj)  # noqa: E501
        attributes = json.loads(data["attributes"])
        event_id = data["id"]
        occurred_on = datetime.fromisoformat(data["occurred_on"])
        event_class = EventDeserializer._get_event_type_from_handler(
            handler
        )  # noqa: E501
        try:
            return event_class.from_dict(
                attributes=attributes,
                event_id=event_id,
                occurred_on=occurred_on,
            )
        except Exception as e:
            raise DeserializationEventError(handler) from e

    def dict_deserializer(event_dict: dict, handler: BaseHandler) -> BaseEvent:
        """Convert a dictionary to an event object.
        Args:
            event_dict (dict): The dictionary to deserialize.
            handler (BaseHandler): The handler to determine the event type.
        Returns:
            BaseEvent: The event object created from the dictionary.
        """
        if not isinstance(event_dict, dict):
            raise TypeError(f"Expected a dictionary, got {type(event_dict)}")
        data = EventDeserializer._validate_and_extract_data(event_dict)
        attributes = json.loads(data["attributes"])
        if not isinstance(attributes, dict):
            raise TypeError(
                f"Expected 'attributes' to be a dictionary, got {type(attributes)}"  # noqa: E501
            )
        event_id = data["id"]
        occurred_on = datetime.fromisoformat(data["occurred_on"])
        event_class = EventDeserializer._get_event_type_from_handler(handler)
        try:
            return event_class.from_dict(
                attributes=attributes,
                event_id=event_id,
                occurred_on=occurred_on,
            )
        except Exception as e:
            raise DeserializationEventError(handler) from e

    @staticmethod
    def _get_event_type_from_handler(
        handler: BaseHandler,
    ) -> type[BaseEvent]:  # noqa: E501
        """Get the event type from the handler."""
        if not isinstance(handler, BaseHandler):
            raise TypeError(
                f"Expected an instance of BaseHandler, got {type(handler)}"
            )  # noqa: E501
        cls = handler.__class__

        return EventDeserializer.get_event_type_from_class_handler(cls)  # noqa: E501

    def get_event_type_from_class_handler(
        handler: type[BaseHandler],
    ) -> type[BaseEvent]:  # noqa: E501
        cls = handler

        method = getattr(cls, "handle", None)
        if method is None:
            raise ValueError(
                f"Handler {cls.__name__} does not have a 'handle' method."
            )  # noqa: E501

        type_hints = get_type_hints(method)
        event = type_hints.get("event", None)
        if event is None:
            raise ValueError(
                f"Handler {cls.__name__} does not specify a 'data' type hint in its 'handle' method."  # noqa: E501
            )
        if not issubclass(event, BaseEvent):
            raise ValueError(
                f"Handler {cls.__name__} does not handle a valid BaseEvent type."  # noqa: E501
            )
        return event

    @staticmethod
    def _validate_and_extract_data(json_obj: dict) -> dict:
        """Validate and extract data from the detail dictionary."""
        if "detail" not in json_obj:
            raise ValueError('Invalid JSON format: "detail" key not found.')
        data = json_obj["detail"]
        missing_keys = [
            key
            for key in ["attributes", "id", "occurred_on"]
            if key not in data  # noqa: E501
        ]
        if missing_keys:
            raise ValueError(
                'Invalid JSON format: Missing keys in "detail": '
                + ", ".join(missing_keys)
            )
        return data

    @staticmethod
    def get_event_type_json(msg: str) -> str:
        try:
            json_obj = json.loads(msg)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e.msg}") from e
        if "detail-type" not in json_obj:
            raise ValueError(
                'Invalid JSON format: "detail-type" key not found.'
            )  # noqa: E501
        return json_obj["detail-type"]
