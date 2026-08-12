"""The Geocaching Plus integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.config_entry_oauth2_flow import (
    OAuth2Session,
    async_get_config_entry_implementation,
)

from .coordinator import (
    GeocachingPlusConfigEntry,
    GeocachingPlusDataUpdateCoordinator,
)

PLATFORMS = [Platform.BINARY_SENSOR, Platform.SENSOR]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GeocachingPlusConfigEntry,
) -> bool:
    """Set up Geocaching Plus from a config entry."""
    geocaching_entries = hass.config_entries.async_entries("geocaching")

    if not geocaching_entries:
        return False

    official_entry = geocaching_entries[0]

    implementation = await async_get_config_entry_implementation(
        hass,
        official_entry,
    )

    oauth_session = OAuth2Session(
        hass,
        official_entry,
        implementation,
    )

    coordinator = GeocachingPlusDataUpdateCoordinator(
        hass,
        entry=entry,
        session=oauth_session,
    )

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload a Geocaching Plus config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
