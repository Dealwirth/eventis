"""DataUpdateCoordinator for Eventis."""

from datetime import datetime, timedelta
import logging
import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_RADIUS,
    CONF_CATEGORIES,
    DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class LocalEventsCoordinator(DataUpdateCoordinator):
    """Class to manage fetching event data from BayernCloud API."""

    def __init__(self, hass: HomeAssistant, entry_data: dict):
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api_key = entry_data.get(CONF_API_KEY)
        self.latitude = entry_data.get(CONF_LATITUDE)
        self.longitude = entry_data.get(CONF_LONGITUDE)
        self.radius = entry_data.get(CONF_RADIUS)
        self.categories = entry_data.get(CONF_CATEGORIES, [])

    async def _async_update_data(self):
        """Fetch events from API."""
        url = "https://data.bayerncloud.digital/api/v4/endpoints/list_current_events"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        params = {
            "lat": self.latitude,
            "lon": self.longitude,
            "radius": self.radius,
        }

        session = async_get_clientsession(self.hass)

        try:
            async with session.get(url, headers=headers, params=params, timeout=15) as resp:
                if resp.status == 401:
                    raise UpdateFailed("Invalid API Key for BayernCloud Tourismus")
                if resp.status != 200:
                    _LOGGER.warning("API returned status %s.", resp.status)
                    return []

                data = await resp.json()
                raw_items = data.get("items", [])
                return self._filter_and_format_events(raw_items)

        except Exception as err:
            raise UpdateFailed(f"Error fetching event data: {err}") from err

    def _filter_and_format_events(self, raw_items):
        """Filter events according to selected categories and format structure."""
        processed_events = []

        for item in raw_items:
            title = item.get("name", "Unknown Event")
            desc = item.get("description", "")
            start_str = item.get("startDate")
            end_str = item.get("endDate", start_str)
            location_info = item.get("location", {}).get("address", {})
            locality = location_info.get("addressLocality", "")

            matched_cat = False
            title_lower = (title + " " + desc).lower()

            if "wine" in self.categories and ("wein" in title_lower or "wine" in title_lower):
                matched_cat = True
            elif "kirchweih" in self.categories and ("kerwa" in title_lower or "kirchweih" in title_lower or "kirmes" in title_lower or "volksfest" in title_lower):
                matched_cat = True
            elif "concert" in self.categories and ("konzert" in title_lower or "musik" in title_lower or "live" in title_lower):
                matched_cat = True
            elif "market" in self.categories and ("markt" in title_lower or "messen" in title_lower):
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
