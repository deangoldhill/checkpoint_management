from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.const import CONF_HOST
from .const import DOMAIN, API_ENDPOINTS

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    host = entry.data[CONF_HOST]
    
    sensors = [CheckPointSensor(coordinator, key, host, entry.entry_id) for key in API_ENDPOINTS.keys()]
    sensors.append(CheckPointLicenseSensor(coordinator, host, entry.entry_id))
    sensors.append(CheckPointCloudServicesSensor(coordinator, host, entry.entry_id))
    
    gateways_data = coordinator.data.get("gateways", {})
    gateway_types = gateways_data.get("types", {}).keys()
    for gw_type in gateway_types:
        sensors.append(CheckPointGatewayTypeSensor(coordinator, gw_type, host, entry.entry_id))
    
    async_add_entities(sensors)

class CheckPointSensor(SensorEntity):
    def __init__(self, coordinator, key, host, entry_id):
        self.coordinator = coordinator
        self.key = key
        self.host = host
        self.entry_id = entry_id
        
        self._attr_name = self._format_name(key)
        self._attr_unique_id = f"cp_{self.entry_id}_{key}"
        self._attr_state_class = "measurement"

    def _format_name(self, key):
        if key.endswith("_objects"):
            return key.replace('_', ' ').title()
        
        if key.endswith("s") and not key.endswith("ss"):
            return f"{key[:-1].replace('_', ' ').title()} Objects"
            
        return f"{key.replace('_', ' ').title()} Objects"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry_id)},
            name=f"Check Point Management ({self.host})",
            manufacturer="Check Point",
            model="Management Server",
            configuration_url=f"https://{self.host}"
        )

    # CHANGED: Extracts 'total' from the new dictionary format
    @property
    def state(self):
        data = self.coordinator.data.get(self.key)
        if isinstance(data, dict):
            return data.get("total", 0)
        return 0

    # NEW: Pushes the lists of names into Home Assistant attributes
    @property
    def extra_state_attributes(self):
        data = self.coordinator.data.get(self.key)
        if isinstance(data, dict):
            names = data.get("names", [])
            # Only populate the lists for the specific endpoints you requested
            if self.key in ["access_layers", "networks", "hosts", "nat_rules"] and names:
                return {"object_names": names}
        return None

    @property
    def should_poll(self):
        return False

    async def async_update(self):
        await self.coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

class CheckPointGatewayTypeSensor(SensorEntity):
    def __init__(self, coordinator, gw_type, host, entry_id):
        self.coordinator = coordinator
        self.gw_type = gw_type
        self.host = host
        self.entry_id = entry_id
        self._attr_name = f"{gw_type} Objects"
        self._attr_unique_id = f"cp_{self.entry_id}_gw_type_{gw_type.lower()}"
        self._attr_state_class = "measurement"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry_id)},
            name=f"Check Point Management ({self.host})",
            manufacturer="Check Point",
            model="Management Server"
        )

    @property
    def state(self):
        return self.coordinator.data.get("gateways", {}).get("types", {}).get(self.gw_type, 0)

    @property
    def should_poll(self):
        return False

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

class CheckPointLicenseSensor(SensorEntity):
    def __init__(self, coordinator, host, entry_id):
        self.coordinator = coordinator
        self.host = host
        self.entry_id = entry_id
        self._attr_name = "License Status"
        self._attr_unique_id = f"cp_{self.entry_id}_license_status"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry_id)},
            name=f"Check Point Management ({self.host})",
            manufacturer="Check Point",
            model="Management Server"
        )

    @property
    def state(self):
        data = self.coordinator.data.get("license")
        if data:
            return data.get("license-status")
        return None

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data.get("license")
        if data and isinstance(data, dict):
            attributes = data.copy()
            attributes.pop("license-status", None)
            return attributes
        return None

    @property
    def should_poll(self):
        return False

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

class CheckPointCloudServicesSensor(SensorEntity):
    def __init__(self, coordinator, host, entry_id):
        self.coordinator = coordinator
        self.host = host
        self.entry_id = entry_id
        self._attr_name = "Infinity Services Connection"
        self._attr_unique_id = f"cp_{self.entry_id}_cloud_services"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry_id)},
            name=f"Check Point Management ({self.host})",
            manufacturer="Check Point",
            model="Management Server"
        )

    @property
    def state(self):
        data = self.coordinator.data.get("cloud_services")
        if data:
            return data.get("status")
        return None

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data.get("cloud_services")
        if data and "connected-at" in data:
            return {"connected-at": data.get("connected-at")}
        return None

    @property
    def should_poll(self):
        return False

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))
