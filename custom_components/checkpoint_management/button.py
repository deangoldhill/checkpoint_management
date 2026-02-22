from homeassistant.components.button import ButtonEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    api = hass.data[DOMAIN][entry.entry_id]["api"]
    package = hass.data[DOMAIN][entry.entry_id]["package"]
    async_add_entities([CheckPointInstallPolicyButton(api, package, entry.title)])

class CheckPointInstallPolicyButton(ButtonEntity):
    def __init__(self, api, package, title):
        self.api = api
        self.package = package
        self._attr_name = f"Install Policy ({package})"
        self._attr_unique_id = f"cp_install_policy_{title}_{package}"

    async def async_press(self) -> None:
        await self.api.login()
        await self.api.install_policy(self.package)
        await self.api.logout()
