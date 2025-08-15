"""Functions for parsing HTML."""

import logging
import re
import unicodedata

from bs4 import BeautifulSoup
from bs4.element import Tag

from melodic import constants
from melodic.exceptions import MelodicError
from melodic.models import SongInfo

logger = logging.getLogger(__name__)


def _clean_artist_name(name: str) -> str:
    """Normalize an artist's name for the URL path.

    Args:
        name: The raw artist name.

    Returns:
        The URL-safe artist name.

    Raises:
        MelodicError: If the name is empty or becomes empty
            after cleaning.

    """
    if not name or not name.strip():
        raise MelodicError("Artist name cannot be empty.")

    # Normalize to remove accents (e.g., 'é' -> 'e')
    try:
        normalized = unicodedata.normalize("NFKD", name)
        ascii_name = normalized.encode("ASCII", "ignore").decode("utf-8")
    except Exception as e:
        raise MelodicError(f"Failed to normalize artist name: {name}") from e

    # Perform common substitutions (e.g., Ke$ha -> kesha)
    substituted_name = ascii_name.replace("$", "s")

    # Clean to keep only lowercase letters and numbers
    cleaned = re.sub(r"[^a-z0-9]", "", substituted_name.lower())

    if not cleaned:
        raise MelodicError(
            f"Cleaning artist name '{name}' resulted in an empty string."
        )

    return cleaned


def get_artist_url(artist_name: str) -> str:
    """Construct the URL for an artist's page.

    Args:
        artist_name: The name of the artist.

    Returns:
        The full URL for the artist's page.

    """
    cleaned_name = _clean_artist_name(artist_name)
    return f"{constants.BASE_URL}/{cleaned_name[0]}/{cleaned_name}.html"


def parse_artist_page(html: str) -> list[SongInfo]:
    """Parse the artist's main page to find all song links.

    Args:
        html: The HTML content of the artist's page.

    Returns:
        A SongInfo object for each song found.

    """
    soup = BeautifulSoup(html, "lxml")

    songs = []

    # Extract artist name
    artist_name_tag = soup.find("h1")
    artist_name = (
        artist_name_tag.text.replace(" Lyrics", "").strip()
        if artist_name_tag and isinstance(artist_name_tag, Tag)
        else "Unknown Artist"
    )

    album_name = "Uncategorized"
    for element in soup.select("div#listAlbum > *"):
        if not isinstance(element, Tag):
            continue

        # Album names are in divs with class "album"
        class_attr = element.get("class")
        classes: list[str] = class_attr if isinstance(class_attr, list) else []
        if element.name == "div" and "album" in classes:
            album_name_tag = element.find("b")
            if album_name_tag:
                album_name = album_name_tag.text.strip().strip('"')
            else:
                album_name = "other songs"

        # Song links are either <a> tags or inside divs with class "listalbum-item"
        elif element.name == "a" or (
            element.name == "div" and "listalbum-item" in classes
        ):
            link = element if element.name == "a" else element.find("a")
            if not link or not isinstance(link, Tag):
                continue

            href = link.get("href")
            if not href or not isinstance(href, str) or not href.startswith("/lyrics"):
                continue

            song_url = f"{constants.BASE_URL}{href.removeprefix('../')}"
            song_title = link.text.strip()
            songs.append(
                SongInfo(
                    artist=artist_name,
                    title=song_title,
                    album=album_name,
                    url=song_url,
                )
            )
    return songs


def parse_song_page(html: str) -> str:
    """Parse the song page to extract the lyrics.

    Args:
        html: The HTML content of the song's page.

    Returns:
        The extracted lyrics as a string.

    """
    soup = BeautifulSoup(html, "lxml")

    ringtone_div = soup.find("div", class_="ringtone")
    if not ringtone_div or not isinstance(ringtone_div, Tag):
        return ""

    lyrics_div = ringtone_div.find_next("div")
    if lyrics_div and isinstance(lyrics_div, Tag):
        # get_text with a separator is the cleanest way to handle <br> tags
        return lyrics_div.get_text(separator="\n", strip=True)

    return ""
