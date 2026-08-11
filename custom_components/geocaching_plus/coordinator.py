"""Data update coordinator for Geocaching Plus."""

from dataclasses import dataclass
from typing import Any, override

from geocachingapi.exceptions import (
    GeocachingApiError,
    GeocachingInvalidSettingsError,
)
from geocachingapi.geocachingapi import GeocachingApi
from geocachingapi.models import GeocachingStatus

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.config_entry_oauth2_flow import OAuth2Session
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    CONF_RECENT_LOGS_COUNT,
    DEFAULT_RECENT_LOGS_COUNT,
    DOMAIN,
    ENVIRONMENT,
    LOGGER,
    UPDATE_INTERVAL,
)

type GeocachingPlusConfigEntry = ConfigEntry["GeocachingPlusDataUpdateCoordinator"]


@dataclass
class GeocachingPlusData:
    """Data provided by the Geocaching Plus coordinator."""

    status: GeocachingStatus
    recent_logs: list[dict[str, Any]]


class GeocachingPlusDataUpdateCoordinator(DataUpdateCoordinator[GeocachingPlusData]):
    """Manage fetching Geocaching Plus data."""

    def __init__(
        self,
        hass: HomeAssistant,
        *,
        entry: GeocachingPlusConfigEntry,
        session: OAuth2Session,
    ) -> None:
        """Initialize the Geocaching Plus coordinator."""
        self.session = session

        self.recent_logs_count = entry.options.get(
            CONF_RECENT_LOGS_COUNT,
            DEFAULT_RECENT_LOGS_COUNT,
        )

        async def async_token_refresh() -> str:
            await session.async_ensure_token_valid()
            return str(session.token["access_token"])

        self.geocaching = GeocachingApi(
            environment=ENVIRONMENT,
            token=session.token["access_token"],
            session=async_get_clientsession(hass),
            token_refresh_method=async_token_refresh,
        )

        super().__init__(
            hass,
            LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    @override
    async def _async_update_data(self) -> GeocachingPlusData:
        """Fetch Geocaching Plus data."""
        try:
            status = await self.geocaching.update()

            recent_logs = await self.geocaching._request(
                "GET",
                (
                    "/users/me/geocachelogs"
                    f"?take={self.recent_logs_count}"
                    "&fields=referenceCode,geocacheCode,geocacheName,"
                    "loggedDate,geocacheLogType,usedFavoritePoint"
                ),
            )

            return GeocachingPlusData(
                status=status,
                recent_logs=recent_logs,
            )

        except GeocachingInvalidSettingsError as error:
            raise UpdateFailed(
                f"Invalid Geocaching Plus configuration: {error}"
            ) from error
        except GeocachingApiError as error:
            raise UpdateFailed(
                f"Error communicating with Geocaching API: {error}"
            ) from error
