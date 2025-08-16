"""API for querying French addresses using the address fr."""

import logging
from typing import Any

from .auth import HTTPRequest, HttpRequestError
from .consts import SEARCH_ADDRESS
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
                path=SEARCH_ADDRESS,
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

    async def async_close(self) -> None:
        """Close the HTTP session."""
        await super().async_close()
