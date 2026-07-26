class LocalEventsCard extends HTMLElement {
  set hass(hass) {
    if (!this.content) {
      this.innerHTML = `
        <ha-card header="🎉 Local Event Radar">
          <div id="events-container" style="padding: 0 16px 16px 16px;"></div>
        </ha-card>
      `;
      this.content = this.querySelector('#events-container');
    }

    const entityId = this.config.entity || 'calendar.local_events_25km';
    const state = hass.states[entityId];

    if (!state) {
      this.content.innerHTML = `<p style="color: var(--error-color);">Calendar entity not found!</p>`;
      return;
    }

    // Fetch upcoming events from sensor attributes or state
    const sensorState = hass.states['sensor.upcoming_local_events_count'];
    const events = sensorState?.attributes?.next_events || [];

    if (events.length === 0) {
      this.content.innerHTML = `<p>No upcoming events found in your radius.</p>`;
      return;
    }

    this.content.innerHTML = events.map(evt => `
      <div style="margin-bottom: 12px; padding: 10px; background: var(--secondary-background-color); border-radius: 8px;">
        <div style="font-weight: bold; font-size: 1.1em; color: var(--primary-text-color);">${evt.summary}</div>
        <div style="font-size: 0.9em; color: var(--secondary-text-color); margin-top: 4px;">
          📍 ${evt.location || 'Local Region'} | 📅 ${new Date(evt.start).toLocaleDateString()}
        </div>
      </div>
    `).join('');
  }

  setConfig(config) {
    this.config = config;
  }

  static getStubConfig() {
    return { entity: "calendar.local_events_25km" };
  }
}

customElements.define('local-events-card', LocalEventsCard);

// Register Card in HA Card Picker UI
window.customCards = window.customCards || [];
window.customCards.push({
  type: "local-events-card",
  name: "Local Events Timetable",
  description: "A pre-made timeline card displaying upcoming local events and festivals.",
  preview: true
});
