import json


from .. import BaseEvent


class EventJsonSerializer:
    """A class for serializing events to and from JSON
    format. This class provides methods to convert event objects to JSON
    strings and to create event objects from JSON strings.
    """

    @staticmethod
    def serialize(event: type[BaseEvent]) -> str:
        """Convert an event object to a JSON string.
        Args:
            event (BaseEvent): The event object to serialize.
        Returns:
            str: The JSON string representation of the event.
        """
        if not isinstance(event, BaseEvent):
            raise TypeError(f"Expected an instance of BaseEvent, got {type(event)}")  # noqa: E501
        return json.dumps(
            {
                "id": event.event_id,
                "type": event.event_name,
                "occurred_on": event.occurred_on.isoformat(),
                "attributes": json.dumps(event.to_dict(), default=str),
            },
            default=str,
        )
