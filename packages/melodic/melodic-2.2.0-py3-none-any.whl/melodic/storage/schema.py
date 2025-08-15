"""Database schema for Melodic."""

CREATE_SONGS_TABLE = """
CREATE TABLE IF NOT EXISTS songs (
    id INTEGER PRIMARY KEY,
    artist TEXT NOT NULL,
    album TEXT NOT NULL,
    title TEXT NOT NULL,
    lyrics TEXT NOT NULL,
    url TEXT NOT NULL,
    UNIQUE(artist, title)
);
"""
