"""Sensor platform for Geocaching Plus."""

from geocachingapi.const import MEMBERSHIP_LEVELS

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import GeocachingPlusConfigEntry
from .entity import GeocachingPlusEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GeocachingPlusConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Geocaching Plus sensors."""
    coordinator = entry.runtime_data

    async_add_entities(
        [
            GeocachingPlusMembershipLevelSensor(coordinator),
            GeocachingPlusLatestLogSensor(coordinator),
            GeocachingPlusRecentLogsSensor(coordinator),
        ]
    )


class GeocachingPlusMembershipLevelSensor(
    GeocachingPlusEntity,
    SensorEntity,
):
    """Geocaching membership level sensor."""

    _attr_name = "Membership level"
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

    _attr_name = "Latest log"
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

    _attr_name = "Recent logs"
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
