from typing import TypeVar
from events_bus.core.contracts.base_event import BaseEvent as Event


BaseEvent = TypeVar("BaseEvent", bound=Event)
