"""Validate the saved LAN credentials before creating an integration entry."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig, TextSelectorType
from .client import BonecoClient, BonecoError
from .const import CONF_DEVICE_ID, CONF_LOCAL_KEY, DOMAIN

class BonecoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            data = dict(user_input)
            data[CONF_HOST] = data[CONF_HOST].strip()
            data[CONF_DEVICE_ID] = data[CONF_DEVICE_ID].strip()
            await self.async_set_unique_id(data[CONF_DEVICE_ID])
            self._abort_if_unique_id_configured()
            try:
                client = BonecoClient(data[CONF_HOST], data[CONF_DEVICE_ID], data[CONF_LOCAL_KEY])
                await self.hass.async_add_executor_job(client.read)
            except ValueError:
                errors['base'] = 'invalid_input'
            except BonecoError:
                errors['base'] = 'cannot_connect'
            else:
                return self.async_create_entry(title='BONECO H700 SMART', data=data)
        return self.async_show_form(
            step_id='user', errors=errors,
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_DEVICE_ID): str,
                vol.Required(CONF_LOCAL_KEY): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD)),
            }),
        )
