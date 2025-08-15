"""A Python client for fetching artist lyrical discographies."""

from melodic.client import Melodic
from melodic.exceptions import (
    ArtistNotFoundError,
    DiscographyNotFoundError,
    LyricsNotFoundError,
    MelodicConfigError,
    MelodicError,
    NetworkError,
    SessionNotStartedError,
)
from melodic.models import ClientConfig, Song, SongInfo

__all__ = [
    "Melodic",
    "ClientConfig",
    "MelodicError",
    "MelodicConfigError",
    "SessionNotStartedError",
    "NetworkError",
    "ArtistNotFoundError",
    "LyricsNotFoundError",
    "DiscographyNotFoundError",
    "Song",
    "SongInfo",
]
