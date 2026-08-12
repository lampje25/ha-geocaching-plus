"""Base entities for Geocaching Plus."""

from typing import Any

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import (
    GeocachingPlusDataUpdateCoordinator,
    GeocachingPlusOwnedCacheData,
)


class GeocachingPlusEntity(CoordinatorEntity[GeocachingPlusDataUpdateCoordinator]):
    """Base entity for Geocaching Plus."""


class GeocachingPlusOwnedCacheEntity(GeocachingPlusEntity):
    """Base entity for an owned geocache."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: GeocachingPlusDataUpdateCoordinator,
        cache_code: str,
    ) -> None:
        """Initialize an owned geocache entity."""
        super().__init__(coordinator)
        self.cache_code = cache_code

    @property
    def owned_cache_data(self) -> GeocachingPlusOwnedCacheData | None:
        """Return current data for this owned geocache."""
        return next(
            (
                owned_cache
                for owned_cache in self.coordinator.data.owned_caches
                if owned_cache.cache.get("referenceCode") == self.cache_code
            ),
            None,
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information for this owned geocache."""
        owned_cache = self.owned_cache_data
        cache: dict[str, Any] = owned_cache.cache if owned_cache else {}

        return DeviceInfo(
            identifiers={(DOMAIN, self.cache_code)},
            name=cache.get("name") or self.cache_code,
            manufacturer="Geocaching",
            model="Owned geocache",
        )
