"""Sensor platform for Geocaching Plus."""

from geocachingapi.const import MEMBERSHIP_LEVELS
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .coordinator import GeocachingPlusConfigEntry
from .entity import GeocachingPlusEntity, GeocachingPlusOwnedCacheEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GeocachingPlusConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Geocaching Plus sensors."""
    coordinator = entry.runtime_data

    entities = [
        GeocachingPlusMembershipLevelSensor(coordinator),
        GeocachingPlusLatestLogSensor(coordinator),
        GeocachingPlusRecentLogsSensor(coordinator),
    ]

    for owned_cache in coordinator.data.owned_caches:
        cache_code = owned_cache.cache.get("referenceCode")
        if not cache_code:
            continue

        entities.extend(
            [
                GeocachingPlusOwnedCacheStatusSensor(coordinator, cache_code),
                GeocachingPlusOwnedCacheLatestLogSensor(coordinator, cache_code),
            ]
        )

    async_add_entities(entities)


class GeocachingPlusMembershipLevelSensor(
    GeocachingPlusEntity,
    SensorEntity,
):
    """Geocaching membership level sensor."""

    _attr_translation_key = "membership_level"
    _attr_unique_id = "geocaching_plus_membership_level"

    @property
    def native_value(self):
        """Return the membership level."""
        user = self.coordinator.data.status.user

        if user is None:
            return None

        return MEMBERSHIP_LEVELS.get(user.membership_level_id, "Unknown")


class GeocachingPlusLatestLogSensor(
    GeocachingPlusEntity,
    SensorEntity,
):
    """Latest Geocaching log sensor."""

    _attr_translation_key = "latest_log"
    _attr_unique_id = "geocaching_plus_latest_log"

    @property
    def native_value(self):
        """Return the latest logged cache name."""
        recent_logs = self.coordinator.data.recent_logs

        if not recent_logs:
            return None

        return recent_logs[0].get("geocacheName")

    @property
    def extra_state_attributes(self):
        """Return details of the latest Geocaching log."""
        recent_logs = self.coordinator.data.recent_logs

        if not recent_logs:
            return {}

        latest_log = recent_logs[0]
        log_type = latest_log.get("geocacheLogType") or {}

        return {
            "geocache_code": latest_log.get("geocacheCode"),
            "log_type": log_type.get("name"),
            "logged_date": latest_log.get("loggedDate"),
            "used_favorite_point": latest_log.get("usedFavoritePoint"),
            "log_reference_code": latest_log.get("referenceCode"),
        }


class GeocachingPlusRecentLogsSensor(
    GeocachingPlusEntity,
    SensorEntity,
):
    """Recent Geocaching logs sensor."""

    _attr_translation_key = "recent_logs"
    _attr_unique_id = "geocaching_plus_recent_logs"

    @property
    def native_value(self):
        """Return the number of recent logs."""
        return len(self.coordinator.data.recent_logs)

    @property
    def extra_state_attributes(self):
        """Return the recent Geocaching logs."""
        logs = []

        for log in self.coordinator.data.recent_logs:
            log_type = log.get("geocacheLogType") or {}

            logs.append(
                {
                    "geocache_code": log.get("geocacheCode"),
                    "geocache_name": log.get("geocacheName"),
                    "log_type": log_type.get("name"),
                    "logged_date": log.get("loggedDate"),
                    "used_favorite_point": log.get("usedFavoritePoint"),
                    "log_reference_code": log.get("referenceCode"),
                }
            )

        return {"logs": logs}


class GeocachingPlusOwnedCacheStatusSensor(
    GeocachingPlusOwnedCacheEntity,
    SensorEntity,
):
    """Status sensor for an owned geocache."""

    _attr_translation_key = "owned_cache_status"

    def __init__(self, coordinator, cache_code: str) -> None:
        """Initialize the owned geocache status sensor."""
        super().__init__(coordinator, cache_code)
        self._attr_unique_id = f"{DOMAIN}_{cache_code.lower()}_status"

    @property
    def native_value(self):
        """Return the owned geocache status."""
        owned_cache = self.owned_cache_data
        if owned_cache is None:
            return None

        return owned_cache.cache.get("status")

    @property
    def extra_state_attributes(self):
        """Return owned geocache details."""
        owned_cache = self.owned_cache_data
        if owned_cache is None:
            return {}

        cache = owned_cache.cache
        return {
            "geocache_code": self.cache_code,
            "find_count": cache.get("findCount"),
            "favorite_points": cache.get("favoritePoints"),
            "last_visited_date": cache.get("lastVisitedDate"),
            "owner": cache.get("ownerAlias"),
        }


class GeocachingPlusOwnedCacheLatestLogSensor(
    GeocachingPlusOwnedCacheEntity,
    SensorEntity,
):
    """Latest log sensor for an owned geocache."""

    _attr_translation_key = "owned_cache_latest_log"

    def __init__(self, coordinator, cache_code: str) -> None:
        """Initialize the owned geocache latest log sensor."""
        super().__init__(coordinator, cache_code)
        self._attr_unique_id = f"{DOMAIN}_{cache_code.lower()}_latest_log"

    @property
    def native_value(self):
        """Return the latest log type."""
        latest_log = self._latest_log
        if latest_log is None:
            return None

        log_type = latest_log.get("geocacheLogType") or {}
        return log_type.get("name")

    @property
    def extra_state_attributes(self):
        """Return details of the latest log."""
        latest_log = self._latest_log
        if latest_log is None:
            return {}

        log_type = latest_log.get("geocacheLogType") or {}
        owner = latest_log.get("owner") or {}

        return {
            "geocache_code": self.cache_code,
            "logger": owner.get("username"),
            "log_type": log_type.get("name"),
            "log_type_id": log_type.get("id"),
            "logged_date": latest_log.get("loggedDate"),
            "text": latest_log.get("text"),
            "image_count": latest_log.get("imageCount"),
            "used_favorite_point": latest_log.get("usedFavoritePoint"),
            "log_reference_code": latest_log.get("referenceCode"),
            "url": latest_log.get("url"),
        }

    @property
    def _latest_log(self):
        """Return the latest log."""
        owned_cache = self.owned_cache_data
        if owned_cache is None or not owned_cache.logs:
            return None

        return owned_cache.logs[0]
