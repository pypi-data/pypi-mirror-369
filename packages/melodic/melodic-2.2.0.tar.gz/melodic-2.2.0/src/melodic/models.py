"""Dataclasses for representing song data."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SongInfo:
    """A temporary object holding a song's URL and metadata."""

    artist: str
    album: str
    title: str
    url: str


@dataclass(frozen=True)
class Song:
    """The final representation of a song, including its lyrics."""

    artist: str
    album: str
    title: str
    lyrics: str
    url: str


@dataclass
class ClientConfig:
    """Configuration settings for the Melodic client."""

    storage_path: str | Path | None = None
    proxies: list[str] | None = None
    max_concurrent_requests: int = 10
    request_delay: float = 3.5
    user_agent: str | None = None
    batch_save_size: int = 20
