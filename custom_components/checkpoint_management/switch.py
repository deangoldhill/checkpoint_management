import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.const import CONF_HOST
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][entry.entry_id]["api"]
    package = hass.data[DOMAIN][entry.entry_id]["package"]
    host = entry.data[CONF_HOST]
    
    rules = coordinator.data.get("rules", [])
    
    if not rules:
        return

    switches = []
    
    for rule in rules:
        switches.append(CheckPointRuleSwitch(coordinator, api, package, rule, host, entry.entry_id))
        
    async_add_entities(switches)

class CheckPointRuleSwitch(SwitchEntity):
    def __init__(self, coordinator, api, package, rule_data, host, entry_id):
        self.coordinator = coordinator
        self.api = api
        self.package = package
        self.host = host
        self.entry_id = entry_id
        self.rule_uid = rule_data.get("uid")
        
        # CHANGED: Capture the specific layer this rule belongs to
        self.rule_layer = rule_data.get("layer_name", "Network")
        
        rule_name = rule_data.get("name")
        if not rule_name:
            rule_name = f"Rule {rule_data.get('rule-number')}"
            
        self._attr_name = f"Rule: {rule_name}"
        self._attr_unique_id = f"cp_rule_{self.rule_uid}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry_id)},
            name=f"Check Point Management ({self.host})",
            manufacturer="Check Point",
            model="Management Server",
            configuration_url=f"https://{self.host}"
        )

    @property
    def entity_registry_enabled_default(self) -> bool:
        return False

    @property
    def is_on(self):
        rules = self.coordinator.data.get("rules", [])
        for rule in rules:
            if rule.get("uid") == self.rule_uid:
                return rule.get("enabled", False)
        return False

    @property
    def extra_state_attributes(self):
        rules = self.coordinator.data.get("rules", [])
        for rule in rules:
            if rule.get("uid") == self.rule_uid:
                # CHANGED: Added the layer name to the attributes UI
                attributes = {
                    "policy_package": self.package,
                    "layer": self.rule_layer
                }
                
                for key, value in rule.items():
                    if key in ["uid", "name", "enabled", "type", "rule-number", "layer_name"]:
                        continue
                        
                    if isinstance(value, list) and all(isinstance(i, dict) and "name" in i for i in value):
                        attributes[key] = ", ".join([i["name"] for i in value])
                    elif isinstance(value, dict) and "name" in value:
                        attributes[key] = value["name"]
                    elif key == "hits" and isinstance(value, dict):
                        attributes["hits_last_hour"] = value.get("value", 0)
                        attributes["hits_percentage"] = value.get("percentage")
                        if "last-date" in value and isinstance(value["last-date"], dict):
                            attributes["last_hit"] = value["last-date"].get("iso-8601")
                        else:
                            attributes["last_hit"] = value.get("last-date")
                    else:
                        attributes[key] = value
                return attributes
        return {}

    @property
    def should_poll(self):
        return False

    async def _toggle_rule(self, state: bool):
        await self.api.login()
        # CHANGED: Pass the specific layer string to the toggle command
        await self.api.set_access_rule_state(self.rule_uid, self.rule_layer, state)
        await self.api.publish()
        await self.api.install_policy(self.package)
        await self.api.logout()
        
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self, **kwargs):
        await self._toggle_rule(True)

    async def async_turn_off(self, **kwargs):
        await self._toggle_rule(False)

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))
