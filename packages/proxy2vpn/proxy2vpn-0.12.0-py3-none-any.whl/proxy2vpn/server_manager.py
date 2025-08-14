"""Utilities for fetching and caching VPN server lists."""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List
from urllib.parse import urlparse

from . import config
from .http_client import HTTPClient, HTTPClientConfig, HTTPClientError, RetryPolicy
from .utils import abort


class ServerManager:
    """Manage gluetun server list information.

    The server list is downloaded from GitHub and cached locally to avoid
    repeated network requests. The cache is considered valid for ``ttl``
    seconds (24h by default).
    """

    def __init__(self, cache_dir: Path | None = None, ttl: int = 24 * 3600) -> None:
        self.cache_dir = cache_dir or config.CACHE_DIR
        self.cache_file = self.cache_dir / "servers.json"
        self.ttl = ttl
        self.data: Dict[str, Dict] | None = None

    # ------------------------------------------------------------------
    # Fetching and caching
    # ------------------------------------------------------------------

    def _is_cache_valid(self) -> bool:
        if not self.cache_file.exists():
            return False
        age = time.time() - self.cache_file.stat().st_mtime
        return age < self.ttl

    async def _download_servers(self, verify: bool) -> Dict[str, Dict]:
        parsed = urlparse(config.SERVER_LIST_URL)
        cfg = HTTPClientConfig(
            base_url=f"{parsed.scheme}://{parsed.netloc}",
            timeout=config.DEFAULT_TIMEOUT,
            verify_ssl=verify,
            retry=RetryPolicy(attempts=config.MAX_RETRIES),
        )
        async with HTTPClient(cfg) as client:
            return await client.get(parsed.path)

    async def _fetch_and_cache(self, verify: bool) -> None:
        data = await self._download_servers(verify)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file.write_text(json.dumps(data), encoding="utf-8")

    def update_servers(self, verify: bool = True) -> Dict[str, Dict]:
        """Fetch the server list, using the cache when possible."""

        if not self._is_cache_valid():
            try:
                asyncio.run(self._fetch_and_cache(verify))
            except HTTPClientError as exc:
                abort("Failed to download server list", str(exc))
        with self.cache_file.open("r", encoding="utf-8") as f:
            self.data = json.load(f)
        return self.data

    async def fetch_server_list_async(self, verify: bool = True) -> Dict[str, Dict]:
        """Fetch and cache the VPN server list asynchronously."""

        if not self._is_cache_valid():
            try:
                await self._fetch_and_cache(verify)
            except HTTPClientError as exc:
                abort("Failed to download server list", str(exc))
        with self.cache_file.open("r", encoding="utf-8") as f:
            self.data = json.load(f)
        return self.data

    # ------------------------------------------------------------------
    # Listing helpers
    # ------------------------------------------------------------------

    def list_providers(self) -> List[str]:
        data = self.data or self.update_servers()
        return sorted(k for k in data.keys() if k != "version")

    def list_countries(self, provider: str) -> List[str]:
        """Return available countries for PROVIDER."""

        data = self.data or self.update_servers()
        prov = data.get(provider, {})
        servers = prov.get("servers", [])
        countries = {srv.get("country") for srv in servers if srv.get("country")}
        return sorted(countries)

    def list_cities(self, provider: str, country: str) -> List[str]:
        """Return available cities for PROVIDER in COUNTRY."""

        data = self.data or self.update_servers()
        prov = data.get(provider, {})
        servers = prov.get("servers", [])
        cities = {
            srv.get("city")
            for srv in servers
            if srv.get("country") == country and srv.get("city")
        }
        return sorted(cities)

    def validate_location(self, provider: str, location: str) -> bool:
        """Return ``True`` if LOCATION exists for PROVIDER."""

        data = self.data or self.update_servers()
        prov = data.get(provider, {})
        servers = prov.get("servers", [])
        loc = location.lower()
        for srv in servers:
            if (
                srv.get("city", "").lower() == loc
                or srv.get("country", "").lower() == loc
            ):
                return True
        return False
