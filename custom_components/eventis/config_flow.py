"""Config flow for Eventis Integration (AllEvents API)."""

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

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


class EventisConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Eventis."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title="Eventis Local Radar", data=user_input)

        default_lat = self.hass.config.latitude
        default_lon = self.hass.config.longitude

        data_schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): cv.string,
                vol.Required(CONF_LATITUDE, default=default_lat): cv.latitude,
                vol.Required(CONF_LONGITUDE, default=default_lon): cv.longitude,
                vol.Required(CONF_RADIUS, default=DEFAULT_RADIUS): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=100)
                ),
                vol.Optional(
                    CONF_CATEGORIES, default=list(EVENT_CATEGORIES.keys())
                ): cv.multi_select(EVENT_CATEGORIES),
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return EventisOptionsFlowHandler(config_entry)


class EventisOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Eventis."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_config = {**self.config_entry.data, **self.config_entry.options}

        options_schema = vol.Schema(
            {
                vol.Required(
                    CONF_RADIUS,
                    default=current_config.get(CONF_RADIUS, DEFAULT_RADIUS),
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=100)),
                vol.Optional(
                    CONF_CATEGORIES,
                    default=current_config.get(
                        CONF_CATEGORIES, list(EVENT_CATEGORIES.keys())
                    ),
                ): cv.multi_select(EVENT_CATEGORIES),
            }
        )

        return self.async_show_form(step_id="init", data_schema=options_schema)
