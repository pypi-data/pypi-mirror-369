"""This example can be run safely as it won't change anything in your box configuration."""

import asyncio
import logging

from addressesfrpy import AddressFr
from addressesfrpy.exceptions import AddressFrException

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


async def async_main() -> None:
    """Instantiate class."""
    api = AddressFr()

    try:
        addresses = await api.async_search("Chemiré", limit=5)
        for address in addresses:
            logger.info("==> Found address: %s", address["properties"]["label"])
            logger.info("==> Coordinates: %s", address["geometry"]["coordinates"])
    except AddressFrException as err:
        logger.error(err)
        return

    try:
        addresses = await api.async_search("Par", limit=10)
        for address in addresses:
            logger.info("==> Found address: %s", address["properties"]["label"])
            logger.info("==> Coordinates: %s", address["geometry"]["coordinates"])
    except AddressFrException as err:
        logger.error(err)
        return

    # Reverse geocoding example https://geo.api.gouv.fr/communes?lon=2.4764814791668925&lat=47.059424367067635
    try:
        addresses = await api.async_reverse(2.4764814791668925, 47.059424367067635)
        for address in addresses:
            logger.info("==> Found address: %s", address["properties"]["label"])
            logger.info("==> Coordinates: %s", address["geometry"]["coordinates"])
    except AddressFrException as err:
        logger.error(err)
        return

    await api.async_close()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.run(async_main())
