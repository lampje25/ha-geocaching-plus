"""Base entities for Geocaching Plus."""

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import GeocachingPlusDataUpdateCoordinator


class GeocachingPlusEntity(CoordinatorEntity[GeocachingPlusDataUpdateCoordinator]):
    """Base entity for Geocaching Plus."""
