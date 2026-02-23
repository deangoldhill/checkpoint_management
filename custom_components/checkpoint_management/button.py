import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.const import CONF_HOST
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][entry.entry_id]["api"]
    package = hass.data[DOMAIN][entry.entry_id]["package"]
    host = entry.data[CONF_HOST]
    
    async_add_entities([
        CheckPointInstallPolicyButton(api, package, host, entry.entry_id),
        CheckPointInstallDatabaseButton(api, coordinator, host, entry.entry_id)
    ])

class CheckPointInstallPolicyButton(ButtonEntity):
    def __init__(self, api, package, host, entry_id):
        self.api = api
        self.package = package
        self.host = host
        self.entry_id = entry_id
        self._attr_name = f"Install Policy ({package})"
        self._attr_unique_id = f"cp_install_policy_{self.entry_id}_{package}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry_id)},
            name=f"Check Point Management ({self.host})",
            manufacturer="Check Point",
            model="Management Server",
            configuration_url=f"https://{self.host}"
        )

    async def async_press(self) -> None:
        await self.api.login()
        await self.api.install_policy(self.package)
        await self.api.logout()

class CheckPointInstallDatabaseButton(ButtonEntity):
    def __init__(self, api, coordinator, host, entry_id):
        self.api = api
        self.coordinator = coordinator
        self.host = host
        self.entry_id = entry_id
        self._attr_name = "Install Database"
        self._attr_unique_id = f"cp_install_database_{self.entry_id}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry_id)},
            name=f"Check Point Management ({self.host})",
            manufacturer="Check Point",
            model="Management Server",
            configuration_url=f"https://{self.host}"
        )

    async def async_press(self) -> None:
        targets = self.coordinator.data.get("gateways", {}).get("mgmt_servers", [])
        
        if not targets:
            _LOGGER.error("No target management servers (CpmiHostCkp) found to install database.")
            return

        await self.api.login()
        await self.api.install_database(targets)
        await self.api.logout()
