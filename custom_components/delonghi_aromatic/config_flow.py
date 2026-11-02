"""Validate ownership without operating the appliance."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig, TextSelectorType

from . import DOMAIN
from .aromatic_cloud.account import CheckError
from .client import authenticate


class AromaticFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        return await self._show_login("user", user_input)

    async def async_step_reconfigure(self, user_input=None):
        return await self._show_login("reconfigure", user_input)

    async def _show_login(self, step, data):
        errors = {}
        if data is not None:
            try:
                await self.hass.async_add_executor_job(authenticate, data)
            except CheckError:
                errors["base"] = "login_failed"
            else:
                await self.async_set_unique_id(data["serial"].strip())
                if step == "reconfigure":
                    self._abort_if_unique_id_mismatch()
                    return self.async_update_reload_and_abort(self._get_reconfigure_entry(), data=data)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="PrimaDonna Aromatic", data=data)
        schema = vol.Schema({
            vol.Required("serial"): str,
            vol.Required("app_client_id"): str,
            vol.Required("email"): TextSelector(TextSelectorConfig(type=TextSelectorType.EMAIL)),
            vol.Required("password"): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD)),
        })
        return self.async_show_form(step_id=step, data_schema=schema, errors=errors)
