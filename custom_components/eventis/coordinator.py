"""DataUpdateCoordinator for Eventis using AllEvents API."""

from datetime import timedelta
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
    """Class to manage fetching event data from AllEvents API."""

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
        """Fetch events safely or raise UpdateFailed with specific error code."""
        session = async_get_clientsession(self.hass)

        # AllEvents API Endpoint (Events in der Nähe nach Lat/Lon)
        url = "https://api.allevents.in/events/list/"

        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Accept": "application/json",
            "User-Agent": "HomeAssistant-Eventis/1.0",
        }

        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "radius": self.radius,
        }

        try:
            async with session.get(url, headers=headers, params=params, timeout=15) as resp:
                if resp.status in (401, 403):
                    raise UpdateFailed("HTTP 401/403: Ungültiger AllEvents API-Schlüssel")
                if resp.status == 404:
                    raise UpdateFailed("HTTP 404: API Endpoint nicht gefunden")
                if resp.status != 200:
                    raise UpdateFailed(f"HTTP {resp.status}: AllEvents Server-Fehler")

                data = await resp.json(content_type=None)
                
                # AllEvents API Antwort-Struktur verarbeiten
                raw_items = data.get("data", []) if isinstance(data, dict) else []
                return self._filter_and_format_events(raw_items)

        except aiohttp.ClientConnectorError as err:
            raise UpdateFailed(f"DNS/Netzwerkfehler beim Aufruf von AllEvents: {err}") from err
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"HTTP-Verbindungsfehler: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Fehler beim Verarbeiten der AllEvents-Daten: {err}") from err

    def _filter_and_format_events(self, raw_items):
        """Filter events according to selected categories and format structure."""
        processed_events = []

        for item in raw_items:
            title = item.get("eventname") or item.get("title", "Veranstaltung")
            desc = item.get("description", "")
            
            # AllEvents verwendet Unix-Timestamps oder ISO Strings
            start_str = item.get("start_time") or item.get("start_date")
            end_str = item.get("end_time") or item.get("end_date") or start_str
            
            venue = item.get("venue", {})
            locality = venue.get("full_address") or venue.get("city") or item.get("location", "")

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
