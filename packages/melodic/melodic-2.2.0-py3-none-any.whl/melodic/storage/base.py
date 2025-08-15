"""Abstract base class for storage backends."""

from abc import ABC, abstractmethod

from melodic.models import Song


class StorageBase(ABC):
    """Define the abstract interface for storage implementations."""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the storage backend."""
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        """Close any open connections."""
        raise NotImplementedError

    @abstractmethod
    async def save_songs(self, songs: list[Song]) -> None:
        """Save a list of songs to the storage."""
        raise NotImplementedError
