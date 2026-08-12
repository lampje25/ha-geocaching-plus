"""Constants for the Geocaching Plus integration."""

import logging
from datetime import timedelta
from typing import Final

from geocachingapi.models import GeocachingApiEnvironment

DOMAIN: Final = "geocaching_plus"

LOGGER = logging.getLogger(__package__)

UPDATE_INTERVAL = timedelta(hours=1)

ENVIRONMENT = GeocachingApiEnvironment.Production
CONF_RECENT_LOGS_COUNT = "recent_logs_count"

DEFAULT_RECENT_LOGS_COUNT = 10
EVENT_NEW_OWNED_CACHE_LOG: Final = "geocaching_plus_new_owned_cache_log"
