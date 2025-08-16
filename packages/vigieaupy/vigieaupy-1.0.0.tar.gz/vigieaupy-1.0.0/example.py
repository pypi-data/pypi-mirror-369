"""This example can be run safely as it won't change anything in your box configuration."""

import asyncio
import logging

from vigieaupy import VigiEau
from vigieaupy.exceptions import VigiEauException

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


async def async_main() -> None:
    """Instantiate class."""
    api = VigiEau()

    try:
        data = await api.async_get_data(longitude=5.405, latitude=43.282, city_id=13055)
        for item in data:
            logger.info("Found: %s", item)
    except VigiEauException as err:
        logger.error(err)
        return

    await api.async_close()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.run(async_main())
