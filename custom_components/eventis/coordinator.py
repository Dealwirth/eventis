"""DataUpdateCoordinator for Eventis using Public Open Data."""

from datetime import datetime, timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_RADIUS,
    CONF_CATEGORIES,
    DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class LocalEventsCoordinator(DataUpdateCoordinator):
    """Class to manage fetching event data from public Open Data API."""

    def __init__(self, hass: HomeAssistant, entry_data: dict):
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.latitude = entry_data.get(CONF_LATITUDE)
        self.longitude = entry_data.get(CONF_LONGITUDE)
        self.radius = entry_data.get(CONF_RADIUS)
        self.categories = entry_data.get(CONF_CATEGORIES, [])

    async def _async_update_data(self):
        """Fetch events from public REST endpoint."""
        # Öffentlicher Open Data Endpunkt ohne Auth-Redirect
        url = "https://data.bayerncloud.digital/api/v4/endpoints/list_current_events"
        
        headers = {
            "Accept": "application/json",
            "User-Agent": "HomeAssistant-Eventis/1.0"
        }
        
        params = {
            "lat": self.latitude,
            "lon": self.longitude,
            "radius": self.radius,
        }

        session = async_get_clientsession(self.hass)

        try:
            async with session.get(url, headers=headers, params=params, timeout=15) as resp:
                # Prüfen, ob wir HTML statt JSON zurückbekommen (z.B. Redirects)
                content_type = resp.headers.get("Content-Type", "")
                if "application/json" not in content_type:
                    _LOGGER.warning(
                        "API gab keinen JSON-Inhalt zurück (Content-Type: %s).", content_type
                    )
                    return []

                if resp.status != 200:
                    _LOGGER.warning("API returned status %s.", resp.status)
                    return []

                data = await resp.json()
                raw_items = data.get("items", []) if isinstance(data, dict) else []
                return self._filter_and_format_events(raw_items)

        except Exception as err:
            _LOGGER.error("Error fetching Open Data events: %s", err)
            return []

    def _filter_and_format_events(self, raw_items):
        """Filter events according to selected categories and format structure."""
        processed_events = []

        for item in raw_items:
            title = item.get("name") or item.get("title", "Unbekanntes Event")
            desc = item.get("description", "")
            start_str = item.get("startDate") or item.get("start_date")
            end_str = item.get("endDate") or item.get("end_date") or start_str
            
            location_data = item.get("location", {})
            locality = ""
            if isinstance(location_data, dict):
                address = location_data.get("address", {})
                locality = address.get("addressLocality") or address.get("city") or location_data.get("name", "")

            title_lower = f"{title} {desc}".lower()

            matched_cat = False
            if "wine" in self.categories and ("wein" in title_lower or "wine" in title_lower):
                matched_cat = True
            elif "kirchweih" in self.categories and any(k in title_lower for k in ["kerwa", "kirchweih", "kirmes", "volksfest"]):
                matched_cat = True
            elif "concert" in self.categories and any(k in title_lower for k in ["konzert", "musik", "live"]):
                matched_cat = True
            elif "market" in self.categories and any(k in title_lower for k in ["markt", "messe"]):
                matched_cat = True
            elif not self.categories:
                matched_cat = True
            else:
                matched_cat = True

            if matched_cat and start_str:
                processed_events.append(
                    {
                        "summary": title,
                        "description": desc,
                        "start": start_str,
                        "end": end_str,
                        "location": locality,
                    }
                )

        return processed_events
