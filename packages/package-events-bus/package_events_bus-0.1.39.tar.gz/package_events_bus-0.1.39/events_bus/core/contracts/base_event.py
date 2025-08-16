import uuid
from datetime import (datetime, timezone)
from abc import ABC, abstractmethod


__TOPIC_REGEX = r'^[a-zA-Z0-9_]+\.[a-zA-Z0-9_]+\.\d+\.(command|event)\.[a-zA-Z0-9_]+\.[a-zA-Z0-9_]+$'  # noqa: E501


class BaseEvent(ABC):
    """
    Base class for all events.

    This class defines the interface for all events in the system.
    It provides methods to convert events to and from dictionaries,
    and to get the event type.

    Attributes:
        event_name (str): The fully qualified name of the event topic.
            Must follow the format:
                [company].[service].[version].[message_type].[resource_name].[event_command_name]
            Where:
                - company (str): Name of the company (e.g., 'finkargo').
                - service (str): Name of the service emitting the event (e.g., 'portfolio', 'documents').
                - version (int): Numeric version of the event (e.g., 1, 2).
                - message_type (str): Either 'command' or 'event'.
                - resource_name (str): The resource/entity the event is related to (e.g., 'disbursement').
                - event_command_name (str):
                    - If message_type is 'event': must be a verb in past tense (e.g., 'created', 'updated', 'deleted').
                    - If message_type is 'command': must be a verb in infinitive form (e.g., 'create', 'send').
        event_id (str): A unique identifier for the event.

        occurred_on (datetime): The timestamp indicating when the event occurred.

    """     # noqa: E501

    def __init__(self,
                 event_name: str,
                 event_id: str | None = None,
                 occurred_on: datetime | None = None):
        self.event_name = event_name
        self.event_id = uuid.uuid4().hex if event_id is None else event_id
        self.occurred_on = datetime.now(
            tz=timezone.utc) if occurred_on is None else occurred_on

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, event_id: str, occurred_on: datetime, attributes: dict) -> "BaseEvent":  # noqa: E501
        pass
