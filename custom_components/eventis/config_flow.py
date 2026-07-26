"""Config flow for Local Event Radar integration."""

import voluptuous as vol
from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
from homeassistant.core import callback

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_RADIUS,
    CONF_CATEGORIES,
    DEFAULT_RADIUS,
    EVENT_CATEGORIES,
)


class LocalEventsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Local Event Radar."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial setup step."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title=f"Events ({user_input[CONF_RADIUS]} km)", data=user_input
            )

        # Default coordinates from Home Assistant system location
        default_lat = self.hass.config.latitude
        default_lon = self.hass.config.longitude

        schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): str,
                vol.Required(CONF_LATITUDE, default=default_lat): float,
                vol.Required(CONF_LONGITUDE, default=default_lon): float,
                vol.Required(CONF_RADIUS, default=DEFAULT_RADIUS): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=200)
                ),
                vol.Required(
                    CONF_CATEGORIES, default=list(EVENT_CATEGORIES.keys())
                ): cv.multi_select(EVENT_CATEGORIES),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for reconfiguring settings later."""
        return LocalEventsOptionsFlowHandler(config_entry)


class LocalEventsOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options re-configuration."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_data = {**self.config_entry.data, **self.config_entry.options}

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_RADIUS, default=current_data.get(CONF_RADIUS, DEFAULT_RADIUS)
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=200)),
                vol.Required(
                    CONF_CATEGORIES,
                    default=current_data.get(
                        CONF_CATEGORIES, list(EVENT_CATEGORIES.keys())
                    ),
                ): cv.multi_select(EVENT_CATEGORIES),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
