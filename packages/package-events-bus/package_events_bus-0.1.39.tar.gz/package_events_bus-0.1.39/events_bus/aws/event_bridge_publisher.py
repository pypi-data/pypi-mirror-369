import boto3
import logging
import threading

from .. import (CONFIG, LOCAL_FAILOVER)
from ..core import (EventBusPublisher, EventJsonSerializer, BaseFailover)
from events_bus.typing import BaseEvent
from ..exceptions import EventBusNotFoundError


logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class EventBridgePublisher(EventBusPublisher):
    def __init__(
        self, bus_name: str, source: str,
        failover: BaseFailover = LOCAL_FAILOVER,
        aws_region_name: str | None = None
    ):
        """_summary_

        Args:
            bus_name (str): _description_
            source (str): _description_
            failover (BaseFailover, optional): _description_. Defaults to LocalFailover().
            aws_region_name (str | None, optional): _description_. Defaults to None.

        Raises:
            EventNotFoundError: _description_
        """  # noqa: E501
        self.bus_name = bus_name
        self.source = source
        self.aws_region_name = aws_region_name or CONFIG.AWS_REGION_NAME
        self.failover = failover
        self._load_client()

    def _load_client(self):
        self.client = boto3.client(
            "events",
            region_name=self.aws_region_name,
            endpoint_url=CONFIG.AWS_CLIENT_URL,
        )

    def set_failover(self, failover: BaseFailover):
        if failover is None:
            raise ValueError("Failover mechanism cannot be None.")
        self.failover = failover

    def set_aws_region(self, aws_region_name: str | None):
        self.aws_region_name = aws_region_name or CONFIG.AWS_REGION_NAME
        self._load_client()

    def publish(self, event: BaseEvent, wait_time: int | None = None):
        """Publish a single event to the EventBridge bus.
        Args:
            event (BaseEvent): The event to publish.
            wait_time (int | None, optional): If provided, the event will be published after this many seconds.
                Defaults to None, which means it will be published immediately.
        """  # noqa: E501
        # TODO: Add try/except for publish
        event_serialized = EventJsonSerializer.serialize(event)
        if wait_time is not None:
            timer = threading.Timer(
                wait_time, self._publish_raw, args=(event.event_id, event.event_name, event_serialized)  # noqa: E501
            )
            timer.start()
        else:
            self._publish_raw(event.event_id, event.event_name, event_serialized)  # noqa: E501

    def _publish_raw(
        self, event_id: str, event_name: str, event_serialized: str
    ):  # noqa: E501
        try:
            try:
                self.client.describe_event_bus(Name=self.bus_name)
            except self.client.exceptions.ResourceNotFoundException:
                raise EventBusNotFoundError(
                    event_name=self.bus_name, region_name=self.client.meta.region_name  # noqa: E501
                )
            self.client.put_events(
                Entries=[
                    {
                        "Source": self.source,
                        "DetailType": event_name,
                        "Detail": event_serialized,
                        "EventBusName": self.bus_name,
                    }
                ]
            )
        except (Exception, EventBusNotFoundError) as e:
            self.failover.publish(event_id, event_name, event_serialized)
            logger.error(
                f" Failed to publish event {event_id} to EventBridge: {e}"
            )

    def publish_batch(self, events: list[BaseEvent]):
        """Publish a batch of events to the EventBridge bus."""
        # TODO: Add try/except for publish_batch
        entries = []
        for event in events:
            entries.append(
                {
                    "Source": self.source,
                    "DetailType": event.event_name,
                    "Detail": EventJsonSerializer.serialize(event),
                    "EventBusName": self.bus_name,
                }
            )
        self.client.put_events(Entries=entries)

    def publish_from_failover(self, total_events: int):
        """Publish events from the failover mechanism."""
        events = self.failover.consume(total_events)
        for event in events:
            self._publish_raw(
                event_id=event["event_id"],
                event_name=event["event_name"],
                event_serialized=event["event_serialized"]
            )
