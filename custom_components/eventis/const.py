"""Constants for the Eventis integration."""

DOMAIN = "eventis"

CONF_API_KEY = "api_key"
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
CONF_RADIUS = "radius"
CONF_CATEGORIES = "categories"

DEFAULT_RADIUS = 25  # in kilometers
DEFAULT_SCAN_INTERVAL = 3600  # 1 hour

EVENT_CATEGORIES = {
    "wine": "Wine Festivals & Tastings",
    "kirchweih": "Traditional Folk Festivals & Kirchweih",
    "concert": "Concerts & Live Music",
    "market": "Markets & Culinary Fairs",
    "culture": "Culture, Theater & Exhibitions",
    "family": "Family & Kids",
    "sports": "Sports & Active Events",
}
