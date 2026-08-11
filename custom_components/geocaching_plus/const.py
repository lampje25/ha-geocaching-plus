"""Constants for the Geocaching Plus integration."""

from datetime import timedelta
import logging
from typing import Final

from geocachingapi.models import GeocachingApiEnvironment


DOMAIN: Final = "geocaching_plus"

LOGGER = logging.getLogger(__package__)

UPDATE_INTERVAL = timedelta(hours=1)

ENVIRONMENT = GeocachingApiEnvironment.Production
CONF_RECENT_LOGS_COUNT = "recent_logs_count"

DEFAULT_RECENT_LOGS_COUNT = 10
