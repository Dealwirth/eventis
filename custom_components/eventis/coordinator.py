"""DataUpdateCoordinator for Eventis using Open Data."""

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
    """Class to manage fetching event data from Open Data REST API."""

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
        """Fetch events from public Open Data API."""
        # Öffentlicher Open Data Endpunkt (ohne API-Key, Schema.org compliant)
        url = "https://opendata.germany.travel/api/v1/events"
        
        params = {
            "lat": self.latitude,
            "lon": self.longitude,
            "distance": self.radius,
            "format": "json"
        }

        session = async_get_clientsession(self.hass)

        try:
            async with session.get(url, params=params, timeout=15) as resp:
                if resp.status != 200:
                    _LOGGER.warning("Open Data API returned status %s.", resp.status)
                    return []

                data = await resp.json()
                # Falls API ein Listen-Format oder 'data'-Wrapper nutzt:
                raw_items = data if isinstance(data, list) else data.get("data", [])
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
            
            # Standort-Parsing aus Schema.org Open Data
            location_data = item.get("location", {})
            locality = ""
            if isinstance(location_data, dict):
                address = location_data.get("address", {})
                locality = address.get("addressLocality") or address.get("city") or location_data.get("name", "")
            elif isinstance(location_data, str):
                locality = location_data

            title_lower = f"{title} {desc}".lower()

            # Kategorie-Abgleich
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
