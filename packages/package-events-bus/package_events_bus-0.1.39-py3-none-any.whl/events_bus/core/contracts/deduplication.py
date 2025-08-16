from abc import ABC


class BaseDeduplication(ABC):
    """
    Abstract base class for deduplication strategies.
    This class defines the interface for deduplication strategies.
    Subclasses should implement the `is_duplicate` method to check for duplicates
    and the `mark_as_processed` method to mark events as processed.
    Attributes:
        event_id (str): The unique identifier for the event.
        This is used to identify events and check for duplicates.
    """  # noqa: E501

    def __init__(self):
        """
        Initialize the BaseDeduplication instance.
        This method is called when an instance of a subclass is created.
        It can be used to set up any necessary resources or configurations.
        """
        pass

    def is_duplicate(self, event_id: str) -> bool:
        """
        Check if the given event ID is a duplicate.

        Args:
            event_id (str): The event ID to check for duplication.

        Returns:
            bool: True if the event ID is a duplicate, False otherwise.
        """
        pass

    def mark_as_processed(self, event_id: str):
        """
        Mark the given event ID as processed.

        Args:
            event_id (str): The event ID to mark as processed.
        """
        pass
