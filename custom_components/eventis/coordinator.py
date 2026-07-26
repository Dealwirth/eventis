"""DataUpdateCoordinator for Eventis."""

from datetime import timedelta
import logging
import aiohttp

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
    """Class to manage fetching event data safely."""

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
        """Fetch events safely or raise UpdateFailed with specific error code."""
        session = async_get_clientsession(self.hass)

        url = "https://raw.githubusercontent.com/Dealwirth/eventis/main/sample_events.json"

        try:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 401:
                    raise UpdateFailed("HTTP 401: Nicht autorisiert (API-Key ungültig oder fehlt)")
                if resp.status == 404:
                    raise UpdateFailed("HTTP 404: Die angeforderte Event-Quelle wurde nicht gefunden")
                if resp.status != 200:
                    raise UpdateFailed(f"HTTP {resp.status}: Server antwortete mit Fehlercode")

                data = await resp.json(content_type=None)
                raw_items = data if isinstance(data, list) else data.get("events", [])
                return self._filter_and_format_events(raw_items)

        except aiohttp.ClientConnectorError as err:
            raise UpdateFailed(f"DNS/Netzwerkfehler: Domain oder Host nicht erreichbar ({err})") from err
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"HTTP-Verbindungsfehler: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unerwarteter Fehler beim Verarbeiten der Daten: {err}") from err

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
