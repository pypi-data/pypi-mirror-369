"""API for querying French addresses using the address fr."""

import logging
from typing import Any

from addressesfrpy.consts import API_BASE_URL, GEO_BASE_URL

from .auth import HTTPRequest, HttpRequestError
from .exceptions import AddressNotFound

_LOGGER = logging.getLogger(__name__)


class AddressFr(HTTPRequest):
    """Class to handle French addresses."""

    async def async_search(
        self, query: str, limit: int = 10, **kwargs: Any
    ) -> list[dict[str, Any]]:
        """Query the addresses."""
        try:
            addresses = await self.async_request(
                path=API_BASE_URL + "/search",
                params={"q": query, "limit": limit, **kwargs},
            )
        except HttpRequestError as error:
            _LOGGER.error("Failed to query address: %s", error)
            raise AddressNotFound("Address not found.") from error

        if addresses and isinstance(addresses, dict) and "features" in addresses:
            addresses = addresses["features"]
            if not addresses:
                raise AddressNotFound("No addresses found for the given query.")
            return addresses
        raise AddressNotFound("No addresses found for the given query.")

    async def async_reverse(
        self, lon: float, lat: float, **kwargs: Any
    ) -> list[dict[str, Any]]:
        """Reverse geocode a location to find the address."""
        try:
            addresses = await self.async_request(
                path=API_BASE_URL + "/reverse",
                params={"lon": lon, "lat": lat, **kwargs},
            )
            if addresses and isinstance(addresses, dict) and "features" in addresses:
                addresses = addresses["features"]
                if not addresses:
                    addresses = await self.async_request(
                        path=GEO_BASE_URL + "/communes",
                        params={"lon": lon, "lat": lat, **kwargs},
                    )
                    if (name := addresses[0].get("nom")) is None:
                        raise AddressNotFound("No addresses found for the given query.")
                    addresses = await self.async_search(name, limit=1)
                return addresses
            raise AddressNotFound("No addresses found for the given query.")

        except HttpRequestError as error:
            _LOGGER.error("Failed to query address: %s", error)
            raise AddressNotFound("Address not found.") from error

    async def async_close(self) -> None:
        """Close the HTTP session."""
        await super().async_close()
