import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD
from .const import DOMAIN, CONF_POLICY_PACKAGE, CONF_VERIFY_SSL, CONF_POLLING_INTERVAL
from .api import CheckPointApiClient

class CheckPointConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self.data = {}
        self.api = None
        self.packages = []

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            self.api = CheckPointApiClient(
                user_input[CONF_HOST],
                user_input[CONF_PORT],
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
                user_input.get(CONF_VERIFY_SSL, False)
            )
            if await self.api.login():
                self.data = user_input
                self.packages = await self.api.get_packages()
                return await self.async_step_package()
            else:
                errors["base"] = "auth_error"

        data_schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_PORT, default=443): int,
            vol.Required(CONF_USERNAME): str,
            vol.Required(CONF_PASSWORD): str,
            vol.Optional(CONF_VERIFY_SSL, default=False): bool,
        })
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    async def async_step_package(self, user_input=None):
        if user_input is not None:
            self.data.update(user_input)
            await self.api.logout()
            return self.async_create_entry(title=self.data[CONF_HOST], data=self.data)

        data_schema = vol.Schema({
            vol.Required(CONF_POLICY_PACKAGE): vol.In(self.packages),
            vol.Required(CONF_POLLING_INTERVAL, default=15): int
        })
        return self.async_show_form(step_id="package", data_schema=data_schema)
