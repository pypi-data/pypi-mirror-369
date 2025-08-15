"""SQLite implementation of the storage backend."""

import logging
from pathlib import Path

import aiosqlite

from melodic.models import Song
from melodic.storage.base import StorageBase
from melodic.storage.schema import CREATE_SONGS_TABLE

logger = logging.getLogger(__name__)


class SQLiteStorage(StorageBase):
    """A storage backend that saves discographies to a SQLite database."""

    def __init__(self, db_path: str | Path) -> None:
        """Initialize the SQLiteStorage backend.

        Args:
            db_path: The file path where the SQLite database will be stored.

        """
        self._db_path = Path(db_path)
        self._connection: aiosqlite.Connection | None = None

    async def initialize(self) -> None:
        """Connect and configure the database tables and attributes.."""
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = await aiosqlite.connect(self._db_path)

        await self._connection.execute("PRAGMA journal_mode = WAL;")
        await self._connection.execute("PRAGMA synchronous = NORMAL;")
        await self._connection.execute("PRAGMA temp_store = MEMORY;")
        await self._connection.execute(CREATE_SONGS_TABLE)
        await self._connection.commit()

        logger.debug("SQLite database initialized at %s.", self._db_path)

    async def close(self) -> None:
        """Close the active database connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None
            logger.debug("SQLite database connection closed.")

    async def save_songs(self, songs: list[Song]) -> None:
        """Save a list of songs to the database in a single transaction.

        Args:
            songs: A list of Song objects to be saved.

        Raises:
            ConnectionError: If the database is not initialized.

        """
        if not self._connection:
            raise ConnectionError("Database is not initialized. Call initialize first.")
        if not songs:
            return

        sql = (
            "INSERT OR IGNORE INTO songs (artist, album, title, lyrics, url) "
            "VALUES (?, ?, ?, ?, ?)"
        )
        data_to_insert = [
            (song.artist, song.album, song.title, song.lyrics, song.url)
            for song in songs
        ]

        await self._connection.executemany(sql, data_to_insert)
        await self._connection.commit()
        logger.info("Attempted to save %d songs to the database.", len(songs))
