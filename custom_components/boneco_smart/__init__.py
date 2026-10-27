"""BONECO H700 SMART, directly over Wi-Fi."""
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN, PLATFORMS
from .coordinator import BonecoCoordinator

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

async def async_setup_entry(hass, entry):
    coordinator = BonecoCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass, entry):
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
