"""Calendar platform for Local Event Radar."""

from datetime import datetime
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up calendar entity."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([LocalEventsCalendar(coordinator, entry)], True)


class LocalEventsCalendar(CoordinatorEntity, CalendarEntity):
    """Representation of a Local Events Calendar."""

    def __init__(self, coordinator, entry):
        """Initialize the calendar."""
        super().__init__(coordinator)
        self._attr_name = f"Local Events ({entry.data.get('radius')}km)"
        self._attr_unique_id = f"{entry.entry_id}_calendar"

    @property
    def event(self) -> CalendarEvent | None:
        """Return the current or next upcoming event."""
        events = self.coordinator.data
        if not events:
            return None

        next_evt = events[0]
        return CalendarEvent(
            summary=next_evt["summary"],
            start=datetime.fromisoformat(next_evt["start"]),
            end=datetime.fromisoformat(next_evt["end"]),
            description=next_evt.get("description"),
            location=next_evt.get("location"),
        )

    async def async_get_events(self, hass, start_date, end_date):
        """Return events within a specific datetime range."""
        events = self.coordinator.data or []
        results = []

        for evt in events:
            evt_start = datetime.fromisoformat(evt["start"])
            evt_end = datetime.fromisoformat(evt["end"])

            if start_date <= evt_start <= end_date or start_date <= evt_end <= end_date:
                results.append(
                    CalendarEvent(
                        summary=evt["summary"],
                        start=evt_start,
                        end=evt_end,
                        description=evt.get("description"),
                        location=evt.get("location"),
                    )
                )

        return results
