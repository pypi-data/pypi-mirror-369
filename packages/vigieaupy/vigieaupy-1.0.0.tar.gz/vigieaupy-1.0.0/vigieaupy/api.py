"""API for querying data using the VigiEau fr."""

import logging
from typing import Any

from .auth import HTTPRequest, HttpRequestError
from .consts import API_BASE_URL
from .exceptions import VigiEauException

_LOGGER = logging.getLogger(__name__)


class VigiEau(HTTPRequest):
    """Class to handle VigiEau information."""

    async def async_get_data(
        self, longitude: float, latitude: float, city_id: int
    ) -> list[dict[str, Any]]:
        """Make a request to the VigiEau API."""
        try:
            return await self.async_request(
                path=API_BASE_URL,
                params={
                    "lon": longitude,
                    "lat": latitude,
                    "city_id": city_id,
                },
            )
        except HttpRequestError as error:
            _LOGGER.error("Failed to fetch data from VigiEau: %s", error)
            raise VigiEauException("Error fetching data from VigiEau.") from error

    async def async_close(self) -> None:
        """Close the HTTP session."""
        await super().async_close()
