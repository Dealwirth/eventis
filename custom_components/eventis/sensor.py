"""Sensor platform for Local Event Radar."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up event count sensor."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([LocalEventsSensor(coordinator, entry)], True)


class LocalEventsSensor(CoordinatorEntity, SensorEntity):
    """Sensor displaying total number of upcoming events."""

    def __init__(self, coordinator, entry):
        """Initialize sensor."""
        super().__init__(coordinator)
        self._attr_name = "Upcoming Local Events Count"
        self._attr_unique_id = f"{entry.entry_id}_count_sensor"
        self._attr_icon = "mdi:calendar-star"

    @property
    def native_value(self):
        """Return total upcoming events count."""
        return len(self.coordinator.data) if self.coordinator.data else 0

    @property
    def extra_state_attributes(self):
        """Return preview list of top 5 events."""
        events = self.coordinator.data or []
        return {"next_events": events[:5]}
