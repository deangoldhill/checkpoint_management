import logging
from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][entry.entry_id]["api"]
    package = hass.data[DOMAIN][entry.entry_id]["package"]
    
    rules = coordinator.data.get("rules", [])
    
    # LOUD LOGGING: Prints exactly how many rules HA sees
    _LOGGER.warning(f"Check Point Switch Setup: Found {len(rules)} rules to create switches for.")
    
    if not rules:
        _LOGGER.error("Check Point Switch Setup: No rules were found. The extraction might be failing.")
        return

    switches = []
    
    for rule in rules:
        switches.append(CheckPointRuleSwitch(coordinator, api, package, rule))
        
    async_add_entities(switches)
    _LOGGER.warning(f"Check Point Switch Setup: Successfully passed {len(switches)} switches to Home Assistant.")

class CheckPointRuleSwitch(SwitchEntity):
    def __init__(self, coordinator, api, package, rule_data):
        self.coordinator = coordinator
        self.api = api
        self.package = package
        self.rule_uid = rule_data.get("uid")
        
        rule_name = rule_data.get("name")
        if not rule_name:
            rule_name = f"Rule {rule_data.get('rule-number')}"
            
        self._attr_name = f"Check Point Rule: {rule_name}"
        self._attr_unique_id = f"cp_rule_{self.rule_uid}"

    @property
    def is_on(self):
        rules = self.coordinator.data.get("rules", [])
        for rule in rules:
            if rule.get("uid") == self.rule_uid:
                return rule.get("enabled", False)
        return False

    @property
    def should_poll(self):
        return False

    async def _toggle_rule(self, state: bool):
        _LOGGER.info(f"Toggling rule {self._attr_name} to {state}")
        await self.api.login()
        await self.api.set_access_rule_state(self.rule_uid, self.package, state)
        await self.api.publish()
        _LOGGER.info(f"Installing policy {self.package}...")
        await self.api.install_policy(self.package)
        await self.api.logout()
        
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self, **kwargs):
        await self._toggle_rule(True)

    async def async_turn_off(self, **kwargs):
        await self._toggle_rule(False)

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))
