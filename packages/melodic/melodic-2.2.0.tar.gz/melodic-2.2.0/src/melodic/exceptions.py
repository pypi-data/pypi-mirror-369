"""Custom exceptions for the Melodic library."""


class MelodicError(Exception):
    """A base exception for all library-specific errors."""


class MelodicConfigError(MelodicError):
    """Raise for configuration-related errors, like invalid proxy formats."""


class SessionNotStartedError(MelodicError):
    """Raise when a network operation is attempted before starting a session."""


class NetworkError(MelodicError):
    """Raise for network issues, such as connection errors or bad responses."""

    def __init__(self, message: str, status: int | None = None):
        """Initialize the NetworkError.

        Args:
            message: The error message.
            status: The HTTP status code, if available.

        """
        super().__init__(message)
        self.status = status


class ArtistNotFoundError(NetworkError):
    """Raise when an artist's page returns a 404 Not Found error."""

    def __init__(self, message: str, status: int = 404):
        """Initialize the ArtistNotFoundError.

        Args:
            message: The error message.
            status: The HTTP status code.

        """
        super().__init__(message, status)


class LyricsNotFoundError(MelodicError):
    """Raise when lyrics cannot be found or parsed on a song page."""


class DiscographyNotFoundError(MelodicError):
    """Raise when an artist is found but has no listed songs."""
