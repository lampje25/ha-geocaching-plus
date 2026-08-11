"""Config flow for Geocaching Plus."""

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.core import callback

from .const import (
    CONF_RECENT_LOGS_COUNT,
    DEFAULT_RECENT_LOGS_COUNT,
    DOMAIN,
)


class GeocachingPlusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Geocaching Plus."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlowWithReload:
        """Create the options flow."""
        return GeocachingPlusOptionsFlow()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        official_entries = self.hass.config_entries.async_entries("geocaching")

        if not official_entries:
            return self.async_abort(reason="geocaching_not_configured")

        if user_input is not None:
            await self.async_set_unique_id("geocaching_plus")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title="Geocaching Plus",
                data={},
            )

        return self.async_show_form(step_id="user")


class GeocachingPlusOptionsFlow(OptionsFlowWithReload):
    """Handle Geocaching Plus options."""

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Manage Geocaching Plus options."""
        if user_input is not None:
            count = int(user_input[CONF_RECENT_LOGS_COUNT])

            if count < 1 or count > 50:
                return self.async_show_form(
                    step_id="init",
                    data_schema=vol.Schema(
                        {
                            vol.Optional(
                                CONF_RECENT_LOGS_COUNT,
                                default=count,
                            ): vol.Coerce(int),
                        }
                    ),
                    errors={"base": "invalid_recent_logs_count"},
                )

            return self.async_create_entry(data=user_input)

        current_count = self.config_entry.options.get(
            CONF_RECENT_LOGS_COUNT,
            DEFAULT_RECENT_LOGS_COUNT,
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_RECENT_LOGS_COUNT,
                        default=current_count,
                    ): vol.Coerce(int),
                }
            ),
        )
