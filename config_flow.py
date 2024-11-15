import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
import aiohttp
from .const import DOMAIN, CONF_API_KEY, CONF_METERING_POINT_ID, CONF_UPDATE_INTERVAL, CONF_API_URL, DEFAULT_API_URL, DEFAULT_UPDATE_INTERVAL

class NorgesnettConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            if await self._test_credentials(user_input[CONF_API_KEY], user_input[CONF_METERING_POINT_ID]):
                return self.async_create_entry(title="Norgesnett API", data=user_input)
            else:
                errors["base"] = "invalid_credentials"

        data_schema = vol.Schema({
            vol.Required(CONF_API_KEY): str,
            vol.Required(CONF_METERING_POINT_ID): str,
            vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): int,
            vol.Optional(CONF_API_URL, default=DEFAULT_API_URL): str,
        })

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    async def _test_credentials(self, api_key, metering_point_id):
        """Test if the provided API key and metering point ID are valid."""
        url = DEFAULT_API_URL
        headers = {"X-API-Key": api_key}
        payload = {"meteringPointIds": [metering_point_id]}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                return response.status == 200

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return NorgesnettOptionsFlow(config_entry)


class NorgesnettOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema({
            vol.Optional(CONF_UPDATE_INTERVAL, default=self.config_entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)): int,
            vol.Optional(CONF_API_URL, default=self.config_entry.data.get(CONF_API_URL, DEFAULT_API_URL)): str,
        })
        return self.async_show_form(step_id="init", data_schema=data_schema)
