"""A client to handle network operations."""

import asyncio
import logging
import random
import time

import aiohttp
from aiohttp_socks import ProxyConnector

from melodic.constants import DEFAULT_USER_AGENT, HTTP_STATUS_NOT_FOUND
from melodic.exceptions import (
    ArtistNotFoundError,
    MelodicConfigError,
    NetworkError,
    SessionNotStartedError,
)

logger = logging.getLogger(__name__)
VALID_PROXY_SCHEMES = ("http://", "socks4://", "socks5://")


class NetworkManager:
    """Manage network requests, including proxy rotation and rate limiting."""

    def __init__(
        self,
        proxies: list[str] | None = None,
        max_concurrent_requests: int = 10,
        request_delay: float = 3.5,
        user_agent: str | None = None,
    ) -> None:
        """Initialize the NetworkManager.

        Args:
            proxies: A list of proxy URLs.
            max_concurrent_requests: Max number of simultaneous requests.
            request_delay: Min delay (in seconds) between requests from the same
                proxy/IP.
            user_agent: The User-Agent string for requests. Defaults to a common
                browser agent.

        Raises:
            MelodicConfigError: If a proxy URL has an invalid format.

        """
        self._request_delay = request_delay
        self._user_agent = user_agent or DEFAULT_USER_AGENT

        if proxies:
            # Validate each proxy format before proceeding
            for proxy in proxies:
                if not proxy.startswith(VALID_PROXY_SCHEMES):
                    raise MelodicConfigError(
                        f"Invalid proxy format: '{proxy}'. "
                        f"Proxy must start with one of {VALID_PROXY_SCHEMES}."
                    )

        # State for managing statuses of proxies
        self._proxy_cooldowns: dict[str | None, float] = (
            {p: 0.0 for p in proxies} if proxies else {None: 0.0}
        )
        self._dead_proxies: set[str] = set()
        self._proxy_lock = asyncio.Lock()

        # Determine concurrency limit
        num_resources = len(self._proxy_cooldowns)
        concurrency_limit = min(num_resources, max_concurrent_requests)
        self._semaphore = asyncio.Semaphore(concurrency_limit)

        self._session: aiohttp.ClientSession | None = None

    async def start_session(self) -> None:
        """Create and initialize the aiohttp.ClientSession."""
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={"User-Agent": self._user_agent}
            )
            logger.debug("aiohttp.ClientSession started.")

    async def close_session(self) -> None:
        """Close the aiohttp.ClientSession if it is open."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
            logger.debug("aiohttp.ClientSession closed.")

    async def _get_available_proxy(self) -> str | None:
        """Select a proxy that is not on cooldown or marked as dead.

        Returns:
            The URL of an available proxy, or None if not using proxies.

        Raises:
            NetworkError: If all available proxies are marked as dead.

        """
        async with self._proxy_lock:
            while True:
                now = time.monotonic()

                available_proxies = [
                    p
                    for p, last_used in self._proxy_cooldowns.items()
                    if p not in self._dead_proxies
                    and (now - last_used) >= self._request_delay
                ]

                if available_proxies:
                    selected_proxy = random.choice(available_proxies)
                    self._proxy_cooldowns[selected_proxy] = now
                    return selected_proxy

                # Check if all proxies (even those on cooldown) are dead
                if len(self._dead_proxies) == len(self._proxy_cooldowns):
                    raise NetworkError("All available proxies have failed.")

                # If no proxies are available right now, wait and retry
                logger.debug("All live proxies are on cooldown, waiting to select one.")
                await asyncio.sleep(0.5)

    async def get(self, url: str) -> str:
        """Perform an asynchronous GET request for the given URL.

        Args:
            url: The URL to fetch.

        Returns:
            The text content of the HTTP response.

        Raises:
            SessionNotStartedError: If the network session is not active.
            NetworkError: If the request fails after all retries.
            ArtistNotFoundError: If a 404 status is received.

        """
        if not self._session:
            raise SessionNotStartedError("Network session not started.")

        async with self._semaphore:
            proxy_url = await self._get_available_proxy()
            logger.debug(
                "Requesting URL: %s via proxy: %s", url, proxy_url or "local IP"
            )

            try:
                # No proxy or an HTTP/HTTPS proxy. Use the main session.
                if not proxy_url or proxy_url.startswith("http"):
                    async with self._session.get(
                        url, proxy=proxy_url, timeout=20
                    ) as response:
                        response.raise_for_status()
                        return await response.text()

                # A new session with a SOCKS connector is required.
                else:
                    connector = ProxyConnector.from_url(proxy_url)
                    async with (
                        aiohttp.ClientSession(
                            connector=connector, headers=self._session.headers
                        ) as temp_session,
                        temp_session.get(url, timeout=20) as response,
                    ):
                        response.raise_for_status()
                        return await response.text()

            except aiohttp.ClientError as e:
                if proxy_url:
                    logger.warning(
                        "Proxy %s failed for URL %s. Marking as dead.", proxy_url, url
                    )
                    self._dead_proxies.add(proxy_url)

                status = getattr(e, "status", None)
                if status == HTTP_STATUS_NOT_FOUND:
                    raise ArtistNotFoundError(f"Artist not found at URL: {url}") from e

                raise NetworkError(
                    f"Network request to {url} failed: {e}", status=status
                ) from e
