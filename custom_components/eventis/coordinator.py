"""DataUpdateCoordinator for Eventis using Free Open Data."""

from datetime import datetime, timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
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
    """Class to manage fetching event data without API keys."""

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
        """Fetch events from a public Open Data API."""
        # Öffentliches Open-Data API-Endpunkt für Regionen (Open-Events-Standard)
        url = "https://api.open-data-events.de/v1/events"
        
        headers = {
            "User-Agent": "HomeAssistant-Eventis/1.0 (Home Assistant Custom Integration)"
        }
        
        params = {
            "lat": self.latitude,
            "lon": self.longitude,
            "radius": self.radius,
        }

        session = async_get_clientsession(self.hass)

        try:
            async with session.get(url, headers=headers, params=params, timeout=15) as resp:
                if resp.status != 200:
                    _LOGGER.warning("Open Data API lieferte Status %s zurück.", resp.status)
                    # Falls der externe Server nicht erreichbar ist, leere Liste statt Fehler zurückgeben
                    return []

                data = await resp.json()
                raw_items = data.get("events", []) if isinstance(data, dict) else []
                return self._filter_and_format_events(raw_items)

        except Exception as err:
            _LOGGER.error("Fehler beim Abrufen der Open-Data-Events: %s", err)
            # Fängt Fehler ab, damit der Start von Home Assistant nicht blockiert wird
            return []

    def _filter_and_format_events(self, raw_items):
        """Filter events according to selected categories and format structure."""
        processed_events = []

        for item in raw_items:
            title = item.get("title") or item.get("name", "Veranstaltung")
            desc = item.get("description", "")
            start_str = item.get("start_date") or item.get("startDate")
            end_str = item.get("end_date") or item.get("endDate") or start_str
            locality = item.get("location_name") or item.get("city", "")

            title_lower = f"{title} {desc}".lower()

            matched_cat = False
            if "wine" in self.categories and any(k in title_lower for k in ["wein", "wine"]):
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
