"""Binary sensor platform for Geocaching Plus."""

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .coordinator import GeocachingPlusConfigEntry
from .entity import GeocachingPlusOwnedCacheEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GeocachingPlusConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Geocaching Plus binary sensors."""
    coordinator = entry.runtime_data
    entities = []

    for owned_cache in coordinator.data.owned_caches:
        cache_code = owned_cache.cache.get("referenceCode")
        if not cache_code:
            continue

        entities.append(
            GeocachingPlusOwnedCacheMaintenanceSensor(
                coordinator,
                cache_code,
            )
        )

    async_add_entities(entities)


class GeocachingPlusOwnedCacheMaintenanceSensor(
    GeocachingPlusOwnedCacheEntity,
    BinarySensorEntity,
):
    """Maintenance sensor for an owned geocache."""

    _attr_translation_key = "maintenance_required"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator, cache_code: str) -> None:
        """Initialize the owned geocache maintenance sensor."""
        super().__init__(coordinator, cache_code)
        self._attr_unique_id = f"{DOMAIN}_{cache_code.lower()}_maintenance_required"

    @property
    def is_on(self) -> bool | None:
        """Return whether maintenance is required."""
        owned_cache = self.owned_cache_data
        if owned_cache is None:
            return None

        return owned_cache.maintenance_required
