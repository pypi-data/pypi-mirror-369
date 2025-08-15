"""A Python client for fetching artist lyrical discographies."""

import asyncio
import logging
import types
from pathlib import Path
from typing import cast

from melodic import constants
from melodic.exceptions import (
    ArtistNotFoundError,
    DiscographyNotFoundError,
    NetworkError,
    SessionNotStartedError,
)
from melodic.models import ClientConfig, Song, SongInfo
from melodic.network.manager import NetworkManager
from melodic.parser import get_artist_url, parse_artist_page, parse_song_page
from melodic.storage.base import StorageBase
from melodic.storage.sqlite import SQLiteStorage

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Melodic:
    """An asynchronous client for fetching artist lyrical discographies."""

    def __init__(self, config: ClientConfig | None = None) -> None:
        """Initialize the Melodic client.

        Args:
            config: Configuration settings for the client.

        """
        if config is None:
            config = ClientConfig()

        self._network_manager = NetworkManager(
            proxies=config.proxies,
            max_concurrent_requests=config.max_concurrent_requests,
            request_delay=config.request_delay,
            user_agent=config.user_agent,
        )

        self._storage = (
            SQLiteStorage(Path(config.storage_path)) if config.storage_path else None
        )

        self._batch_save_size = config.batch_save_size
        self._is_open = False
        logger.info("Melodic instance has been initialized.")

    async def __aenter__(self) -> "Melodic":
        """Initialize resources for the async context.

        Returns:
            The initialized Melodic instance.

        """
        await self._network_manager.start_session()
        if self._storage:
            await self._storage.initialize()
        self._is_open = True
        logger.debug("Melodic context entered and resources initialized.")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        """Close resources upon exiting the async context."""
        await self._network_manager.close_session()
        if self._storage:
            await self._storage.close()
        self._is_open = False
        logger.debug("Melodic context exited and resources closed.")

    async def get_discography(self, artist_name: str) -> dict[str, list[Song]]:
        """Fetch and process the complete discography for a given artist.

        Args:
            artist_name: The name of the artist.

        Returns:
            A dictionary mapping album names to lists of Song objects.

        Raises:
            SessionNotStartedError: If called outside an async with block.
            ArtistNotFoundError: If the artist cannot be found on the server.
            DiscographyNotFoundError: If the artist is found but has no songs.

        """
        if not self._is_open:
            raise SessionNotStartedError(
                "Resources not initialized. Use an async with block."
            )

        logger.info("Fetching discography for artist: '%s'", artist_name)
        artist_url = get_artist_url(artist_name)

        try:
            artist_page_html = await self._network_manager.get(artist_url)
        except NetworkError as e:
            if e.status == constants.HTTP_STATUS_NOT_FOUND:
                raise ArtistNotFoundError(f"Artist '{artist_name}' not found.") from e
            raise

        song_infos = parse_artist_page(artist_page_html)
        if not song_infos:
            raise DiscographyNotFoundError(f"No songs found for '{artist_name}'.")

        total_song_count = len(song_infos)
        tasks = [
            asyncio.create_task(self._fetch_and_parse_song(artist_name, info))
            for info in song_infos
        ]
        all_songs: list[Song] = []

        # Process tasks in chunks to save progress periodically
        for i in range(0, len(tasks), self._batch_save_size):
            chunk_tasks = tasks[i : i + self._batch_save_size]
            logger.info(
                "Processing song batch %d-%d of %d...",
                i + 1,
                min(i + self._batch_save_size, len(tasks)),
                len(tasks),
            )
            results = await asyncio.gather(*chunk_tasks, return_exceptions=True)

            chunk_songs = [song for song in results if isinstance(song, Song)]
            all_songs.extend(chunk_songs)

            if self._storage and chunk_songs:
                storage = cast(StorageBase, self._storage)
                await storage.save_songs(chunk_songs)

        discography: dict[str, list[Song]] = {}
        for song in all_songs:
            discography.setdefault(song.album, []).append(song)

        logger.info(
            "Successfully fetched %d/%d song lyrics for '%s'.",
            len(all_songs),
            total_song_count,
            artist_name,
        )
        return discography

    async def _fetch_and_parse_song(
        self, artist: str, song_info: SongInfo
    ) -> Song | None:
        """Fetch, parse, and create a Song object.

        Args:
            artist: The name of the artist.
            song_info: A SongInfo object with the song's URL and metadata.

        Returns:
            A Song object if successful, otherwise None.

        """
        try:
            song_html = await self._network_manager.get(song_info.url)
            lyrics = parse_song_page(song_html)

            if not lyrics:
                logger.warning(
                    "Could not find lyrics for '%s' at %s",
                    song_info.title,
                    song_info.url,
                )
                return None

            return Song(
                artist=artist,
                title=song_info.title,
                album=song_info.album,
                lyrics=lyrics,
                url=song_info.url,
            )
        except NetworkError as e:
            logger.warning("Failed to fetch song '%s': %s", song_info.title, e)
            return None
