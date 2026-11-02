"""The household's De’Longhi PrimaDonna Aromatic warm-up action."""
import asyncio

import voluptuous as vol
from homeassistant.exceptions import HomeAssistantError

from .client import CheckError, warm_up

DOMAIN = "delonghi_aromatic"


async def async_setup_entry(hass, entry):
    lock = asyncio.Lock()

    async def handle_wake(call):
        if lock.locked():
            raise HomeAssistantError("A warm-up request is already running.")
        async with lock:
            try:
                await hass.async_add_executor_job(
                    warm_up, entry.data
                )
            except CheckError as exc:
                raise HomeAssistantError(str(exc)) from None

    hass.services.async_register(DOMAIN, "warm_up", handle_wake, schema=vol.Schema({}))
    return True


async def async_unload_entry(hass, entry):
    hass.services.async_remove(DOMAIN, "warm_up")
    return True
