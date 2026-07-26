"""Sensor platform for Eventis."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensor entity."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([EventisSensor(coordinator, entry)], True)


class EventisSensor(CoordinatorEntity, SensorEntity):
    """Representation of an Eventis Event Counter Sensor."""

    def __init__(self, coordinator, entry):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = f"Eventis Anzahlsensor ({entry.data.get('radius')}km)"
        self._attr_unique_id = f"{entry.entry_id}_event_count"
        self._attr_icon = "mdi:calendar-multiselect"
        self._attr_native_unit_of_measurement = "Events"

    @property
    def native_value(self):
        """Return the total number of upcoming events."""
        if not self.coordinator.data:
            return 0
        return len(self.coordinator.data)

    @property
    def extra_state_attributes(self):
        """Return additional attributes for the sensor."""
        events = self.coordinator.data or []
        return {
            "events_list": [evt.get("summary") for evt in events[:5]],
            "last_updated": self.coordinator.last_update_success_time,
        }
