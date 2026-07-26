"""The Eventis Integration."""

import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.frontend import add_extra_js_url

from .const import DOMAIN
from .coordinator import LocalEventsCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["calendar", "sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Eventis from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    config_data = {**entry.data, **entry.options}

    coordinator = LocalEventsCoordinator(hass, config_data)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register Custom Lovelace Dashboard Card automatically
    url_path = "/eventis/local-events-card.js"
    hass.http.register_static_path(
        url_path,
        hass.config.path("custom_components/eventis/www/local-events-card.js"),
        cache_headers=True,
    )
    add_extra_js_url(hass, url_path)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
