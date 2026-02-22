from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN, API_ENDPOINTS

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    sensors = [CheckPointSensor(coordinator, key) for key in API_ENDPOINTS.keys()]
    async_add_entities(sensors)

class CheckPointSensor(SensorEntity):
    def __init__(self, coordinator, key):
        self.coordinator = coordinator
        self.key = key
        self._attr_name = f"Check Point {key.replace('_', ' ').title()} Count"
        self._attr_unique_id = f"cp_{coordinator.name}_{key}"
        self._attr_state_class = "measurement"

    @property
    def state(self):
        return self.coordinator.data.get(self.key)

    @property
    def should_poll(self):
        return False

    async def async_update(self):
        await self.coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))
