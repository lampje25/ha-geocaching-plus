"""Data update coordinator for Geocaching Plus."""

from dataclasses import dataclass
from typing import Any, override
from urllib.parse import quote

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
    EVENT_NEW_OWNED_CACHE_LOG,
    LOGGER,
    UPDATE_INTERVAL,
)

type GeocachingPlusConfigEntry = ConfigEntry["GeocachingPlusDataUpdateCoordinator"]


@dataclass
class GeocachingPlusOwnedCacheData:
    """Data for one owned geocache."""

    cache: dict[str, Any]
    logs: list[dict[str, Any]]
    maintenance_required: bool


@dataclass
class GeocachingPlusData:
    """Data provided by the Geocaching Plus coordinator."""

    status: GeocachingStatus
    recent_logs: list[dict[str, Any]]
    owned_caches: list[GeocachingPlusOwnedCacheData]


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

    def _fire_new_owned_cache_log_events(
        self,
        owned_caches: list[GeocachingPlusOwnedCacheData],
    ) -> None:
        """Fire events for newly received logs on owned geocaches."""
        if self.data is None:
            return

        previous_caches = {
            owned_cache.cache.get("referenceCode"): owned_cache
            for owned_cache in self.data.owned_caches
            if owned_cache.cache.get("referenceCode")
        }

        for owned_cache in owned_caches:
            cache = owned_cache.cache
            cache_code = cache.get("referenceCode")
            if not cache_code or cache_code not in previous_caches:
                continue

            previous_log_codes = {
                log.get("referenceCode")
                for log in previous_caches[cache_code].logs
                if log.get("referenceCode")
            }
            new_logs = [
                log
                for log in owned_cache.logs
                if log.get("referenceCode")
                and log.get("referenceCode") not in previous_log_codes
            ]

            for log in reversed(new_logs):
                log_type = log.get("geocacheLogType") or {}
                owner = log.get("owner") or {}

                self.hass.bus.async_fire(
                    EVENT_NEW_OWNED_CACHE_LOG,
                    {
                        "cache_code": cache_code,
                        "cache_name": cache.get("name"),
                        "log_reference_code": log.get("referenceCode"),
                        "log_type": log_type.get("name"),
                        "log_type_id": log_type.get("id"),
                        "logger": owner.get("username"),
                        "logged_date": log.get("loggedDate"),
                        "text": log.get("text"),
                        "image_count": log.get("imageCount"),
                        "used_favorite_point": log.get("usedFavoritePoint"),
                        "url": log.get("url"),
                        "maintenance_required": owned_cache.maintenance_required,
                    },
                )

    @override
    async def _async_update_data(self) -> GeocachingPlusData:
        """Fetch Geocaching Plus data."""
        try:
            status = await self.geocaching.update()
            username = status.user.username
            if not username:
                raise UpdateFailed(
                    "Geocaching API returned no username for the authenticated user"
                )

            encoded_username = quote(username, safe="")
            owned_cache_results = await self.geocaching._request(
                "GET",
                (
                    "/geocaches/search"
                    f"?q=hiddenBy:{encoded_username}"
                    "&lite=true"
                    "&take=100"
                    "&fields=referenceCode,name,status,findCount,"
                    "favoritePoints,lastVisitedDate,ownerCode,ownerAlias"
                ),
            )

            LOGGER.debug(
                "Found %s owned geocaches for %s",
                len(owned_cache_results),
                username,
            )

            owned_caches: list[GeocachingPlusOwnedCacheData] = []

            for cache in owned_cache_results:
                cache_code = cache.get("referenceCode")
                if not cache_code:
                    continue

                LOGGER.debug(
                    "Owned geocache: %s - %s - %s",
                    cache_code,
                    cache.get("name"),
                    cache.get("status"),
                )

                cache_logs = await self.geocaching._request(
                    "GET",
                    (
                        f"/geocaches/{cache_code}/geocachelogs"
                        "?take=50"
                        "&sort=newest"
                        "&fields=referenceCode,owner,loggedDate,text,"
                        "geocacheLogType,imageCount,usedFavoritePoint,url"
                    ),
                )

                latest_log = cache_logs[0] if cache_logs else None
                maintenance_logs = [
                    log
                    for log in cache_logs
                    if log.get("geocacheLogType", {}).get("id") in (45, 46)
                ]
                maintenance_required = bool(
                    maintenance_logs
                    and maintenance_logs[0].get("geocacheLogType", {}).get("id") == 45
                )
                owned_caches.append(
                    GeocachingPlusOwnedCacheData(
                        cache=cache,
                        logs=cache_logs,
                        maintenance_required=maintenance_required,
                    )
                )

                if latest_log:
                    LOGGER.debug(
                        "Latest log for %s: %s by %s on %s; maintenance required: %s",
                        cache_code,
                        latest_log.get("geocacheLogType", {}).get("name"),
                        latest_log.get("owner", {}).get("username"),
                        latest_log.get("loggedDate"),
                        maintenance_required,
                    )
                else:
                    LOGGER.debug(
                        "No logs found for owned geocache %s",
                        cache_code,
                    )

            recent_logs = await self.geocaching._request(
                "GET",
                (
                    "/users/me/geocachelogs"
                    f"?take={self.recent_logs_count}"
                    "&fields=referenceCode,geocacheCode,geocacheName,"
                    "loggedDate,geocacheLogType,usedFavoritePoint"
                ),
            )

            self._fire_new_owned_cache_log_events(owned_caches)

            return GeocachingPlusData(
                status=status,
                recent_logs=recent_logs,
                owned_caches=owned_caches,
            )

        except GeocachingInvalidSettingsError as error:
            raise UpdateFailed(
                f"Invalid Geocaching Plus configuration: {error}"
            ) from error
        except GeocachingApiError as error:
            raise UpdateFailed(
                f"Error communicating with Geocaching API: {error}"
            ) from error
