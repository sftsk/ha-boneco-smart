"""Choose humidification, purification, or hybrid operation."""
from homeassistant.components.select import SelectEntity
from .client import FUNCTIONS
from .entity import BonecoEntity

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([BonecoFunction(entry.runtime_data)])

class BonecoFunction(BonecoEntity, SelectEntity):
    _attr_name = 'Function'
    _attr_icon = 'mdi:air-purifier'
    _attr_options = list(FUNCTIONS)

    def __init__(self, coordinator):
        super().__init__(coordinator, 'function')

    @property
    def current_option(self):
        return self.coordinator.data['3']

    async def async_select_option(self, option):
        await self.coordinator.async_write({'3': option})
