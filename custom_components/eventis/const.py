"""Constants for the Eventis integration (AllEvents Edition)."""

DOMAIN = "eventis"

CONF_API_KEY = "api_key"
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
CONF_RADIUS = "radius"
CONF_CATEGORIES = "categories"

DEFAULT_RADIUS = 25  # in Kilometern
DEFAULT_SCAN_INTERVAL = 3600  # 1 Stunde (in Sekunden)

EVENT_CATEGORIES = {
    "wine": "Weinfeste & Weinverkostungen",
    "kirchweih": "Kirchweihen, Kerwa & Volksfeste",
    "concert": "Konzerte & Live-Musik",
    "market": "Märkte & Kulinarik",
    "culture": "Kultur, Theater & Ausstellungen",
    "family": "Familie & Kinder",
    "sports": "Sport & Aktiv-Events",
}
