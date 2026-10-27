"""Serialize local requests and share one status poll across entities."""
import asyncio
from datetime import timedelta
import logging
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .client import BonecoClient, BonecoError
from .const import CONF_DEVICE_ID, CONF_LOCAL_KEY, DOMAIN

_LOGGER = logging.getLogger(__name__)

class BonecoCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        super().__init__(hass, _LOGGER, config_entry=entry, name=DOMAIN,
                         update_interval=timedelta(seconds=30), always_update=False)
        self.device_id = entry.data[CONF_DEVICE_ID]
        self.client = BonecoClient(entry.data['host'], self.device_id, entry.data[CONF_LOCAL_KEY])
        self._lock = asyncio.Lock()

    async def _async_update_data(self):
        async with self._lock:
            try:
                return await self.hass.async_add_executor_job(self.client.read)
            except BonecoError as exc:
                raise UpdateFailed(str(exc)) from exc

    async def async_write(self, values):
        async with self._lock:
            try:
                data = await self.hass.async_add_executor_job(self.client.write, values)
            except ValueError as exc:
                raise ServiceValidationError(str(exc)) from exc
            except BonecoError as exc:
                self.async_set_update_error(exc)
                raise HomeAssistantError(str(exc)) from exc
        self.async_set_updated_data(data)
